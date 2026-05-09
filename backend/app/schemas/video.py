from typing import Optional
from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    
    status: bool
    message: str
    data: dict


class VideoMetadata(BaseModel):
  
    video_id: int
    title: str
    subject_name: Optional[str]
    file_path: str
    uploaded_by: Optional[str]
