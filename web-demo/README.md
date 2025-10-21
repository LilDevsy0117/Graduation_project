# PDF 발표 영상 생성기 - 웹 데모 (JavaScript)

React JavaScript로 구현된 PDF 발표 영상 생성기의 웹 인터페이스입니다.

## 🚀 기술 스택

- **Frontend**: React 18 (JavaScript)
- **Styling**: Styled Components
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Icons**: React Icons
- **Backend API**: FastAPI

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
npm install
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:
```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. 개발 서버 실행
```bash
npm start
```

브라우저에서 `http://localhost:3000`으로 접속하세요.

### 4. 프로덕션 빌드
```bash
npm run build
```

## 🎯 주요 기능

### 1. **파일 업로드**
- 드래그 앤 드롭 지원
- PDF와 음성 파일 업로드
- 파일 유효성 검사

### 2. **품질 모드 선택**
- 안정적 한국어 (권장)
- 발표용
- 최고 품질
- 빠른 생성

### 3. **실시간 진행 추적**
- 작업 진행률 표시
- 단계별 상태 확인
- 오류 메시지 표시

### 4. **시스템 상태 모니터링**
- 서버 상태 확인
- 메모리 사용률
- GPU 상태
- VibeVoice 상태

## 🏗️ 프로젝트 구조

```
src/
├── components/          # React 컴포넌트
│   ├── FileUpload.js   # 파일 업로드 UI
│   ├── ProgressTracker.js  # 진행 상황 추적
│   └── SystemStatus.js # 시스템 상태
├── context/            # Context API
│   └── AppContext.js   # 전역 상태 관리
├── services/           # API 서비스
│   └── api.js          # Axios API 클라이언트
├── App.js              # 메인 앱 컴포넌트
└── index.js            # 엔트리 포인트
```

## 🎨 Styled Components 사용

모든 스타일은 Styled Components로 작성되어 있습니다:

```javascript
import styled from 'styled-components';

const Button = styled.button`
  background: #2563eb;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
`;
```

## 🔄 Context API 상태 관리

전역 상태는 React Context API로 관리됩니다:

```javascript
import { useAppContext } from './context/AppContext';

const MyComponent = () => {
  const { progress, handleUpload } = useAppContext();
  // ...
};
```

## 📡 API 통신

Axios를 사용한 API 통신:

```javascript
import apiService from './services/api';

// 파일 업로드
const response = await apiService.uploadAndCreatePresentation(
  pdfFile,
  audioFile,
  qualityMode,
  slideDuration
);
```

## 🚨 주의사항

1. **백엔드 서버**: FastAPI 서버가 실행 중이어야 합니다
2. **파일 크기**: 각 파일당 최대 100MB
3. **지원 형식**: PDF, WAV, MP3만 지원
4. **브라우저**: 최신 브라우저 사용 권장

## 🐛 문제 해결

### API 연결 오류
- 백엔드 서버가 실행 중인지 확인
- `.env` 파일의 `REACT_APP_API_URL` 확인
- CORS 설정 확인

### 파일 업로드 실패
- 파일 형식 확인 (PDF, WAV, MP3)
- 파일 크기 확인 (100MB 이하)
- 네트워크 연결 확인

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.