# API 문서

PDF 발표 영상 자동 생성기의 REST API 문서입니다.

## 📚 API 개요

### 기본 정보
- **Base URL**: `http://localhost:9200`
- **Content-Type**: `application/json` (일반), `multipart/form-data` (파일 업로드)
- **인증**: 없음 (현재 버전)

### 응답 형식
모든 API 응답은 JSON 형식으로 반환됩니다.

## 🔗 엔드포인트 목록

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| GET | `/` | API 정보 |
| GET | `/health` | 시스템 상태 확인 |
| POST | `/upload` | 파일 업로드 + 발표영상 자동 생성 |
| GET | `/status/{task_id}` | 작업 상태 확인 |
| GET | `/download/{task_id}` | 결과 파일 다운로드 |
| GET | `/tasks` | 작업 목록 조회 |
| DELETE | `/tasks/{task_id}` | 작업 삭제 |

## 📋 상세 API 문서

### 1. API 정보 조회

**GET** `/`

API 기본 정보를 반환합니다.

**응답 예시:**
```json
{
  "message": "PDF 발표 영상 자동 생성기 API",
  "version": "1.0.0",
  "endpoints": {
    "upload": "/upload",
    "status": "/status/{task_id}",
    "download": "/download/{task_id}",
    "health": "/health"
  }
}
```

### 2. 시스템 상태 확인

**GET** `/health`

시스템의 전반적인 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  },
  "vibevoice": {
    "status": "ready",
    "model_loaded": true
  }
}
```

### 3. 파일 업로드 및 발표영상 생성

**POST** `/upload`

PDF 파일과 음성 샘플을 업로드하고 발표 영상 생성을 시작합니다.

**Content-Type:** `multipart/form-data`

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `pdf_file` | File | ✅ | PDF 파일 |
| `speaker_audio` | File | ✅ | 음성 샘플 파일 (WAV/MP3) |
| `language` | String | ❌ | 발표 언어 (`korean` 또는 `english`, 기본값: `korean`) |
| `include_subtitles` | String | ❌ | 자막 포함 여부 (`true` 또는 `false`, 기본값: `false`) |

**요청 예시:**
```bash
curl -X POST "http://localhost:9200/upload" \
  -F "pdf_file=@presentation.pdf" \
  -F "speaker_audio=@my_voice.wav" \
  -F "language=korean" \
  -F "include_subtitles=true"
```

**응답 예시:**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "message": "파일이 업로드되었고 발표영상 생성이 시작되었습니다.",
  "language": "korean",
  "include_subtitles": true,
  "check_status_url": "/status/123e4567-e89b-12d3-a456-426614174000",
  "download_url": "/download/123e4567-e89b-12d3-a456-426614174000"
}
```

**오류 응답:**
```json
{
  "detail": "PDF 파일만 업로드 가능합니다."
}
```

### 4. 작업 상태 확인

**GET** `/status/{task_id}`

특정 작업의 현재 상태와 진행률을 확인합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `task_id` | String | ✅ | 작업 ID (UUID) |

**응답 예시:**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": 65,
  "current_step": "한국어 음성 생성 중... (2/3)",
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": null,
  "error_message": null,
  "result_file": null,
  "download_filename": "presentation_korean.mp4"
}
```

**상태 값:**
- `processing`: 처리 중
- `completed`: 완료
- `failed`: 실패

**진행률 단계:**
- 0-10%: PDF 처리
- 15-30%: 스크립트 생성
- 35-60%: 음성 생성
- 65-80%: 영상 생성
- 100%: 완료

### 5. 결과 파일 다운로드

**GET** `/download/{task_id}`

완성된 발표 영상을 다운로드합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `task_id` | String | ✅ | 작업 ID (UUID) |

**응답:**
- **Content-Type**: `video/mp4`
- **Content-Disposition**: `attachment; filename="파일명.mp4"`

**요청 예시:**
```bash
curl -O http://localhost:9200/download/123e4567-e89b-12d3-a456-426614174000
```

### 6. 작업 목록 조회

**GET** `/tasks`

모든 작업의 목록을 조회합니다.

**응답 예시:**
```json
{
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00Z",
      "completed_at": "2024-01-01T12:05:00Z"
    },
    {
      "task_id": "987fcdeb-51a2-43d1-9c8e-123456789abc",
      "status": "processing",
      "created_at": "2024-01-01T12:10:00Z",
      "completed_at": null
    }
  ],
  "total": 2
}
```

### 7. 작업 삭제

**DELETE** `/tasks/{task_id}`

특정 작업과 관련된 모든 파일을 삭제합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `task_id` | String | ✅ | 작업 ID (UUID) |

**응답 예시:**
```json
{
  "message": "작업이 성공적으로 삭제되었습니다."
}
```

## 🔄 워크플로우 예시

### 1. 발표 영상 생성 전체 과정

```bash
# 1. 파일 업로드 및 작업 시작
curl -X POST "http://localhost:9200/upload" \
  -F "pdf_file=@marketing_strategy.pdf" \
  -F "speaker_audio=@my_voice.wav" \
  -F "language=english" \
  -F "include_subtitles=true"

# 응답: {"task_id": "abc123...", "status": "processing", ...}

# 2. 작업 상태 확인 (반복)
curl http://localhost:9200/status/abc123...

# 3. 완료 후 다운로드
curl -O http://localhost:9200/download/abc123...
```

### 2. JavaScript/React에서 사용

```javascript
// 파일 업로드
const formData = new FormData();
formData.append('pdf_file', pdfFile);
formData.append('speaker_audio', audioFile);
formData.append('language', 'korean');
formData.append('include_subtitles', 'true');

const response = await fetch('/upload', {
  method: 'POST',
  body: formData
});

const { task_id } = await response.json();

// 상태 확인 (폴링)
const checkStatus = async () => {
  const statusResponse = await fetch(`/status/${task_id}`);
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    // 다운로드
    window.location.href = `/download/${task_id}`;
  } else if (status.status === 'failed') {
    console.error('작업 실패:', status.error_message);
  } else {
    // 2초 후 다시 확인
    setTimeout(checkStatus, 2000);
  }
};

checkStatus();
```

## 🚨 오류 코드

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파일 형식 오류 등) |
| 404 | 리소스를 찾을 수 없음 (작업 ID 없음) |
| 500 | 서버 내부 오류 |

### 오류 응답 형식

```json
{
  "detail": "오류 메시지"
}
```

### 일반적인 오류

1. **파일 형식 오류**
   ```json
   {
     "detail": "PDF 파일만 업로드 가능합니다."
   }
   ```

2. **작업을 찾을 수 없음**
   ```json
   {
     "detail": "작업을 찾을 수 없습니다."
   }
   ```

3. **작업이 아직 완료되지 않음**
   ```json
   {
     "detail": "작업이 아직 완료되지 않았습니다."
   }
   ```

## 📊 성능 및 제한사항

### 파일 제한
- **PDF 파일**: 최대 100MB
- **음성 파일**: 최대 100MB
- **지원 형식**: PDF, WAV, MP3

### 처리 시간
- **슬라이드당**: 약 1-2분
- **전체 처리**: 슬라이드 수에 따라 선형 증가

### 동시 처리
- 현재 버전에서는 순차 처리
- 향후 버전에서 병렬 처리 지원 예정

## 🔧 개발자 도구

### Swagger UI
API 문서는 Swagger UI를 통해 자동 생성됩니다:
- URL: `http://localhost:9200/docs`
- 대화형 API 테스트 가능

### Postman Collection
Postman을 사용한 API 테스트를 위한 컬렉션을 제공합니다.
