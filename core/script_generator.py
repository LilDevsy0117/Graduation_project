"""
스크립트 생성 모듈
"""

import os
import base64
from openai import AzureOpenAI
from typing import Optional

class ScriptGenerator:
    """스크립트 생성 클래스"""
    
    def __init__(self):
        # Azure OpenAI 클라이언트 초기화
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://magosaturn.openai.azure.com/"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", "YOUR_API_KEY_HERE")
        )
    
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
    
    async def generate_script_for_slide(
        self, 
        slide_num: int, 
        slide_image_path: str, 
        is_first_slide: bool = False, 
        is_last_slide: bool = False,
        previous_script: str = "",
        language: str = "korean"
    ) -> str:
        """슬라이드 번호와 이미지를 기반으로 발표 스크립트를 생성하는 함수"""
        try:
            # 언어에 따른 시스템 프롬프트
            if language == "english":
                system_prompt = """You are an experienced presentation expert with the following expertise:
- Creating clear and persuasive presentation scripts
- Engaging and captivating expression that captures audience attention
- Logical and natural content flow
- Professional yet friendly tone and manner
- Accurate understanding and interpretation of slide image content

Presentation script writing rules:
1. Compose exactly two sentences only
2. First sentence: Introduce slide content and deliver core message
3. Second sentence: Specific points or emphasis
4. Write based on actual content of slide images
5. Use natural and engaging English expressions
6. Clear language that audiences can easily understand
7. Maintain professional yet friendly tone and manner
8. Calm and confident tone suitable for presentations
9. Include natural commas and pauses for appropriate speaking pace
10. Use proper English punctuation"""
            else:  # korean
                system_prompt = """당신은 경험이 풍부한 발표 전문가입니다. 
다음의 전문성을 가지고 있습니다:
- 명확하고 설득력 있는 발표 스크립트 작성
- 청중의 관심을 끄는 매력적인 표현력
- 논리적이고 자연스러운 내용 연결
- 전문적이면서도 친근한 톤앤매너
- 슬라이드 이미지 내용을 정확히 파악하고 해석

발표 스크립트 작성 규칙:
1. 정확히 두 문장으로만 구성
2. 첫 번째 문장: 슬라이드 내용 소개 및 핵심 메시지 전달
3. 두 번째 문장: 구체적인 포인트나 강조사항
4. 슬라이드 이미지의 실제 내용을 바탕으로 작성
5. 자연스럽고 매력적인 한국어 표현 사용
6. 청중이 이해하기 쉬운 명확한 언어
7. 전문적이면서도 친근한 톤앤매너 유지
8. 발표에 적합한 차분하고 자신감 있는 톤
9. 적절한 속도로 말할 수 있도록 자연스러운 쉼표와 휴지 포함
10. 한국어 구두점은 영어 구두점으로 변환 (쌍따옴표, 작은따옴표 등)"""

            # 이미지를 base64로 인코딩
            with open(slide_image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            if is_first_slide:
                # 첫 번째 슬라이드: 인사와 함께 시작
                if language == "english":
                    user_prompt = f"""Write a presentation script for the first slide of the presentation.

Slide Information:
- Slide number: {slide_num} (First slide)
- Presentation opening

Requirements:
- Write based on actual content of slide images
- Introduce slide content attractively with greetings
- Create a compelling first impression for the audience
- Present the overall direction of the presentation

Presentation script (exactly two sentences):"""
                else:  # korean
                    user_prompt = f"""발표의 첫 번째 슬라이드에 대한 발표 스크립트를 작성해주세요.

슬라이드 정보:
- 슬라이드 번호: {slide_num}번째 (첫 번째 슬라이드)
- 발표 시작 부분

요구사항:
- 슬라이드 이미지의 실제 내용을 바탕으로 작성
- 인사말과 함께 슬라이드 내용을 매력적으로 소개
- 청중의 관심을 끄는 첫인상 만들기
- 발표의 전체적인 방향성 제시

발표 스크립트 (정확히 두 문장):"""
            elif is_last_slide:
                # 마지막 슬라이드: 발표 마무리
                if language == "english":
                    user_prompt = f"""Write a presentation script for the last slide of the presentation.

Previous slide content:
{previous_script}

Current slide information:
- Slide number: {slide_num} (Last slide)
- Presentation conclusion

Requirements:
- Write based on actual content of slide images
- Naturally conclude the previous content
- Use concluding expressions like "Finally", "In conclusion", "To summarize"
- Include closing remarks ("Thank you for your attention", "Thank you" etc.)
- End the presentation with gratitude to the audience

Presentation script (exactly two sentences):"""
                else:  # korean
                    user_prompt = f"""발표의 마지막 슬라이드에 대한 발표 스크립트를 작성해주세요.

이전 슬라이드 내용:
{previous_script}

현재 슬라이드 정보:
- 슬라이드 번호: {slide_num}번째 (마지막 슬라이드)
- 발표 마무리 부분

요구사항:
- 슬라이드 이미지의 실제 내용을 바탕으로 작성
- 이전 내용을 자연스럽게 마무리
- "마지막으로", "결론적으로", "요약하면" 등의 마무리 표현 활용
- 발표 마무리 인사말 포함 ("발표를 마치겠습니다", "감사합니다" 등)
- 청중에게 감사 인사와 함께 발표 종료

발표 스크립트 (정확히 두 문장):"""
            else:
                # 중간 슬라이드: 이전 내용과 자연스럽게 연결
                if language == "english":
                    user_prompt = f"""Write a presentation script for the {slide_num}th slide of the presentation.

Previous slide content:
{previous_script}

Current slide information:
- Slide number: {slide_num}
- Natural connection with previous content needed

Requirements:
- Write based on actual content of slide images
- Logical transition connecting with previous content
- Use connecting words like "Next", "Now", "Additionally", "Furthermore"
- Clear introduction of new content
- Natural expressions that maintain presentation flow

Presentation script (exactly two sentences):"""
                else:  # korean
                    user_prompt = f"""발표의 {slide_num}번째 슬라이드에 대한 발표 스크립트를 작성해주세요.

이전 슬라이드 내용:
{previous_script}

현재 슬라이드 정보:
- 슬라이드 번호: {slide_num}번째
- 이전 내용과의 자연스러운 연결 필요

요구사항:
- 슬라이드 이미지의 실제 내용을 바탕으로 작성
- 이전 내용과 논리적으로 연결되는 전환
- "다음으로", "이제", "또한", "더 나아가" 등의 연결어 활용
- 새로운 내용에 대한 명확한 소개
- 발표의 흐름을 유지하는 자연스러운 표현

발표 스크립트 (정확히 두 문장):"""
            
            # Azure OpenAI API 호출 (Vision 기능 사용)
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
                
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"),
                    max_tokens=200,
                    temperature=0.7,
                    top_p=0.95
                )
                script = response.choices[0].message.content.strip()
            except Exception as api_error:
                print(f"⚠️ Azure OpenAI API 오류: {api_error}")
                # API 오류 시 기본 스크립트 사용
                if is_first_slide:
                    script = f"안녕하세요. {slide_num}번째 슬라이드에 대해 발표하겠습니다. 이 내용은 중요한 포인트를 포함하고 있습니다."
                elif is_last_slide:
                    script = f"마지막으로 {slide_num}번째 슬라이드에 대해 살펴보겠습니다. 발표를 마치겠습니다. 감사합니다."
                else:
                    script = f"다음으로 {slide_num}번째 슬라이드에 대해 살펴보겠습니다. 이 부분도 중요한 내용입니다."
            
            return script
            
        except Exception as e:
            print(f"❌ 스크립트 생성 실패: {e}")
            if is_last_slide:
                return f"마지막으로 {slide_num}번째 슬라이드의 내용을 발표합니다. 발표를 마치겠습니다. 감사합니다."
            else:
                return f"{slide_num}번째 슬라이드의 내용을 발표합니다."
