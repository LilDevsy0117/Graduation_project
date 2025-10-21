import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { FiUpload, FiFile, FiMusic, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { useAppContext } from '../context/AppContext';

const FileUpload = () => {
  const { handleUpload, isUploading, uploadError } = useAppContext();

  const [pdfFile, setPdfFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [language, setLanguage] = useState('korean');
  const [includeSubtitles, setIncludeSubtitles] = useState(false);
  const [dragActive, setDragActive] = useState({ pdf: false, audio: false });

  const handleDrag = useCallback((e, type) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(prev => ({ ...prev, [type]: true }));
    } else if (e.type === 'dragleave') {
      setDragActive(prev => ({ ...prev, [type]: false }));
    }
  }, []);

  const handleDrop = useCallback((e, type) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(prev => ({ ...prev, [type]: false }));

    const files = Array.from(e.dataTransfer.files);
    const file = files[0];

    if (!file) return;

    if (type === 'pdf' && file.type === 'application/pdf') {
      setPdfFile(file);
    } else if (type === 'audio' && (file.type === 'audio/wav' || file.type === 'audio/mpeg')) {
      setAudioFile(file);
    }
  }, []);

  const handleFileSelect = useCallback((e, type) => {
    const file = e.target.files?.[0];
    if (file) {
      if (type === 'pdf') {
        setPdfFile(file);
      } else {
        setAudioFile(file);
      }
    }
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    if (!pdfFile || !audioFile) return;
    await handleUpload(pdfFile, audioFile, language, includeSubtitles);
  }, [pdfFile, audioFile, language, includeSubtitles, handleUpload]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Container>
      <Header>
        <Title>PDF 발표 영상 생성기</Title>
        <Subtitle>PDF 파일과 음성 샘플을 업로드하면 AI가 자동으로 발표 영상을 생성합니다</Subtitle>
      </Header>

      <Form onSubmit={handleSubmit}>
        {/* PDF 업로드 */}
        <UploadSection>
          <Label>PDF 파일 <Required>*</Required></Label>
          <DropZone
            $isActive={dragActive.pdf}
            $hasFile={!!pdfFile}
            onDragEnter={(e) => handleDrag(e, 'pdf')}
            onDragLeave={(e) => handleDrag(e, 'pdf')}
            onDragOver={(e) => handleDrag(e, 'pdf')}
            onDrop={(e) => handleDrop(e, 'pdf')}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => handleFileSelect(e, 'pdf')}
              disabled={isUploading}
              style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
            />

            {pdfFile ? (
              <FileInfo>
                <FiCheckCircle size={32} color="#10b981" />
                <div>
                  <FileName>{pdfFile.name}</FileName>
                  <FileSize>{formatFileSize(pdfFile.size)}</FileSize>
                </div>
              </FileInfo>
            ) : (
              <DropZoneContent>
                <FiFile size={48} color="#9ca3af" />
                <DropZoneTitle>PDF 파일을 드래그하거나 클릭하여 선택</DropZoneTitle>
                <DropZoneSubtitle>PDF 형식만 지원됩니다</DropZoneSubtitle>
              </DropZoneContent>
            )}
          </DropZone>
        </UploadSection>

        {/* 오디오 업로드 */}
        <UploadSection>
          <Label>음성 샘플 파일 <Required>*</Required></Label>
          <DropZone
            $isActive={dragActive.audio}
            $hasFile={!!audioFile}
            onDragEnter={(e) => handleDrag(e, 'audio')}
            onDragLeave={(e) => handleDrag(e, 'audio')}
            onDragOver={(e) => handleDrag(e, 'audio')}
            onDrop={(e) => handleDrop(e, 'audio')}
          >
            <input
              type="file"
              accept=".wav,.mp3"
              onChange={(e) => handleFileSelect(e, 'audio')}
              disabled={isUploading}
              style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
            />

            {audioFile ? (
              <FileInfo>
                <FiCheckCircle size={32} color="#10b981" />
                <div>
                  <FileName>{audioFile.name}</FileName>
                  <FileSize>{formatFileSize(audioFile.size)}</FileSize>
                </div>
              </FileInfo>
            ) : (
              <DropZoneContent>
                <FiMusic size={48} color="#9ca3af" />
                <DropZoneTitle>음성 파일을 드래그하거나 클릭하여 선택</DropZoneTitle>
                <DropZoneSubtitle>WAV, MP3 형식 지원</DropZoneSubtitle>
              </DropZoneContent>
            )}
          </DropZone>
        </UploadSection>

        {/* 언어 선택 */}
        <UploadSection>
          <Label>발표 언어</Label>
          <LanguageGrid>
            <LanguageOption
              $isSelected={language === 'korean'}
              onClick={() => setLanguage('korean')}
            >
              <input
                type="radio"
                name="language"
                value="korean"
                checked={language === 'korean'}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ display: 'none' }}
                disabled={isUploading}
              />
              <div>
                <LanguageLabel>🇰🇷 한국어</LanguageLabel>
                <LanguageDescription>한국어 발표 영상 생성</LanguageDescription>
              </div>
              {language === 'korean' && <RadioDot />}
            </LanguageOption>

            <LanguageOption
              $isSelected={language === 'english'}
              onClick={() => setLanguage('english')}
            >
              <input
                type="radio"
                name="language"
                value="english"
                checked={language === 'english'}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ display: 'none' }}
                disabled={isUploading}
              />
              <div>
                <LanguageLabel>🇺🇸 English</LanguageLabel>
                <LanguageDescription>English presentation video</LanguageDescription>
              </div>
              {language === 'english' && <RadioDot />}
            </LanguageOption>
          </LanguageGrid>
        </UploadSection>

        {/* 자막 옵션 */}
        <UploadSection>
          <Label>자막 옵션</Label>
          <SubtitleOption>
            <SubtitleCheckbox
              type="checkbox"
              id="subtitles"
              checked={includeSubtitles}
              onChange={(e) => setIncludeSubtitles(e.target.checked)}
              disabled={isUploading}
            />
            <SubtitleLabel htmlFor="subtitles">
              <SubtitleIcon>📝</SubtitleIcon>
              <div>
                <SubtitleTitle>자막 포함</SubtitleTitle>
                <SubtitleDescription>
                  발표 스크립트를 영상에 자막으로 표시
                </SubtitleDescription>
              </div>
            </SubtitleLabel>
          </SubtitleOption>
        </UploadSection>

        {/* 오류 메시지 */}
        {uploadError && (
          <ErrorMessage>
            <FiAlertCircle size={20} />
            <span>{uploadError}</span>
          </ErrorMessage>
        )}

        {/* 업로드 버튼 */}
        <ButtonContainer>
          <SubmitButton
            type="submit"
            disabled={!pdfFile || !audioFile || isUploading}
          >
            {isUploading ? (
              <>
                <Spinner />
                <span>업로드 중...</span>
              </>
            ) : (
              <>
                <FiUpload size={20} />
                <span>발표 영상 생성 시작</span>
              </>
            )}
          </SubmitButton>
        </ButtonContainer>
      </Form>
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
  text-align: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  color: #6b7280;
  font-size: 0.875rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const UploadSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
