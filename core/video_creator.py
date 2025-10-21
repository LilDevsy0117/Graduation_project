"""
영상 생성 모듈
"""

import os
import subprocess
from typing import List, Optional
import asyncio

class VideoCreator:
    """영상 생성 클래스"""
    
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def create_presentation_video(
        self, 
        slide_images: List[str], 
        audio_files: List[str], 
        task_id: str,
        slide_duration: int = 5,
        scripts: List[str] = None,
        include_subtitles: bool = False
    ) -> Optional[str]:
        """발표 영상 생성"""
        try:
            print("🎬 영상 생성 중...")
            video_segments = []
            
            for i, (slide_image, audio_file) in enumerate(zip(slide_images, audio_files)):
                if not os.path.exists(audio_file):
                    print(f"❌ 오디오 파일이 존재하지 않습니다: {audio_file}")
                    continue
                
                # 오디오 길이 확인
                duration = await self.get_audio_duration(audio_file)
                if duration is None:
                    print(f"❌ 오디오 파일 분석 실패: {audio_file}")
                    continue
                
                # 최소 슬라이드 시간 적용
                if duration < slide_duration:
                    duration = slide_duration
                
                print(f"📊 페이지 {i+1} 오디오 길이: {duration:.2f}초")
                
                # 개별 영상 생성
                segment_path = await self.create_video_segment(
                    slide_image, audio_file, duration, task_id, i + 1
                )
                
                if segment_path:
                    video_segments.append(segment_path)
                    print(f"✅ 세그먼트 {i+1} 생성 완료 (길이: {duration:.2f}초)")
                else:
                    print(f"❌ 세그먼트 {i+1} 생성 실패")
            
            if not video_segments:
                print("❌ 생성된 영상 세그먼트가 없습니다.")
                return None
            
            # 모든 세그먼트 합치기
            final_video = await self.merge_video_segments(video_segments, task_id)
            
            # 자막이 포함된 경우 자막 오버레이 추가
            if include_subtitles and scripts:
                print("📝 자막 오버레이 추가 중...")
                srt_path = self.create_srt_file(scripts, audio_files, task_id)
                final_video_with_subtitles = await self.add_subtitles_to_video(final_video, srt_path, task_id)
                
                if final_video_with_subtitles:
                    # 기존 파일 삭제하고 자막 포함 파일로 교체
                    os.remove(final_video)
                    final_video = final_video_with_subtitles
                    print("✅ 자막 오버레이 완료")
                else:
                    print("❌ 자막 오버레이 실패, 원본 영상 사용")
            
            # 임시 세그먼트 파일들 정리
            await self.cleanup_segments(video_segments)
            
            return final_video
            
        except Exception as e:
            print(f"❌ 영상 생성 실패: {e}")
            return None
    
    async def get_audio_duration(self, audio_file: str) -> Optional[float]:
        """오디오 파일의 길이를 초 단위로 반환"""
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", audio_file
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            return float(result.stdout.strip())
            
        except (ValueError, subprocess.SubprocessError) as e:
            print(f"❌ 오디오 길이 파싱 실패: {e}")
            return None
    
    async def create_video_segment(
        self, 
        slide_image: str, 
        audio_file: str, 
        duration: float, 
        task_id: str, 
        segment_num: int
    ) -> Optional[str]:
        """개별 영상 세그먼트 생성"""
        try:
            segment_path = os.path.join("temp", task_id, f"video{segment_num}.mp4")
            
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", slide_image,  # 이미지를 무한 루프
                "-i", audio_file,                 # 오디오 파일
                "-c:v", "libx264",               # 비디오 코덱
                "-t", str(duration),             # 오디오 길이만큼만 생성
                "-pix_fmt", "yuv420p",           # 픽셀 포맷
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",  # 이미지 크기 조정
                segment_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return segment_path
            else:
                print(f"❌ 세그먼트 생성 실패: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 세그먼트 생성 중 오류: {e}")
            return None
    
    async def merge_video_segments(self, video_segments: List[str], task_id: str) -> Optional[str]:
        """영상 세그먼트들을 하나로 합치기"""
        try:
            print("🔗 영상 합치는 중...")
            
            # concat 파일 생성
            concat_file = os.path.join("temp", task_id, "concat_list.txt")
            with open(concat_file, "w") as f:
                for segment in video_segments:
                    f.write(f"file '{os.path.abspath(segment)}'\n")
            
            # 최종 영상 생성
            final_video = os.path.join(self.output_dir, f"{task_id}_presentation.mp4")
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file, 
                "-c", "copy",  # copy 모드로 빠른 합치기
                final_video
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🎉 발표 영상 생성 완료: {final_video}")
                return final_video
            else:
                print(f"❌ 영상 합치기 실패: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 영상 합치기 중 오류: {e}")
            return None
    
    async def cleanup_segments(self, video_segments: List[str]):
        """임시 세그먼트 파일들 정리"""
        try:
            for segment in video_segments:
                if os.path.exists(segment):
                    os.remove(segment)
                    print(f"🗑️ 세그먼트 파일 삭제: {os.path.basename(segment)}")
        except Exception as e:
            print(f"⚠️ 세그먼트 파일 정리 실패: {e}")
    
    def get_video_info(self, video_path: str) -> dict:
        """영상 파일 정보 조회"""
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                return {"error": "영상 정보 조회 실패"}
                
        except Exception as e:
            return {"error": str(e)}

    def create_srt_file(self, scripts: List[str], audio_files: List[str], task_id: str) -> str:
        """SRT 자막 파일 생성"""
        srt_path = os.path.join(self.output_dir, f"{task_id}_subtitles.srt")
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            subtitle_index = 1
            current_time = 0.0
            
            for i, (script, audio_file) in enumerate(zip(scripts, audio_files)):
                # 오디오 길이 확인
                duration = self.get_audio_duration_sync(audio_file)
                if duration is None:
                    duration = 5.0  # 기본값
                
                # 시작 시간과 종료 시간 계산
                start_time = self.format_srt_time(current_time)
                end_time = self.format_srt_time(current_time + duration)
                
                # SRT 형식으로 자막 작성
                f.write(f"{subtitle_index}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{script}\n\n")
                
                subtitle_index += 1
                current_time += duration
        
        return srt_path
    
    def get_audio_duration_sync(self, audio_file: str) -> Optional[float]:
        """오디오 파일 길이를 동기적으로 가져오기"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"❌ 오디오 길이 확인 실패: {e}")
            return None
    
    def format_srt_time(self, seconds: float) -> str:
        """초를 SRT 시간 형식으로 변환 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    async def add_subtitles_to_video(self, video_path: str, srt_path: str, task_id: str) -> Optional[str]:
        """영상에 자막 오버레이 추가"""
        try:
            output_path = os.path.join(self.output_dir, f"{task_id}_with_subtitles.mp4")
            
            # FFmpeg 명령어로 자막 오버레이
            cmd = [
                'ffmpeg', '-y',  # 덮어쓰기 허용
                '-i', video_path,  # 입력 영상
                '-vf', f"subtitles={srt_path}:force_style='FontSize=18,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2'",  # 자막 필터
                '-c:a', 'copy',  # 오디오는 복사
                '-c:v', 'libx264',  # 비디오 코덱
                '-preset', 'fast',  # 인코딩 속도
                output_path
            ]
            
            print(f"🎬 자막 오버레이 명령어: {' '.join(cmd)}")
            
            # 비동기로 FFmpeg 실행
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print("✅ 자막 오버레이 성공")
                return output_path
            else:
                print(f"❌ 자막 오버레이 실패: {stderr.decode()}")
                return None
                
        except Exception as e:
            print(f"❌ 자막 오버레이 중 오류: {e}")
            return None

