import React from 'react';
import styled from 'styled-components';
import { FiCheckCircle, FiAlertCircle, FiClock, FiDownload, FiRefreshCw } from 'react-icons/fi';
import { useAppContext } from '../context/AppContext';

const ProgressTracker = () => {
    const { progress, handleDownload, handleReset } = useAppContext();

    const getStatusIcon = () => {
        switch (progress.status) {
            case 'completed':
                return <FiCheckCircle size={32} color="#10b981" />;
            case 'failed':
                return <FiAlertCircle size={32} color="#ef4444" />;
            case 'processing':
                return <SpinningIcon><FiRefreshCw size={32} color="#3b82f6" /></SpinningIcon>;
            default:
                return <FiClock size={32} color="#9ca3af" />;
        }
    };

    const getStatusText = () => {
        switch (progress.status) {
            case 'completed': return '완료';
            case 'failed': return '실패';
            case 'processing': return '처리 중';
            case 'uploading': return '업로드 중';
            default: return '대기 중';
        }
    };

    const getProgressSteps = () => {
        const currentProgress = progress.progress || 0;
        console.log('🔍 현재 진행률:', currentProgress, '현재 단계:', progress.currentStep);

        return [
            {
                name: '파일 업로드',
                progress: progress.status === 'uploading' || currentProgress > 0 ? 100 : 0,
                isActive: progress.status === 'uploading'
            },
            {
                name: 'PDF 처리',
                progress: currentProgress >= 10 ? 100 : currentProgress > 0 ? (currentProgress / 10) * 100 : 0,
                isActive: currentProgress > 0 && currentProgress < 15
            },
            {
                name: '스크립트 생성',
                progress: currentProgress >= 30 ? 100 : currentProgress > 15 ? ((currentProgress - 15) / 15) * 100 : 0,
                isActive: currentProgress >= 15 && currentProgress < 35,
                detail: progress.currentStep?.includes('스크립트') ? progress.currentStep : null
            },
            {
                name: '음성 생성',
                progress: currentProgress >= 60 ? 100 : currentProgress > 35 ? ((currentProgress - 35) / 25) * 100 : 0,
                isActive: currentProgress >= 35 && currentProgress < 65,
                detail: progress.currentStep?.includes('음성') ? progress.currentStep : null
            },
            {
                name: '영상 생성',
                progress: currentProgress >= 80 ? 100 : currentProgress > 65 ? ((currentProgress - 65) / 15) * 100 : 0,
                isActive: currentProgress >= 65 && currentProgress < 100
            },
            {
                name: '완료',
                progress: currentProgress >= 100 ? 100 : 0,
                isActive: currentProgress >= 100
            },
        ];
    };

    if (progress.status === 'idle') {
        return null;
    }

    return (
        <Container>
            <Header>
                <IconContainer>
                    {getStatusIcon()}
                </IconContainer>
                <div>
                    <Title>발표 영상 생성</Title>
                    <StatusBadge $status={progress.status}>{getStatusText()}</StatusBadge>
                </div>
            </Header>

            {/* 전체 진행률 */}
            <ProgressSection>
                <ProgressHeader>
                    <ProgressLabel>전체 진행률</ProgressLabel>
                    <ProgressValue>{progress.progress}%</ProgressValue>
                </ProgressHeader>
                <ProgressBarContainer>
                    <ProgressBarFill $progress={progress.progress} />
                </ProgressBarContainer>
            </ProgressSection>

            {/* 현재 단계 */}
            {progress.currentStep && (
                <CurrentStep>
                    <p>{progress.currentStep}</p>
                </CurrentStep>
            )}

            {/* 오류 메시지 */}
            {progress.errorMessage && (
                <ErrorMessage>
                    <FiAlertCircle size={20} />
                    <span>{progress.errorMessage}</span>
                </ErrorMessage>
            )}

            {/* 단계별 진행률 */}
            <StepsSection>
                <StepsTitle>처리 단계</StepsTitle>
                {getProgressSteps().map((step, index) => (
                    <StepItem key={index}>
                        <StepIcon $isComplete={step.progress === 100} $isActive={step.progress > 0}>
                            {step.progress === 100 ? (
                                <FiCheckCircle size={20} />
                            ) : (
                                <span>{index + 1}</span>
                            )}
                        </StepIcon>
                        <StepContent>
                            <StepHeader>
                                <StepName>{step.name}</StepName>
                                <StepProgress>{Math.round(step.progress)}%</StepProgress>
                            </StepHeader>
                            {step.detail && (
                                <StepDetail>{step.detail}</StepDetail>
                            )}
                            <StepProgressBar>
                                <StepProgressFill $progress={step.progress} $isComplete={step.progress === 100} />
                            </StepProgressBar>
                        </StepContent>
                    </StepItem>
                ))}
            </StepsSection>

            {/* 액션 버튼 */}
            <Actions>
                {progress.status === 'completed' && (
                    <ActionButton $primary onClick={handleDownload}>
                        <FiDownload size={20} />
                        <span>영상 다운로드</span>
                    </ActionButton>
                )}

                {(progress.status === 'failed' || progress.status === 'completed') && (
                    <ActionButton onClick={handleReset}>
                        <FiRefreshCw size={20} />
                        <span>새로 시작</span>
                    </ActionButton>
                )}
            </Actions>

            {/* 작업 ID */}
            {progress.taskId && (
                <TaskId>
                    <strong>작업 ID:</strong> {progress.taskId}
                </TaskId>
            )}
        </Container>
    );
};

