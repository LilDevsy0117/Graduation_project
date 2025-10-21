"""
PDF 처리 모듈
"""

import os
import fitz  # PyMuPDF
from typing import List

class PDFProcessor:
    """PDF 처리 클래스"""
    
    def __init__(self):
        self.output_dir = "temp"
    
    async def extract_pages_from_pdf(self, pdf_path: str, task_id: str) -> List[str]:
        """PDF의 각 페이지를 이미지로 저장하는 함수"""
        try:
            task_output_dir = os.path.join(self.output_dir, task_id, "slides")
            os.makedirs(task_output_dir, exist_ok=True)
            
            doc = fitz.open(pdf_path)
            slide_images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # 페이지를 이미지로 변환 (고해상도)
                mat = fitz.Matrix(2.0, 2.0)  # 2배 확대
                pix = page.get_pixmap(matrix=mat)
                
                # 이미지 저장
                image_path = os.path.join(task_output_dir, f"slide_{page_num + 1}.png")
                pix.save(image_path)
                slide_images.append(image_path)
                
                print(f"✅ 슬라이드 {page_num + 1} 이미지 저장: {image_path}")
            
            doc.close()
            return slide_images
        
        except Exception as e:
            print(f"❌ PDF 페이지 추출 실패: {e}")
            return []
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """PDF 정보 조회"""
        try:
            doc = fitz.open(pdf_path)
            info = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", "")
            }
            doc.close()
            return info
        except Exception as e:
            print(f"❌ PDF 정보 조회 실패: {e}")
            return {"error": str(e)}



