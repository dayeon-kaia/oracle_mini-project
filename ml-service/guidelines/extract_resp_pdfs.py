#!/usr/bin/env python3
"""
호흡/환기 가이드라인 PDF에서 핵심 텍스트 추출
"""

import json
import pdfplumber

# PDF 파일 경로
PDF_JSCC = "/home/hykim/projects/mimic_dev/ml-service/guidelines/2012 JSCC 중환자실에서의 기도관리.pdf"
PDF_ARDS = "/home/hykim/projects/mimic_dev/ml-service/guidelines/2016 대한중환자의학회_ARDS 지침서.pdf"

def extract_jscc():
    """JSCC 기도관리 PDF에서 텍스트 추출"""
    print("Extracting JSCC...")
    with pdfplumber.open(PDF_JSCC) as pdf:
        pages = []
        for i in range(min(10, len(pdf.pages))):
            text = pdf.pages[i].extract_text()
            if text:
                pages.append({"page": i+1, "text": text})
                print(f"  Page {i+1}: {len(text)} chars")
        return pages

def extract_ards():
    """ARDS 지침서 PDF에서 텍스트 추출"""
    print("\nExtracting ARDS...")
    with pdfplumber.open(PDF_ARDS) as pdf:
        pages = []
        # 주요 페이지만 추출 (목차, 권고안, PEEP, Prone 등)
        key_pages = list(range(0, 20)) + list(range(30, 50)) + list(range(60, 80))
        for i in key_pages:
            if i < len(pdf.pages):
                text = pdf.pages[i].extract_text()
                if text:
                    pages.append({"page": i+1, "text": text})
                    print(f"  Page {i+1}: {len(text)} chars")
        return pages

def main():
    jscc_pages = extract_jscc()
    ards_pages = extract_ards()
    
    output = {
        "jscc": jscc_pages,
        "ards": ards_pages
    }
    
    with open("respiratory_pdfs_extracted.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to respiratory_pdfs_extracted.json")
    print(f"  JSCC: {len(jscc_pages)} pages")
    print(f"  ARDS: {len(ards_pages)} pages")

if __name__ == "__main__":
    main()
