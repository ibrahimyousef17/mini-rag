from controllers.base_controller import BaseController 
import os
import re
class ProjectController(BaseController): 
    def __init__(self):
        super().__init__()

    def get_project_path(self,project_id :str):

        project_dir = os.path.join(
            self.file_dir ,
            project_id
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir 
    
    def get_clean_filename(self,orig_filename:str):
        cleaned_filename = re.sub(r'^\W.' , ' ' ,orig_filename.strip())
        cleaned_filename = cleaned_filename.replace(' ','_' )
        return cleaned_filename 

    def generate_unique_filename(self,orig_filename:str,project_id:str):
        random_key= self.generate_random_string()
        cleaned_filname = self.get_clean_filename(orig_filename=orig_filename)
        project_path = self.get_project_path(project_id=project_id) 

        new_file_path = os.path.join(
            project_path,
            random_key + '_' + cleaned_filname
        )  

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
            project_path,
            random_key + '_' + cleaned_filname
        )  
        
        return new_file_path , random_key + '_' + cleaned_filname
