import fitz  # PyMuPDF 라이브러리를 'fitz'로 임포트합니다.
import os

def pdf_to_images(pdf_path, output_folder):
    """
    PDF 파일의 각 페이지를 PNG 이미지로 변환하여 저장하는 함수.

    Args:
        pdf_path (str): 변환할 PDF 파일의 경로.
        output_folder (str): 이미지를 저장할 폴더 경로.
    """
    try:
        # PDF 파일 열기
        pdf_document = fitz.open(pdf_path)

        # 출력 폴더가 없으면 생성
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        print(f"총 {pdf_document.page_count} 페이지를 이미지로 변환합니다.")

        for page_num in range(pdf_document.page_count):
            # 페이지 로드
            page = pdf_document.load_page(page_num)

            # 렌더링을 위한 설정 (dpi를 높여 고해상도 이미지로 만듭니다)
            # scale_factor = 2 (200 dpi), scale_factor = 4 (400 dpi)
            zoom = 2  # 200% 확대 (200 DPI)
            mat = fitz.Matrix(zoom, zoom)
            
            # 페이지를 픽셀맵으로 변환 (이미지 데이터)
            pix = page.get_pixmap(matrix=mat)

            # 이미지 파일 경로 설정
            image_path = os.path.join(output_folder, f"page{page_num + 1}.png")
            
            # 픽셀맵을 PNG 파일로 저장
            pix.save(image_path)
            
            print(f"페이지 {page_num + 1}이 {image_path}에 저장되었습니다.")

        pdf_document.close()
        print("모든 페이지 변환이 완료되었습니다.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 사용 예시:
    # 1. PDF 파일 경로를 지정합니다.
    pdf_file = "중간보고서 미팅.pdf"

    # 2. 이미지를 저장할 폴더 경로를 지정합니다.
    output_dir = "exported_slides"

    # 함수 실행
    pdf_to_images(pdf_file, output_dir)