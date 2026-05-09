from typing import Optional
from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    """
    POST /upload-video ka success response schema.
    Frontend ise expect karega.
    """
    status: bool
    message: str
    data: dict


class VideoMetadata(BaseModel):
    """
    Database mein store ki gayi video ki details.
    """
    video_id: int
    title: str
    subject_name: Optional[str]
    file_path: str
    uploaded_by: Optional[str]
