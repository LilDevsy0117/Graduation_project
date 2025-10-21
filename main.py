#!/usr/bin/env python3
"""
PDF 발표 영상 자동 생성기 - FastAPI 버전
PDF → 스크립트 → 음성 → 영상 자동 생성
VibeVoice 기반 보이스 클로닝 지원
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
import uuid
import asyncio
from datetime import datetime
import json

# 프로젝트 모듈 import
from core.pdf_processor import PDFProcessor
from core.voice_generator import VoiceGenerator
from core.video_creator import VideoCreator
from core.script_generator import ScriptGenerator
from models.schemas import (
    PresentationRequest, 
    PresentationResponse, 
    StatusResponse,
    QualityMode
)

# FastAPI 앱 초기화
app = FastAPI(
    title="PDF 발표 영상 자동 생성기",
    description="PDF를 자동으로 발표 영상으로 변환하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="."), name="static")

# 전역 변수
processing_tasks = {}  # 진행 중인 작업들 추적
output_dir = "outputs"
temp_dir = "temp"

# 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)

# 컴포넌트 초기화
pdf_processor = PDFProcessor()
voice_generator = VoiceGenerator()
video_creator = VideoCreator()
script_generator = ScriptGenerator()

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "PDF 발표 영상 자동 생성기 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload (파일 업로드 + 자동 발표영상 생성)",
            "status": "/status/{task_id}",
            "download": "/download/{task_id}",
            "list_tasks": "/tasks"
        }
    }

@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    try:
        # 시스템 리소스 확인
        system_info = await check_system_resources()
        
        # VibeVoice 상태 확인
        vibevoice_status = voice_generator.check_vibevoice_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": system_info,
            "vibevoice": vibevoice_status
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/upload")
async def upload_and_create_presentation(
    pdf_file: UploadFile = File(..., description="PDF 파일"),
    speaker_audio: UploadFile = File(..., description="스피커 음성 파일 (WAV/MP3)"),
    language: str = Form("korean"),
    include_subtitles: str = Form("false"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """파일 업로드 및 발표영상 자동 생성 엔드포인트"""
    try:
        # 파일 유효성 검사
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
        
        if not speaker_audio.filename.endswith(('.wav', '.mp3')):
            raise HTTPException(status_code=400, detail="음성 파일은 WAV 또는 MP3 형식만 지원됩니다.")
        
        # 품질 모드와 슬라이드 지속시간은 기본값으로 고정
        quality_mode = "stable_korean"
        slide_duration = 5
        
        # 언어 유효성 검사
        if language not in ["korean", "english"]:
            raise HTTPException(status_code=400, detail="지원되는 언어: korean, english")
        
        # 자막 옵션 처리
        include_subtitles_bool = include_subtitles.lower() == "true"
        
        # 고유 ID 생성
        task_id = str(uuid.uuid4())
        task_dir = os.path.join(temp_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 파일 저장
        pdf_path = os.path.join(task_dir, "input.pdf")
        audio_path = os.path.join(task_dir, "speaker_audio.wav")
        
        with open(pdf_path, "wb") as f:
            content = await pdf_file.read()
            f.write(content)
        
        with open(audio_path, "wb") as f:
            content = await speaker_audio.read()
            f.write(content)
        
        # PDF 파일명에서 확장자 제거하여 기본 파일명 생성
        pdf_filename = os.path.splitext(pdf_file.filename)[0]
        
        # 작업 상태 초기화
        processing_tasks[task_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "pdf_path": pdf_path,
            "audio_path": audio_path,
            "pdf_filename": pdf_filename,
            "progress": 0,
            "current_step": "파일 업로드 완료, 발표영상 생성 시작",
            "quality_mode": quality_mode,
            "slide_duration": slide_duration,
            "language": language,
            "include_subtitles": include_subtitles_bool
        }
        
        # 백그라운드 작업이 실제로 시작될 때까지 잠시 대기
        await asyncio.sleep(0.1)
        
        # 백그라운드에서 발표영상 생성 시작
        background_tasks.add_task(
            process_presentation_task,
            task_id,
            quality_mode,
            slide_duration,
            language,
            include_subtitles_bool
        )
        
        # 백그라운드 작업이 실제로 시작될 때까지 추가 대기
        await asyncio.sleep(0.5)
        
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "파일이 업로드되었고 발표영상 생성이 시작되었습니다.",
            "quality_mode": quality_mode,
            "slide_duration": slide_duration,
            "check_status_url": f"/status/{task_id}",
            "download_url": f"/download/{task_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 및 처리 실패: {str(e)}")

# /create-presentation 엔드포인트는 /upload로 통합되어 제거됨

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """작업 상태 확인"""
    if task_id not in processing_tasks:
        print(f"❌ 작업을 찾을 수 없음: {task_id}")
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    task = processing_tasks[task_id]
    print(f"📤 상태 응답 전송: {task_id} - 진행률: {task['progress']}% - 단계: {task['current_step']}")
    
    return StatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        current_step=task["current_step"],
        created_at=task["created_at"],
        completed_at=task.get("completed_at"),
        error_message=task.get("error_message"),
        result_file=task.get("result_file"),
        download_filename=task.get("download_filename")
    )

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """결과 파일 다운로드"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    task = processing_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="작업이 아직 완료되지 않았습니다.")
    
    result_file = task.get("result_file")
    if not result_file or not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="결과 파일을 찾을 수 없습니다.")
    
    # 다운로드 파일명 사용 (PDF 파일명 기반)
    download_filename = task.get("download_filename", os.path.basename(result_file))
    print(f"📁 다운로드 파일명: {download_filename}")
    
    from fastapi.responses import Response
    import mimetypes
    
    # 파일 읽기
    with open(result_file, "rb") as f:
        content = f.read()
    
    # Content-Disposition 헤더 설정
    headers = {
        "Content-Disposition": f'attachment; filename="{download_filename}"'
    }
    print(f"📁 Content-Disposition 헤더: {headers['Content-Disposition']}")
    
    return Response(
        content=content,
        media_type="video/mp4",
        headers=headers
    )