// Styled Components
const Container = styled.div`
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 2rem;
  max-width: 56rem;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
`;

const IconContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SpinningIcon = styled.div`
  animation: spin 1s linear infinite;
  display: flex;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const Title = styled.h2`
  font-size: 1.5rem;
  font-weight: bold;
  color: #111827;
  margin: 0 0 0.5rem 0;
`;

const StatusBadge = styled.span`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid;

  ${props => {
        switch (props.$status) {
            case 'completed':
                return `
          color: #065f46;
          background: #d1fae5;
          border-color: #6ee7b7;
        `;
            case 'failed':
                return `
          color: #991b1b;
          background: #fee2e2;
          border-color: #fca5a5;
        `;
            case 'processing':
                return `
          color: #1e40af;
          background: #dbeafe;
          border-color: #93c5fd;
        `;
            default:
                return `
          color: #4b5563;
          background: #f3f4f6;
          border-color: #d1d5db;
        `;
        }
    }}
`;

const ProgressSection = styled.div`
  margin-bottom: 1.5rem;
`;

const ProgressHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const ProgressLabel = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
`;

const ProgressValue = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
`;

const ProgressBarContainer = styled.div`
  width: 100%;
  height: 0.75rem;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
`;

const ProgressBarFill = styled.div`
  height: 100%;
  width: ${props => props.$progress}%;
  background: #2563eb;
  border-radius: 9999px;
  transition: width 0.5s ease-out;
`;

const CurrentStep = styled.div`
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;

  p {
    margin: 0;
    color: #374151;
    font-weight: 500;
    text-align: center;
  }
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  color: #b91c1c;
  margin-bottom: 1.5rem;
`;

const StepsSection = styled.div`
  margin-bottom: 2rem;
`;

const StepsTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
`;

const StepItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const StepIcon = styled.div`
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 500;

  ${props => {
        if (props.$isComplete) {
            return `
        background: #10b981;
        color: white;
      `;
        } else if (props.$isActive) {
            return `
        background: #2563eb;
        color: white;
      `;
        } else {
            return `
        background: #e5e7eb;
        color: #6b7280;
      `;
        }
    }}
`;

const StepContent = styled.div`
  flex: 1;
`;

const StepHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
`;

const StepName = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
`;

const StepProgress = styled.span`
  font-size: 0.875rem;
  color: #6b7280;
`;

const StepDetail = styled.div`
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  font-style: italic;
`;

const StepProgressBar = styled.div`
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
`;

const StepProgressFill = styled.div`
  height: 100%;
  width: ${props => props.$progress}%;
  background: ${props => props.$isComplete ? '#10b981' : '#2563eb'};
  border-radius: 9999px;
  transition: width 0.5s ease-out;
`;

const Actions = styled.div`
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;

  ${props => props.$primary ? `
    background: #2563eb;
    color: white;

    &:hover {
      background: #1d4ed8;
    }
  ` : `
    background: #e5e7eb;
    color: #1f2937;

    &:hover {
      background: #d1d5db;
    }
  `}
`;

const TaskId = styled.div`
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
`;

export default ProgressTracker;
