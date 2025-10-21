"""
Pydantic 모델 정의
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class QualityMode(str, Enum):
    """품질 모드 열거형"""
    STABLE_KOREAN = "stable_korean"
    PRESENTATION = "presentation"
    HIGH_QUALITY = "high_quality"
    FAST = "fast"

class PresentationRequest(BaseModel):
    """발표 영상 생성 요청 모델"""
    task_id: str = Field(..., description="작업 ID")
    quality_mode: QualityMode = Field(
        default=QualityMode.STABLE_KOREAN,
        description="품질 모드"
    )
    slide_duration: int = Field(
        default=5,
        ge=3,
        le=30,
        description="슬라이드당 최소 표시 시간 (초)"
    )

class PresentationResponse(BaseModel):
    """발표 영상 생성 응답 모델"""
    task_id: str
    status: str
    message: str
    check_status_url: Optional[str] = None

class StatusResponse(BaseModel):
    """작업 상태 응답 모델"""
    task_id: str
    status: Literal["uploaded", "processing", "completed", "failed"]
    progress: int = Field(ge=0, le=100, description="진행률 (0-100)")
    current_step: str
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result_file: Optional[str] = None
    download_filename: Optional[str] = None

class HealthResponse(BaseModel):
    """시스템 상태 응답 모델"""
    status: Literal["healthy", "unhealthy"]
    timestamp: str
    system: dict
    vibevoice: dict

class UploadResponse(BaseModel):
    """파일 업로드 응답 모델"""
    task_id: str
    status: str
    message: str
    next_step: str

class TaskInfo(BaseModel):
    """작업 정보 모델"""
    task_id: str
    status: str
    created_at: str
    progress: int
    current_step: str

class TaskListResponse(BaseModel):
    """작업 목록 응답 모델"""
    tasks: list[TaskInfo]

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    detail: str
    error_code: Optional[str] = None



