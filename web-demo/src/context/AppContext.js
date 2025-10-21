import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import apiService from '../services/api';

const AppContext = createContext();

export const useAppContext = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within AppProvider');
    }
    return context;
};

export const AppProvider = ({ children }) => {
    // 업로드 상태
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);

    // 진행 상태
    const [progress, setProgress] = useState({
        taskId: null,
        status: 'idle', // idle, uploading, processing, completed, failed
        progress: 0,
        currentStep: '',
        errorMessage: null,
        downloadUrl: null,
        downloadFilename: null,
    });

    const intervalRef = useRef(null);
    const isPollingRef = useRef(false);

    // 진행 상황 업데이트
    const updateProgress = useCallback((updates) => {
        setProgress(prev => ({ ...prev, ...updates }));
    }, []);

    // 폴링 중지
    const stopPolling = useCallback(() => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        isPollingRef.current = false;
    }, []);

    // 작업 상태 확인
    const checkTaskStatus = useCallback(async (taskId) => {
        try {
            const status = await apiService.getTaskStatus(taskId);

            console.log(`📊 프론트엔드 진행률 업데이트: ${status.progress}% - ${status.current_step}`);
            updateProgress({
                progress: status.progress,
                currentStep: status.current_step,
                errorMessage: status.error_message || null,
            });

            if (status.status === 'completed') {
                stopPolling();
                updateProgress({
                    status: 'completed',
                    downloadUrl: apiService.getDownloadUrl(taskId),
                    downloadFilename: status.download_filename,
                });
            } else if (status.status === 'failed') {
                stopPolling();
                updateProgress({
                    status: 'failed',
                    errorMessage: status.error_message || '작업 처리 중 오류가 발생했습니다.',
                });
            } else {
                updateProgress({
                    status: 'processing',
                });
            }
        } catch (error) {
            console.error('❌ 작업 상태 확인 실패:', error);
            stopPolling();
            updateProgress({
                status: 'failed',
                errorMessage: '작업 상태를 확인할 수 없습니다.',
            });
        }
    }, [updateProgress, stopPolling]);

    // 폴링 시작
    const startPolling = useCallback((taskId) => {
        if (isPollingRef.current) {
            return;
        }

        isPollingRef.current = true;
        updateProgress({
            taskId,
            status: 'processing',
            progress: 0,
            currentStep: '작업 상태 확인 중...',
            errorMessage: null,
        });

        checkTaskStatus(taskId);

        intervalRef.current = setInterval(() => {
            checkTaskStatus(taskId);
        }, 2000);
    }, [updateProgress, checkTaskStatus]);

    // 파일 업로드
    const handleUpload = useCallback(async (pdfFile, audioFile, language = 'korean', includeSubtitles = false) => {
        try {
            setIsUploading(true);
            setUploadError(null);

            // 파일 유효성 검사
            if (!pdfFile.type.includes('pdf')) {
                throw new Error('PDF 파일만 업로드 가능합니다.');
            }

            if (!audioFile.type.includes('audio')) {
                throw new Error('음성 파일만 업로드 가능합니다.');
            }

            const maxSize = 100 * 1024 * 1024;
            if (pdfFile.size > maxSize) {
                throw new Error('PDF 파일 크기는 100MB를 초과할 수 없습니다.');
            }
            if (audioFile.size > maxSize) {
                throw new Error('음성 파일 크기는 100MB를 초과할 수 없습니다.');
            }

            const response = await apiService.uploadAndCreatePresentation(
                pdfFile,
                audioFile,
                language,
                includeSubtitles
            );

            // 백엔드에서 작업 등록이 완료될 때까지 잠시 대기
            setTimeout(() => {
                startPolling(response.task_id);
            }, 2000);
        } catch (error) {
            console.error('업로드 실패:', error);
            setUploadError(error.message || '업로드 중 오류가 발생했습니다.');
        } finally {
            setIsUploading(false);
        }
    }, [startPolling]);

    // 다운로드
    const handleDownload = useCallback(async () => {
        if (!progress.taskId) return;

        try {
            await apiService.downloadFile(progress.taskId, progress.downloadFilename);
        } catch (error) {
            console.error('다운로드 실패:', error);
            setUploadError('다운로드 중 오류가 발생했습니다.');
        }
    }, [progress.taskId, progress.downloadFilename]);

    // 초기화
    const handleReset = useCallback(() => {
        stopPolling();
        setProgress({
            taskId: null,
            status: 'idle',
            progress: 0,
            currentStep: '',
            errorMessage: null,
            downloadUrl: null,
        });
        setUploadError(null);
    }, [stopPolling]);

    // 컴포넌트 언마운트 시 정리
    useEffect(() => {
        return () => {
            stopPolling();
        };
    }, [stopPolling]);

    const value = {
        isUploading,
        uploadError,
        progress,
        handleUpload,
        handleDownload,
        handleReset,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

