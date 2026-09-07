
from controllers.base_controller import BaseController

from fastapi import UploadFile
from models.enums import ResponseSignal

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.file_max_size_byte = 10 * 1024 *1024 

    def validate_uploaded_file(self,file:UploadFile):
        if file.size > self.file_max_size_byte :  # type: ignore
            return False,ResponseSignal().file_size_error.value # type: ignore
        if file.content_type not in self.app_settings.file_allowd_extention:
            return False,ResponseSignal.file_extention_error.value 
        return True , ResponseSignal.file_validate_success.value 