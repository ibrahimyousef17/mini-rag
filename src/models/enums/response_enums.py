from enum import Enum

class ResponseSignal(Enum): 
    file_validate_success = "File validate Successfully "
    file_extention_error = "File type not supported" 
    file_size_error = "file size muste be maximum 10 MB"
    file_uploaded_success = 'File Uploaded Successfully'
    file_uploaded_failed = 'File Uploaded Failed'
    processing_failed = 'Processing Failed'
    processing_successfully = 'processing successfully'
    file_is_actually_existing = 'file_is_actually_existing'
    no_files_found_in_this_project = 'no files found in this project'
    file_not_found = 'file not found'
    file_already_processed_before = 'file already processed before'
    chunks_deleted_failed = 'chunks deleted failed'
