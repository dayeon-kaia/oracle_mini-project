#!/usr/bin/env python3
"""
패혈증 가이드라인 PDF에서 텍스트 추출
"""

import json
from pathlib import Path
try:
    import pdfplumber
except ImportError:
    print("pdfplumber not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "pdfplumber"])
    import pdfplumber


PDF_PATH = "/home/hykim/projects/mimic_dev/ml-service/guidelines/2024 질병관리청 성인 패혈증 초기치료지침서.pdf"

# 섹션별 페이지 범위 (PDF 페이지 번호, 1-indexed)
SECTIONS = {
    "summary": {"name": "권고문 요약표", "start": 6, "end": 6, "section_key": "diagnosis"},
    "lactate": {"name": "젖산", "start": 38, "end": 45, "section_key": "lactate"},
    "fluid": {"name": "수액", "start": 46, "end": 62, "section_key": "fluid"},
    "map": {"name": "MAP 목표", "start": 63, "end": 67, "section_key": "map"},
    "abx": {"name": "항생제", "start": 77, "end": 88, "section_key": "abx"},
    "pressor": {"name": "승압제", "start": 93, "end": 143, "section_key": "pressor"}
}


def extract_text_from_pdf():
    """PDF에서 섹션별로 텍스트 추출"""
    extracted_sections = {}
    
    with pdfplumber.open(PDF_PATH) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages in PDF: {total_pages}")
        
        for section_id, info in SECTIONS.items():
            print(f"\n추출 중: {info['name']} (p{info['start']}-{info['end']})")
            section_text = []
            
            for page_num in range(info['start'], info['end'] + 1):
                if page_num <= total_pages:
                    page = pdf.pages[page_num - 1]  # 0-indexed
                    text = page.extract_text()
                    if text:
                        section_text.append({
                            "page": page_num,
                            "text": text
                        })
                        print(f"  - p{page_num}: {len(text)} characters")
            
            extracted_sections[section_id] = {
                "name": info['name'],
                "section_key": info['section_key'],
                "pages": section_text,
                "page_range": f"{info['start']}-{info['end']}"
            }
    
    return extracted_sections


def save_extracted_text(sections, output_path):
    """추출된 텍스트를 JSON으로 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
    print(f"\n추출된 텍스트 저장: {output_path}")


def main():
    print("=" * 60)
    print("패혈증 가이드라인 PDF 텍스트 추출")
    print("=" * 60)
    
    # 텍스트 추출
    sections = extract_text_from_pdf()
    
    # JSON으로 저장
    output_path = "/home/hykim/projects/mimic_dev/ml-service/guidelines/sepsis_extracted_text.json"
    save_extracted_text(sections, output_path)
    
    print("\n✓ 추출 완료!")
    print(f"\n다음 단계: 추출된 텍스트를 검토하고 Evidence Chunk를 생성하세요.")


if __name__ == "__main__":
    main()
