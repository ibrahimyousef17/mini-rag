from controllers.base_controller import BaseController
from controllers.project_controller import ProjectController 
from langchain_community.document_loaders import TextLoader , PyMuPDFLoader
import os
from models.enums import ProcessEnums
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController): 

    def __init__(self,project_id:str):
        super().__init__()
        self.project_id = project_id 
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extention(self,file_name:str):
        return os.path.splitext(file_name)[-1]

    def get_file_loader(self,file_name:str):

        file_extention = self.get_file_extention(file_name)
        file_path = os.path.join(
            self.project_path,
            file_name
        )
        if not os.path.exists(file_path):
            return None 
        if file_extention == ProcessEnums.TXT.value:
            return TextLoader(file_path=file_path,encoding='utf-8')
        if file_extention == ProcessEnums.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        raise ValueError(f"Unsupported file extension: {file_extention}")

    def get_file_content(self,file_name:str):
        loader = self.get_file_loader(file_name=file_name)
        if loader:
            return loader.load() 
        return None 

    def process_file_content(self,file_name:str,chunk_size:int,chunk_overlap:int):
        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
        file_contents = self.get_file_content(file_name=file_name)
        if file_contents is None :
            return None
        file_content_text = [ doc.page_content
            for doc in file_contents
        ]
        file_content_meta_data = [ doc.metadata
                                  for doc in file_contents
        ]

        chunks = text_splitter.create_documents(file_content_text,metadatas=file_content_meta_data)
        return chunks
    