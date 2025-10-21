import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiServer, FiCpu, FiHardDrive, FiZap, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';
import apiService from '../services/api';

const SystemStatus = () => {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchHealth = async () => {
        try {
            setLoading(true);
            setError(null);
            const healthData = await apiService.checkHealth();
            setHealth(healthData);
        } catch (err) {
            setError('시스템 상태를 확인할 수 없습니다.');
            console.error('Health check failed:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
        const interval = setInterval(fetchHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <Container>
                <LoadingContainer>
                    <Spinner />
                    <span>시스템 상태 확인 중...</span>
                </LoadingContainer>
            </Container>
        );
    }

    if (error) {
        return (
            <Container>
                <ErrorContainer>
                    <FiAlertTriangle size={20} />
                    <span>{error}</span>
                </ErrorContainer>
            </Container>
        );
    }

    if (!health) return null;

    const getMemoryColor = (percent) => {
        if (percent < 50) return '#10b981';
        if (percent < 80) return '#f59e0b';
        return '#ef4444';
    };

    const vibevoiceReady = health.vibevoice.status === 'ready';

    return (
        <Container>
            <Header>
                <HeaderTitle>
                    <FiServer size={24} />
                    <span>시스템 상태</span>
                </HeaderTitle>
                <StatusBadge $isHealthy={health.status === 'healthy'}>
                    {health.status === 'healthy' ? (
                        <>
                            <FiCheckCircle size={16} />
                            <span>정상</span>
                        </>
                    ) : (
                        <>
                            <FiAlertTriangle size={16} />
                            <span>오류</span>
                        </>
                    )}
                </StatusBadge>
            </Header>

            <Grid>
                {/* 시스템 리소스 */}
                <Section>
                    <SectionTitle>
                        <FiCpu size={20} />
                        <span>시스템 리소스</span>
                    </SectionTitle>

                    <InfoBox>
                        <InfoHeader>
                            <InfoLabel>메모리 사용률</InfoLabel>
                            <InfoValue color={getMemoryColor(health.system.memory_percent)}>
                                {health.system.memory_percent.toFixed(1)}%
                            </InfoValue>
                        </InfoHeader>
                        <ProgressBar>
                            <ProgressFill
                                progress={health.system.memory_percent}
                                color={getMemoryColor(health.system.memory_percent)}
                            />
                        </ProgressBar>
                        <InfoSubtext>
                            사용 가능: {health.system.memory_available_gb}GB
                        </InfoSubtext>
                    </InfoBox>

                    <StatusItem>
                        <StatusItemLabel>
                            <FiZap size={16} />
                            <span>GPU</span>
                        </StatusItemLabel>
                        <StatusItemValue>
                            {health.system.gpu_available ? (
                                <>
                                    <FiCheckCircle size={16} color="#10b981" />
                                    <span style={{ color: '#10b981' }}>사용 가능</span>
                                </>
                            ) : (
                                <>
                                    <FiAlertTriangle size={16} color="#f59e0b" />
                                    <span style={{ color: '#f59e0b' }}>CPU 모드</span>
                                </>
                            )}
                        </StatusItemValue>
                    </StatusItem>

                    {health.system.gpu_available && health.system.gpu_memory_total_gb && (
                        <InfoBox>
                            <InfoHeader>
                                <InfoLabel>GPU 메모리</InfoLabel>
                                <InfoValue>
                                    {health.system.gpu_memory_free_gb}GB / {health.system.gpu_memory_total_gb}GB
                                </InfoValue>
                            </InfoHeader>
                            <ProgressBar>
                                <ProgressFill
                                    progress={((health.system.gpu_memory_total_gb - (health.system.gpu_memory_free_gb || 0)) / health.system.gpu_memory_total_gb) * 100}
                                    color="#3b82f6"
                                />
                            </ProgressBar>
                        </InfoBox>
                    )}
                </Section>

                {/* VibeVoice 상태 */}
                <Section>
                    <SectionTitle>
                        <FiHardDrive size={20} />
                        <span>VibeVoice</span>
                    </SectionTitle>

                    <VibeBadge $isReady={vibevoiceReady}>
                        {vibevoiceReady ? (
                            <>
                                <FiCheckCircle size={16} />
                                <span>준비 완료</span>
                            </>
                        ) : (
                            <>
                                <FiAlertTriangle size={16} />
                                <span>오류</span>
                            </>
                        )}
                    </VibeBadge>

                    <VibeMessage>
                        <p>{health.vibevoice.message}</p>
                        {health.vibevoice.device && (
                            <DeviceInfo>실행 모드: {health.vibevoice.device.toUpperCase()}</DeviceInfo>
                        )}
                    </VibeMessage>
                </Section>
            </Grid>

            <Footer>
                마지막 업데이트: {new Date(health.timestamp).toLocaleString('ko-KR')}
            </Footer>
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

const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6b7280;
`;

const Spinner = styled.div`
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #2563eb;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const ErrorContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #dc2626;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
`;

const HeaderTitle = styled.h2`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const StatusBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid;

  ${props => props.$isHealthy ? `
    color: #065f46;
    background: #d1fae5;
    border-color: #6ee7b7;
  ` : `
    color: #991b1b;
    background: #fee2e2;
    border-color: #fca5a5;
  `}
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
`;

const Section = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const SectionTitle = styled.h3`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 500;
  color: #111827;
  margin: 0;
`;

const InfoBox = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const InfoHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const InfoLabel = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
`;

const InfoValue = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.color || '#111827'};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
`;

const ProgressFill = styled.div`
  height: 100%;
  width: ${props => props.progress}%;
  background: ${props => props.color};
  border-radius: 9999px;
  transition: width 0.3s;
`;

const InfoSubtext = styled.p`
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.5rem;
`;

const StatusItemLabel = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
`;

const StatusItemValue = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
`;

const VibeBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid;
  width: fit-content;

  ${props => props.$isReady ? `
    color: #065f46;
    background: #d1fae5;
    border-color: #6ee7b7;
  ` : `
    color: #991b1b;
    background: #fee2e2;
    border-color: #fca5a5;
  `}
`;

const VibeMessage = styled.div`
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.5rem;

  p {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: #6b7280;
  }
`;

const DeviceInfo = styled.p`
  font-size: 0.75rem !important;
  color: #6b7280 !important;
  margin: 0 !important;
`;

const Footer = styled.div`
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  text-align: center;
  font-size: 0.75rem;
  color: #6b7280;
`;

export default SystemStatus;
