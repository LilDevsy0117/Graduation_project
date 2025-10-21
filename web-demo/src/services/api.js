import axios from 'axios';

// API URL 고정 설정 - 환경변수 무시하고 강제로 9200 포트 사용
let API_BASE_URL = 'http://localhost:9200';
console.log('🔧 API_BASE_URL 설정:', API_BASE_URL);
console.log('🔧 process.env.REACT_APP_API_URL:', process.env.REACT_APP_API_URL);

// API 연결 테스트 함수
const testApiConnection = async (url) => {
    try {
        const response = await axios.get(`${url}/health`, { timeout: 5000 });
        return response.status === 200;
    } catch (error) {
        return false;
    }
};

// 사용 가능한 API URL 찾기
const findWorkingApiUrl = async () => {
    // 9200 포트로 고정
    const url = 'http://localhost:9200';
    console.log(`🔍 테스트 중: ${url}`);

    if (await testApiConnection(url)) {
        console.log(`✅ 연결 성공: ${url}`);
        return url;
    }

    console.log('❌ API 연결 실패');
    return url; // 기본값 반환
};

// API URL은 위에서 이미 설정됨

// 연결 테스트 후 URL 업데이트
findWorkingApiUrl().then(workingUrl => {
    if (workingUrl !== API_BASE_URL) {
        API_BASE_URL = workingUrl;
        console.log(`🔄 API URL 업데이트: ${API_BASE_URL}`);
    }
});

console.log('🔧 apiClient 생성 시 API_BASE_URL:', API_BASE_URL);
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5분으로 증가
    headers: {
        'Content-Type': 'application/json',
    },
    maxContentLength: 100 * 1024 * 1024, // 100MB
    maxBodyLength: 100 * 1024 * 1024, // 100MB
});

// 요청 인터셉터
apiClient.interceptors.request.use(
    (config) => {
        console.log(`🚀 API 요청: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('❌ API 요청 오류:', error);
        return Promise.reject(error);
    }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
    (response) => {
        console.log(`✅ API 응답: ${response.status} ${response.config.url}`);
        return response;
    },
    (error) => {
        console.error('❌ API 응답 오류:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// API 서비스
const apiService = {
    // 시스템 상태 확인
    checkHealth: async () => {
        const response = await apiClient.get('/health');
        return response.data;
    },

    // 파일 업로드 및 발표영상 생성 시작
    uploadAndCreatePresentation: async (pdfFile, audioFile, language = 'korean', includeSubtitles = false) => {
        const formData = new FormData();
        formData.append('pdf_file', pdfFile);
        formData.append('speaker_audio', audioFile);
        formData.append('quality_mode', 'stable_korean');
        formData.append('slide_duration', '5');
        formData.append('language', language);
        formData.append('include_subtitles', includeSubtitles.toString());

        const response = await apiClient.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            timeout: 300000, // 5분으로 증가
            maxContentLength: 100 * 1024 * 1024, // 100MB
            maxBodyLength: 100 * 1024 * 1024, // 100MB
        });

        return response.data;
    },

    // 작업 상태 확인
    getTaskStatus: async (taskId) => {
        try {
            const response = await apiClient.get(`/status/${taskId}`);
            console.log(`📡 API 응답 받음:`, response.data);
            return response.data;
        } catch (error) {
            console.log(`❌ API 요청 실패:`, error.response?.status, error.response?.data);
            if (error.response?.status === 404) {
                // 작업이 아직 등록되지 않았을 때 기본값 반환
                return {
                    status: 'processing',
                    progress: 0,
                    current_step: '작업 초기화 중...',
                    error_message: null
                };
            }
            throw error;
        }
    },

    // 작업 목록 조회
    getTasks: async () => {
        const response = await apiClient.get('/tasks');
        return response.data;
    },

    // 작업 삭제
    deleteTask: async (taskId) => {
        const response = await apiClient.delete(`/tasks/${taskId}`);
        return response.data;
    },

    // 파일 다운로드 URL 생성
    getDownloadUrl: (taskId) => {
        return `${API_BASE_URL}/download/${taskId}`;
    },

    // 파일 다운로드 실행
    downloadFile: async (taskId, filename) => {
        const url = `${API_BASE_URL}/download/${taskId}`;

        try {
            const response = await apiClient.get(url, {
                responseType: 'blob',
                timeout: 300000,
            });

            const blob = new Blob([response.data], { type: 'video/mp4' });
            const downloadUrl = window.URL.createObjectURL(blob);

            // 파일명 설정 (파라미터로 받은 파일명 우선 사용)
            let downloadFilename = filename || `presentation_${taskId}.mp4`;
            console.log('📁 사용할 파일명:', downloadFilename);

            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = downloadFilename;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            window.URL.revokeObjectURL(downloadUrl);
        } catch (error) {
            console.error('❌ 파일 다운로드 실패:', error);
            throw error;
        }
    },
};

export default apiService;
