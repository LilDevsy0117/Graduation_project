# 졸업 프로젝트 - AI 기반 발표 영상 생성 시스템

이 프로젝트는 PDF 문서를 입력으로 받아 AI 기반 발표 스크립트를 생성하고, Zonos 음성 합성 모델을 사용하여 음성을 생성한 후, 최종적으로 발표 영상을 자동으로 생성하는 시스템입니다.

## 주요 기능

- **PDF 문서 처리**: PDF 파일에서 텍스트와 이미지를 추출
- **AI 스크립트 생성**: GPT-4o를 사용하여 발표용 스크립트 자동 생성
- **음성 합성**: Zonos 모델을 사용한 고품질 음성 생성 (보이스 클로닝 지원)
- **영상 생성**: ffmpeg를 사용하여 슬라이드와 음성을 결합한 발표 영상 생성

## 시스템 요구사항

- Python 3.8+
- CUDA 지원 GPU (권장)
- ffmpeg
- 필요한 Python 패키지들 (requirements.txt 참조)

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/LilDevsy0117/Graduation_project.git
cd Graduation_project
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. Zonos 모델 설정:
- Zonos 디렉토리가 프로젝트 루트에 있어야 합니다
- 필요한 모델 파일들을 Zonos 디렉토리에 배치하세요

4. 환경 변수 설정:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

## 사용 방법

```bash
python3 project.py
```

프로그램이 실행되면:
1. PDF 파일을 자동으로 감지
2. 각 페이지에서 텍스트와 이미지 추출
3. GPT-4o로 발표 스크립트 생성
4. Zonos 모델로 음성 생성
5. ffmpeg로 최종 발표 영상 생성

## 파일 구조

```
Graduation_project/
├── project.py          # 메인 실행 파일
├── Zonos/              # Zonos 음성 합성 모델
├── requirements.txt    # Python 의존성
├── README.md          # 프로젝트 설명서
└── .gitignore         # Git 무시 파일 목록
```

## 주요 기술 스택

- **음성 합성**: Zonos (Zyphra/Zonos-v0.1-transformer)
- **AI 모델**: OpenAI GPT-4o
- **PDF 처리**: PyMuPDF (fitz)
- **영상 처리**: ffmpeg
- **오디오 처리**: torchaudio, soundfile

## 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

## 개발자

LilDevsy0117
