from enum import Enum

class ResponseSignal(Enum): 
    file_validate_success = "File validate Successfully "
    file_extention_error = "File type not supported" 
    file_size_error = "file size muste be maximum 10 MB"
    file_uploaded_success = 'File Uploaded Successfully'
    file_uploaded_failed = 'File Uploaded Failed'
    processing_failed = 'Processing Failed'
