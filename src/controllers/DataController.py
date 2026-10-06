from .BaseController import BaseController
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
    
    def validate_upload_file(self, file):
        ALLOWED_EXTENSIONS = self.app_settings.FILE_ALLOWED_EXTENSIONS
        if file.content_type not in ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        file_size_mb = len(file.file.read()) / (1024 * 1024) 
        if file_size_mb > self.app_settings.FILE_MAX_SIZE_MB:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        file.file.seek(0)
        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def generate_unique_filename(self, original_filename: str, project_id: str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_filename = self.get_clean_filename(original_filename=original_filename)
        new_filename = os.path.join(project_path, f"{random_key}_{cleaned_filename}")
        while os.path.exists(new_filename):
            random_key = self.generate_random_string()
            new_filename = os.path.join(project_path, f"{random_key}_{cleaned_filename}")
        return new_filename
        

    def get_clean_filename(self, original_filename: str):
        cleaned_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_filename)
        cleaned_filename = cleaned_filename.replace(' ', '_')
        return cleaned_filename