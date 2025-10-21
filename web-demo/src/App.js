import React from 'react';
import styled from 'styled-components';
import { AppProvider, useAppContext } from './context/AppContext';
import FileUpload from './components/FileUpload';
import ProgressTracker from './components/ProgressTracker';

const AppContent = () => {
  const { progress } = useAppContext();

  return (
    <AppContainer>
      {/* 헤더 */}
      <Header>
        <HeaderContent>
          <HeaderLeft>
            <Logo>P</Logo>
            <HeaderTitle>PDF 발표 영상 생성기</HeaderTitle>
          </HeaderLeft>
          <HeaderRight>AI 기반 자동 발표 영상 생성</HeaderRight>
        </HeaderContent>
      </Header>

      {/* 메인 컨텐츠 */}
      <Main>
        <Content>
          {/* 파일 업로드 또는 진행 상황 */}
          {progress.status === 'idle' ? (
            <FileUpload />
          ) : (
            <ProgressTracker />
          )}
        </Content>
      </Main>

      {/* 푸터 */}
      <Footer>
        <FooterContent>
          <p>© 2024 PDF 발표 영상 생성기. AI 기술로 더 나은 발표를 만들어보세요.</p>
          <Technologies>
            <span>• GPT-4 Vision</span>
            <span>• VibeVoice</span>
            <span>• FastAPI</span>
            <span>• React</span>
          </Technologies>
        </FooterContent>
      </Footer>
    </AppContainer>
  );
};

const App = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

// Styled Components
const AppContainer = styled.div`
  min-height: 100vh;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
`;

const Header = styled.header`
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e5e7eb;
`;

const HeaderContent = styled.div`
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 4rem;

  @media (max-width: 640px) {
    flex-direction: column;
    height: auto;
    padding: 1rem;
    gap: 0.5rem;
  }
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const Logo = styled.div`
  width: 2rem;
  height: 2rem;
  background: #2563eb;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.125rem;
`;

const HeaderTitle = styled.h1`
  font-size: 1.25rem;
  font-weight: bold;
  color: #111827;
  margin: 0;

  @media (max-width: 640px) {
    font-size: 1rem;
  }
`;

const HeaderRight = styled.div`
  font-size: 0.875rem;
  color: #6b7280;

  @media (max-width: 640px) {
    font-size: 0.75rem;
  }
`;

const Main = styled.main`
  flex: 1;
  max-width: 80rem;
  margin: 0 auto;
  padding: 2rem 1rem;
  width: 100%;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const Footer = styled.footer`
  background: white;
  border-top: 1px solid #e5e7eb;
  margin-top: 4rem;
`;

const FooterContent = styled.div`
  max-width: 80rem;
  margin: 0 auto;
  padding: 2rem 1rem;
  text-align: center;

  p {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: #6b7280;
  }
`;

const Technologies = styled.div`
  display: flex;
  justify-content: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  flex-wrap: wrap;
`;

export default App;