`;

const Required = styled.span`
  color: #ef4444;
`;

const DropZone = styled.div`
  position: relative;
  border: 2px dashed ${props => props.$isActive ? '#2563eb' : props.$hasFile ? '#10b981' : '#d1d5db'};
  background: ${props => props.$isActive ? '#eff6ff' : props.$hasFile ? '#f0fdf4' : 'white'};
  border-radius: 0.5rem;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    border-color: ${props => props.$hasFile ? '#10b981' : '#9ca3af'};
  }
`;

const DropZoneContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
`;

const DropZoneTitle = styled.p`
  font-size: 1.125rem;
  font-weight: 500;
  color: #374151;
  margin: 0;
`;

const DropZoneSubtitle = styled.p`
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
`;

const FileName = styled.p`
  font-weight: 500;
  color: #065f46;
  margin: 0;
`;

const FileSize = styled.p`
  font-size: 0.875rem;
  color: #059669;
  margin: 0;
`;

const LanguageGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
`;

const LanguageOption = styled.label`
  position: relative;
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid ${props => props.$isSelected ? '#2563eb' : '#e5e7eb'};
  background: ${props => props.$isSelected ? '#eff6ff' : 'white'};
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #d1d5db;
  }
`;

const LanguageLabel = styled.p`
  font-weight: 500;
  color: #111827;
  margin: 0 0 0.25rem 0;
`;

const LanguageDescription = styled.p`
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
`;

const RadioDot = styled.div`
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 0.75rem;
  height: 0.75rem;
  background: #2563eb;
  border-radius: 50%;
`;

const Slider = styled.input`
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 0.5rem;
  outline: none;
  cursor: pointer;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 1.25rem;
    height: 1.25rem;
    background: #2563eb;
    border-radius: 50%;
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 1.25rem;
    height: 1.25rem;
    background: #2563eb;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }
`;

const SliderLabels = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
`;

const SubtitleOption = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
`;

const SubtitleCheckbox = styled.input`
  width: 1.25rem;
  height: 1.25rem;
  margin-top: 0.125rem;
  cursor: pointer;
  accent-color: #2563eb;
`;

const SubtitleLabel = styled.label`
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  flex: 1;
`;

const SubtitleIcon = styled.div`
  font-size: 1.5rem;
  margin-top: 0.125rem;
`;

const SubtitleTitle = styled.p`
  font-weight: 500;
  color: #111827;
  margin: 0 0 0.25rem 0;
`;

const SubtitleDescription = styled.p`
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
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
`;

const ButtonContainer = styled.div`
  text-align: center;
`;

const SubmitButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;
  font-size: 1.125rem;
  font-weight: 500;
  color: white;
  background: #2563eb;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;

  &:hover:not(:disabled) {
    background: #1d4ed8;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Spinner = styled.div`
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

export default FileUpload;
