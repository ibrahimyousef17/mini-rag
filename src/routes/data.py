from fastapi import APIRouter , Depends , UploadFile ,status
from fastapi.responses import JSONResponse
from helpers import Settings,get_settings
from controllers import DataController
from controllers import ProjectController
import aiofiles 
import logging 
from models import ResponseSignal
from routes.schemas.data_schema import ProcessRequest

from controllers import ProcessController


logger = logging.getLogger('uvicorn-error')

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['/api/v1/data']
)

@data_router.post('/upload/{project_id}')
async def upload_data(project_id : str, file:UploadFile ,
                    
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
        project_id=project_id , orig_filename= file.filename
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

    return JSONResponse(
        content={
        'signal' : ResponseSignal.file_uploaded_success.value,
        'file_name' : file_id,
    })

@data_router.post('/process/{project_id}')
async def process_data(project_id : str , process_request : ProcessRequest):
    file_chunks = ProcessController(project_id=project_id).process_file_content(
                                                      file_name=process_request.file_id,
                                                      chunk_size=process_request.chunk_size,
                                                      chunk_overlap=process_request.overlap
                                                      )

    if file_chunks is None or len(file_chunks) ==0 :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.processing_failed.value
            }
        )
    return file_chunks