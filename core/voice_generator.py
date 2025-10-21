"""
음성 생성 모듈
"""

import os
import sys
import subprocess
import tempfile
import torch
import soundfile as sf
import librosa
from typing import Optional

# VibeVoice 모듈 경로 추가
sys.path.append('/home/devsy/workspace/VibeVoice')

class VoiceGenerator:
    """음성 생성 클래스"""
    
    def __init__(self):
        self.vibevoice_dir = "/home/devsy/workspace/VibeVoice"
        self.voices_dir = os.path.join(self.vibevoice_dir, "demo", "voices")
        os.makedirs(self.voices_dir, exist_ok=True)
    
    def check_vibevoice_status(self) -> dict:
        """VibeVoice 상태 확인"""
        try:
            # VibeVoice 디렉토리 존재 확인
            if not os.path.exists(self.vibevoice_dir):
                return {"status": "error", "message": "VibeVoice 디렉토리를 찾을 수 없습니다."}
            
            # 데모 스크립트 존재 확인
            demo_script = os.path.join(self.vibevoice_dir, "demo", "inference_from_file.py")
            if not os.path.exists(demo_script):
                return {"status": "error", "message": "VibeVoice 데모 스크립트를 찾을 수 없습니다."}
            
            # GPU 사용 가능 여부
            gpu_available = torch.cuda.is_available()
            
            return {
                "status": "ready",
                "message": "VibeVoice 준비 완료",
                "gpu_available": gpu_available,
                "device": "cuda" if gpu_available else "cpu"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"VibeVoice 상태 확인 실패: {str(e)}"}
    
    def get_quality_parameters(self, quality_mode: str = "presentation") -> dict:
        """품질 모드에 따른 VibeVoice 파라미터 설정"""
        
        # 기본 설정들
        base_params = {
            "model_path": "vibevoice/VibeVoice-1.5B",  # 안정성을 위해 1.5B 사용
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "cfg_scale": 1.3  # CFG 스케일 (기본값)
        }
        
        if quality_mode == "presentation":
            # 발표용 최적화 설정
            return {
                **base_params,
                "cfg_scale": 1.5,  # 높은 CFG로 더 명확한 음성
            }
        
        elif quality_mode == "high_quality":
            # 최고 품질 설정 (느리지만 고품질)
            return {
                **base_params,
                "model_path": "vibevoice/VibeVoice-7B",  # 더 큰 모델 사용
                "cfg_scale": 1.8,  # 매우 높은 CFG로 최고 품질
            }
        
        elif quality_mode == "fast":
            # 빠른 생성 설정
            return {
                **base_params,
                "cfg_scale": 1.1,  # 낮은 CFG로 빠른 생성
            }
        
        elif quality_mode == "stable_korean":
            # 한국어 안정성 최적화 설정 (메모리 문제 해결을 위해 1.5B 사용)
            return {
                **base_params,
                "model_path": "vibevoice/VibeVoice-1.5B",  # 메모리 문제 해결
                "cfg_scale": 1.6,  # 높은 CFG로 안정성 확보
            }
        
        else:
            # 기본 설정
            return {
                **base_params,
                "cfg_scale": 1.3,
            }
    
    async def generate_voice(
        self, 
        text: str, 
        speaker_audio_path: str, 
        task_id: str, 
        slide_num: int, 
        quality_mode: str = "presentation"
    ) -> Optional[str]:
        """텍스트를 음성으로 변환하는 VibeVoice 함수"""
        try:
            if not speaker_audio_path or not os.path.exists(speaker_audio_path):
                print("❌ 스피커 오디오 파일이 필요합니다.")
                return None
            
            print(f"음성 생성 중: '{text[:50]}...'")
            
            # 한국어 텍스트 전처리 (발표 스타일 최적화)
            processed_text = self.preprocess_korean_text_for_presentation(text)
            print(f"📝 전처리된 텍스트: '{processed_text[:50]}...'")
            
            # 품질 모드에 따른 파라미터 설정
            quality_params = self.get_quality_parameters(quality_mode)
            print(f"🎛️ 품질 설정: {quality_mode} 모드")
            
            # 임시 파일들 생성
            temp_text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
            formatted_text = f"Speaker 1: {processed_text}"
            temp_text_file.write(formatted_text)
            temp_text_file.close()
            
            # voices 디렉토리에 음성 파일 복사
            speaker_voice_file = os.path.join(self.voices_dir, "Speaker_1.wav")
            
            # 음성 파일 전처리 (24kHz로 변환)
            try:
                audio, sr = librosa.load(speaker_audio_path, sr=24000)
                sf.write(speaker_voice_file, audio, 24000)
                print(f"✅ 음성 파일 전처리 완료")
            except Exception as e:
                print(f"❌ 음성 파일 전처리 실패: {e}")
                return None
            
            # 출력 디렉토리 설정
            output_dir = os.path.abspath(os.path.join("temp", task_id, "audio"))
            os.makedirs(output_dir, exist_ok=True)
            print(f"📁 VibeVoice 출력 디렉토리: {output_dir}")
            
            # VibeVoice 명령어 구성
            cmd = [
                "python", "demo/inference_from_file.py",
                "--model_path", quality_params["model_path"],
                "--txt_path", temp_text_file.name,
                "--speaker_names", "Speaker 1",
                "--output_dir", output_dir,
                "--device", quality_params["device"],
                "--cfg_scale", str(quality_params["cfg_scale"])
            ]
            
            print(f"🚀 VibeVoice 실행 중... (시간이 오래 걸릴 수 있습니다)")
            print(f"📋 실행 명령어: {' '.join(cmd)}")
            
            # 타임아웃 설정 (10분)
            result = subprocess.run(cmd, cwd=self.vibevoice_dir, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # VibeVoice가 생성하는 파일명 예측
                txt_filename = os.path.splitext(os.path.basename(temp_text_file.name))[0]
                expected_filename = f"{txt_filename}_generated.wav"
                expected_path = os.path.join(output_dir, expected_filename)
                
                # 예상 파일이 존재하는지 확인
                if os.path.exists(expected_path):
                    source_path = expected_path
                    print(f"✅ VibeVoice 생성 파일 발견: {expected_filename}")
                else:
                    # 예상 파일이 없으면 디렉토리에서 _generated.wav 파일 찾기
                    output_files = [f for f in os.listdir(output_dir) if f.endswith('_generated.wav')]
                    if output_files:
                        # 가장 최근 파일 선택
                        latest_file = max(output_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
                        source_path = os.path.join(output_dir, latest_file)
                        print(f"✅ 대체 파일 사용: {latest_file}")
                    else:
                        print("❌ 생성된 오디오 파일을 찾을 수 없습니다.")
                        return None
                
                # 최종 출력 파일 경로
                final_output_path = os.path.join(output_dir, f"slide_{slide_num}_audio.wav")
                
                # 파일 복사
                import shutil
                shutil.copy2(source_path, final_output_path)
                print(f"✅ 음성 생성 완료: {final_output_path}")
                
                # 원본 임시 파일 삭제
                try:
                    if source_path != final_output_path and os.path.exists(source_path):
                        os.remove(source_path)
                        print(f"🗑️ 임시 파일 삭제: {os.path.basename(source_path)}")
                except Exception as e:
                    print(f"⚠️ 임시 파일 삭제 실패: {e}")
                
                # 오디오 길이 확인
                try:
                    audio, sr = librosa.load(final_output_path, sr=24000)
                    print(f"음성 길이: {len(audio)/24000:.2f}초")
                except:
                    pass
                
                return final_output_path
            else:
                print(f"❌ VibeVoice 실행 실패:")
                print(f"   Return code: {result.returncode}")
                print(f"   Error output: {result.stderr}")
                print(f"   Standard output: {result.stdout}")
                return None
            
        except subprocess.TimeoutExpired:
            print(f"⏰ VibeVoice 실행 시간 초과 (10분)")
            print("💡 해결 방법:")
            print("   1. 더 작은 모델 사용 (fast 모드)")
            print("   2. 텍스트를 더 짧게 나누기")
            print("   3. GPU 메모리 확인")
            return None
        except Exception as e:
            print(f"❌ 음성 생성 실패: {e}")
            return None
        finally:
            # 임시 파일 정리
            try:
                if 'temp_text_file' in locals():
                    os.unlink(temp_text_file.name)
                    print(f"🗑️ 임시 파일 정리: {temp_text_file.name}")
            except Exception as cleanup_error:
                print(f"⚠️ 임시 파일 정리 실패: {cleanup_error}")
                pass
    
    def preprocess_korean_text_for_presentation(self, text: str) -> str:
        """한국어 텍스트를 발표에 적합하게 전처리"""
        import re
        
        # 1. 한국어 구두점을 영어 구두점으로 변환 (VibeVoice 권장사항)
        text = text.replace('"', '"').replace('"', '"')  # 한국어 따옴표 → 영어 따옴표
        text = text.replace(''', "'").replace(''', "'")  # 한국어 작은따옴표 → 영어 작은따옴표
        text = text.replace('…', '...')  # 줄임표 통일
        
        # 2. 발표에 적합한 구두점 정리
        text = re.sub(r'[!]{2,}', '!', text)  # 연속된 느낌표 정리
        text = re.sub(r'[?]{2,}', '?', text)  # 연속된 물음표 정리
        text = re.sub(r'[.]{3,}', '...', text)  # 연속된 마침표 정리
        
        # 3. 발표 속도 조절을 위한 쉼표 추가 (자연스러운 휴지)
        sentences = text.split('.')
        processed_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 30자 이상인 문장에 적절한 쉼표 추가
            if len(sentence) > 30:
                # "그리고", "또한", "하지만" 등의 연결어 앞에 쉼표 추가
                sentence = re.sub(r'(\w+)(\s+)(그리고|또한|하지만|그러나|따라서|그런데)', r'\1,\2\3', sentence)
                # "이것은", "저것은" 등의 주어 뒤에 쉼표 추가 (긴 문장에서)
                sentence = re.sub(r'(\w+는|\w+은)(\s+)(\w+을|\w+를|\w+가|\w+이)', r'\1,\2\3', sentence)
            
            processed_sentences.append(sentence)
        
        # 4. 문장 재조립
        result = '. '.join(processed_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
        
        return result



