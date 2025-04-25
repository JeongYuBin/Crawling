import os
import pdfplumber

# 참고 사이트 : https://jaylala.tistory.com/entry/%EC%97%85%EB%AC%B4%EC%9E%90%EB%8F%99%ED%99%94-with-Python-PDF%EB%AC%B8%EC%84%9C%EB%82%B4%EC%9A%A9-%EC%B6%94%EC%B6%9CPDFPlumber-%ED%99%9C%EC%9A%A9-3-%ED%91%9C-%EC%B6%94%EC%B6%9C

# PDF 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "2025_1_schedule.pdf")

# 저장 폴더 만들기
output_dir = os.path.join(current_dir, "debug_images")
os.makedirs(output_dir, exist_ok=True)

# 테이블 인식 세팅
custom_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_y_tolerance": 3,
    "intersection_x_tolerance": 5,
    "join_tolerance": 2,
}

# PDF 열기
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        im = page.to_image(resolution=150)
        im.debug_tablefinder(table_settings=custom_settings)

        filename = f"page_{i:02}_debug.png"
        output_path = os.path.join(output_dir, filename)
        im.save(output_path)
        print(f"저장 완료: {filename}")

print(f"\n총 {len(pdf.pages)}장 저장 완료! 확인 경로: {output_dir}")