@app.get("/tasks")
async def list_tasks():
    """모든 작업 목록 조회"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "created_at": task["created_at"],
                "progress": task["progress"],
                "current_step": task["current_step"]
            }
            for task_id, task in processing_tasks.items()
        ]
    }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """작업 삭제"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    # 파일 정리
    task = processing_tasks[task_id]
    task_dir = os.path.dirname(task["pdf_path"])
    
    try:
        import shutil
        if os.path.exists(task_dir):
            shutil.rmtree(task_dir)
        
        # 결과 파일도 삭제
        if task.get("result_file") and os.path.exists(task["result_file"]):
            os.remove(task["result_file"])
        
        # 작업 정보 삭제
        del processing_tasks[task_id]
        
        return {"message": "작업이 성공적으로 삭제되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 삭제 실패: {str(e)}")

async def process_presentation_task(task_id: str, quality_mode: str, slide_duration: int, language: str, include_subtitles: bool):
    """백그라운드에서 발표 영상 생성 처리"""
    try:
        task = processing_tasks[task_id]
        pdf_path = task["pdf_path"]
        audio_path = task["audio_path"]
        
        # 1. PDF 처리
        task["current_step"] = "PDF 페이지 추출 중..."
        task["progress"] = 5
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        slide_images = await pdf_processor.extract_pages_from_pdf(pdf_path, task_id)
        
        if not slide_images:
            raise Exception("PDF 페이지 추출 실패")
        
        task["current_step"] = f"PDF 처리 완료 - {len(slide_images)}개 슬라이드 추출"
        task["progress"] = 10
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        # 2. 스크립트 생성
        task["current_step"] = "발표 스크립트 생성 시작..."
        task["progress"] = 15
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        scripts = []
        previous_script = ""
        
        for i, slide_image in enumerate(slide_images):
            lang_text = "영어" if language == "english" else "한국어"
            task["current_step"] = f"{lang_text} 발표 스크립트 생성 중... ({i + 1}/{len(slide_images)})"
            script = await script_generator.generate_script_for_slide(
                i + 1, slide_image, i == 0, i == len(slide_images) - 1, previous_script, language
            )
            scripts.append(script)
            previous_script = script
            
            # 진행률 업데이트 (15% → 30%)
            progress = 15 + (i + 1) * 15 // len(slide_images)
            task["progress"] = progress
            print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
            await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        lang_text = "영어" if language == "english" else "한국어"
        task["current_step"] = f"{lang_text} 스크립트 생성 완료 - {len(scripts)}개 스크립트 생성"
        task["progress"] = 30
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        # 3. 음성 생성
        task["current_step"] = "음성 생성 시작..."
        task["progress"] = 35
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        audio_files = []
        
        for i, script in enumerate(scripts):
            lang_text = "영어" if language == "english" else "한국어"
            task["current_step"] = f"{lang_text} 음성 생성 중... ({i + 1}/{len(scripts)})"
            audio_path = await voice_generator.generate_voice(
                script, task["audio_path"], task_id, i + 1, quality_mode
            )
            if audio_path:
                audio_files.append(audio_path)
            
            # 진행률 업데이트 (35% → 60%)
            progress = 35 + (i + 1) * 25 // len(scripts)
            task["progress"] = progress
            print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
            await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        lang_text = "영어" if language == "english" else "한국어"
        task["current_step"] = f"{lang_text} 음성 생성 완료 - {len(audio_files)}개 음성 파일 생성"
        task["progress"] = 60
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        # 4. 영상 생성
        task["current_step"] = "영상 생성 시작..."
        task["progress"] = 65
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        result_file = await video_creator.create_presentation_video(
            slide_images, audio_files, task_id, slide_duration, scripts, include_subtitles
        )
        
        if not result_file:
            raise Exception("영상 생성 실패")
        
        task["current_step"] = "영상 생성 완료"
        task["progress"] = 80
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        await asyncio.sleep(0)  # 다른 코루틴이 실행될 수 있도록 양보
        
        # 5. 완료 - PDF 파일명 기반으로 결과 파일명 생성
        pdf_filename = task["pdf_filename"]
        lang_suffix = "_english" if language == "english" else "_korean"
        final_filename = f"{pdf_filename}{lang_suffix}.mp4"
        print(f"📁 PDF 파일명: {pdf_filename}")
        print(f"📁 최종 파일명: {final_filename}")
        
        # 결과 파일을 최종 파일명으로 복사
        final_result_path = os.path.join(os.path.dirname(result_file), final_filename)
        import shutil
        shutil.copy2(result_file, final_result_path)
        print(f"📁 최종 파일 경로: {final_result_path}")
        
        task["status"] = "completed"
        task["progress"] = 100
        task["current_step"] = "완료"
        task["completed_at"] = datetime.now().isoformat()
        task["result_file"] = final_result_path
        task["download_filename"] = final_filename
        print(f"🔄 [{task_id}] 진행률 업데이트: {task['progress']}% - {task['current_step']}")
        
        # 임시 파일 정리
        await cleanup_temp_files(task_id)
        
    except Exception as e:
        task["status"] = "failed"
        task["error_message"] = str(e)
        task["current_step"] = f"오류: {str(e)}"
        print(f"작업 {task_id} 실패: {e}")

async def cleanup_temp_files(task_id: str):
    """임시 파일 정리"""
    try:
        task = processing_tasks[task_id]
        task_dir = os.path.dirname(task["pdf_path"])
        
        if os.path.exists(task_dir):
            import shutil
            shutil.rmtree(task_dir)
            
    except Exception as e:
        print(f"임시 파일 정리 실패: {e}")

async def check_system_resources():
    """시스템 리소스 확인"""
    try:
        import psutil
        import torch
        
        memory = psutil.virtual_memory()
        system_info = {
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available // (1024**3),
            "gpu_available": torch.cuda.is_available()
        }
        
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            gpu_allocated = torch.cuda.memory_allocated(0)
            gpu_free = gpu_memory - gpu_allocated
            system_info.update({
                "gpu_memory_total_gb": gpu_memory // (1024**3),
                "gpu_memory_free_gb": gpu_free // (1024**3)
            })
        
        return system_info
        
    except ImportError:
        return {"error": "psutil이 설치되지 않음"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9200, reload=False)
