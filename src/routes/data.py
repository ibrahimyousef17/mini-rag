from fastapi import APIRouter , Depends , UploadFile ,status,Request
from fastapi.responses import JSONResponse
from helpers import Settings,get_settings
from controllers import DataController
from controllers import ProjectController
import aiofiles 
import logging 
from models.enums import ResponseSignal
from routes.schemas.data_schema import ProcessRequest
from db_services import ProjectService
from db_services import ChunkService
from models.db_schemas import ChunkSchema
from controllers import ProcessController


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
    
    #create a unique file name 
    file_path,file_id = ProjectController().generate_unique_filename(
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


    return JSONResponse(
        content={
        'signal' : ResponseSignal.file_uploaded_success.value,
        'file_name' : file_id,
    })

@data_router.post('/process/{project_id}')
async def process_data(request:Request,project_id : str , process_request : ProcessRequest):

    chunk_service = ChunkService(db_client=request.app.db_client)
    #check on do_reset 
    if process_request.do_reset==1:
        chunks_del_no = await chunk_service.delete_chunks_by_project_id(project_id=project_id)
        return f"{chunks_del_no} was deleted in project {project_id}"


    
    file_chunks = ProcessController(project_id=project_id).process_file_content(
                                                      file_name=process_request.file_id,
                                                      chunk_size=process_request.chunk_size, # type: ignore
                                                      chunk_overlap=process_request.overlap # type: ignore
                                                      )

    if file_chunks is None or len(file_chunks) ==0 :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.processing_failed.value
            }
        )

    #save chunks in db

    chunks_records = [
        ChunkSchema(chunk_id=str(i),chunk_text=chunk.page_content,chunk_meta_data=chunk.metadata,project_id=project_id)  # type: ignore
        for i,chunk in enumerate(file_chunks)
    ]
    
    chunks_no = await chunk_service.insert_many_chunks(chunks_records)
    
    return file_chunks


