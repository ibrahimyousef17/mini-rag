from fastapi import APIRouter , Depends , UploadFile ,status,Request
from fastapi.responses import JSONResponse
from helpers import Settings,get_settings
from controllers import DataController
from controllers import ProjectController
import aiofiles 
import logging 
from models.enums import ResponseSignal,AssetTypeEnum,AssetStatusEnum
from routes.schemas.data_schema import ProcessRequest
from db_services import ProjectService
from db_services import ChunkService,AssetService
from models.db_schemas import ChunkSchema,AssetSchema
from controllers import ProcessController
from bson import ObjectId
import hashlib 

logger = logging.getLogger('uvicorn-error')

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['/api/v1/data']
)

@data_router.post('/upload/{project_id}')
async def upload_data(request:Request,project_id : str, file:UploadFile ,
                    
                       app_settings : Settings = Depends(get_settings)):

    
    #validate on file , is file for my request (size / extention) or not 
    isvalid,signal = DataController().validate_uploaded_file(file=file)

    if not isvalid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                'signal' : signal
            }
        )
    # check file is actually exist in db by hash 

    sha256_hash = hashlib.sha256() 

    while chunk:= await file.read(app_settings.file_defult_chunk_size):
        sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()
    await file.seek(0)

    asset_service = await AssetService.create_instance(db_client=request.app.db_client)

    result = await asset_service.search_asset_by_hash(asset_hash=file_hash)

    if result:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.file_is_actually_existing.value,
                'file_name':result.asset_name,
                'file_id':result.id
            }
        )

    
    #create a unique file name 
    file_path,file_name = ProjectController().generate_unique_filename(
        project_id=project_id , orig_filename= file.filename # type: ignore
    )

    #spliting uploading file to chunks 
    
    try:
        async with aiofiles.open(file_path,'wb') as f:
            while chunk := await file.read(app_settings.file_defult_chunk_size):
                await f.write(chunk)
    except Exception as e :
        logger.error(f"error while uploading file {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.file_uploaded_failed.value
            }
        )

    #save project in db 
    project_service = ProjectService(db_client=request.app.db_client) # type: ignore

    project = await project_service.get_project_or_create_one(project_id=project_id)

    #save file in db 
    asset = AssetSchema(
        asset_project_id=project.id, # type: ignore
        asset_name=file_name,
        asset_hash=file_hash,
        asset_size=file.size, # type: ignore
        asset_status=AssetStatusEnum.asset_pending.value,
        asset_type= AssetTypeEnum.file.value
    )
    _= await asset_service.create_asset(asset)

    return JSONResponse(
        content={
        'signal' : ResponseSignal.file_uploaded_success.value,
        'file_name' : file_name,
    })

@data_router.post('/process/{project_id}')
async def process_data(request:Request,project_id : str , process_request : ProcessRequest):

    chunk_service = await ChunkService.create_instance(db_client=request.app.db_client)
    asset_service = await AssetService.create_instance(db_client=request.app.db_client)
    project_service = await ProjectService.create_instance(db_client=request.app.db_client) 
    project = await project_service.get_project_or_create_one(project_id=project_id)
    #check on do_reset 
    if process_request.do_reset==1:
        chunks_del_no = await chunk_service.delete_chunks_by_project_id(project_id=project.id) # type: ignore
        if chunks_del_no == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'signal':ResponseSignal.chunks_deleted_failed.value
                }
            )
        #reset project asset to pending status after delete chunks
        _= await asset_service.reset_project_asset_status(
            project_id=project.id, # type: ignore
            asset_status=AssetStatusEnum.asset_pending.value
        )
        return f"{chunks_del_no} was deleted in project {project_id}"

    #check user enter special file to pprocess or user want to all files in project 
    project_files_names = []
    if process_request.file_name:
        specific_file = await asset_service.get_specific_asset(project_id=str(project.id),asset_name=process_request.file_name) # type: ignore
        if not specific_file:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'signal':ResponseSignal.file_not_found.value
                }
            )
        elif specific_file.asset_status != AssetStatusEnum.asset_pending.value:
            return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                'signal':ResponseSignal.file_already_processed_before.value
                            }
                        )
        project_files_names = [process_request.file_name]

    else:
        project_files = await asset_service.get_all_asset_by_type_and_project_id(
            project_id=str(project.id),
            asset_type=AssetTypeEnum.file.value
        )

        if len(project_files)==0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'signal':ResponseSignal.no_files_found_in_this_project.value
                }
            )
        
        project_files_names = [file.asset_name for file in project_files if file.asset_status==AssetStatusEnum.asset_pending]

    no_success_files = 0 
    no_failed_files = 0 
    failed_files_names = []
    no_chunks= 0 


    #process to project_files
    for i,file_name in enumerate(project_files_names):
            
        file_chunks = ProcessController(project_id=project_id).process_file_content(
                                                            file_name=file_name,
                                                            chunk_size=process_request.chunk_size, # type: ignore
                                                            chunk_overlap=process_request.overlap # type: ignore
                                                            )

        if file_chunks is None or len(file_chunks) ==0 :
                no_failed_files += 1
                failed_files_names.append(file_name)
                continue

        #save chunks in db
        #get file by name and project_id because we need to pass to chunk

        file = await asset_service.get_specific_asset(project_id=str(project.id),asset_name=file_name)
        if file is None:
            no_failed_files +=1 
            failed_files_names.append(file_name)
            continue
        
        chunks_records = [
                ChunkSchema(chunk_id=str(i),asset_id=file.id,chunk_text=chunk.page_content,chunk_meta_data=chunk.metadata,project_id=project.id)   # type: ignore
                for i,chunk in enumerate(file_chunks)
            ]

        #update asset_status from pending to completed

        _= await asset_service.update_asset_status(asset_name=file_name,asset_status=AssetStatusEnum.asset_completed.value)

        no_success_files += 1

        no_chunks += await chunk_service.insert_many_chunks(chunks_records)

        


    
    return JSONResponse(
        content={
            'signal':ResponseSignal.processing_successfully.value,
            'no_success_files':no_success_files,
            'no_failed_files':no_failed_files,
            'failed_files_names':failed_files_names,

        }
    )


