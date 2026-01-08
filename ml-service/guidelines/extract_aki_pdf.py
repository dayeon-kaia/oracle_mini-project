#!/usr/bin/env python3
"""
AKI 진료지침 PDF 텍스트 추출
"""

import json
import pdfplumber

PDF_PATH = "/home/hykim/projects/mimic_dev/ml-service/guidelines/급성 신손상의 정의와 평가 임상 진료 지침.pdf"

def extract_aki_pdf():
    """AKI PDF 전체 추출"""
    print("Extracting AKI guideline PDF...")
    with pdfplumber.open(PDF_PATH) as pdf:
        pages = []
        for i in range(len(pdf.pages)):
            text = pdf.pages[i].extract_text()
            if text:
                pages.append({"page": i+1, "text": text})
                print(f"  Page {i+1}: {len(text)} chars")
        return pages

def main():
    pages = extract_aki_pdf()
    
    output = {"aki": pages}
    
    with open("aki_extracted_text.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to aki_extracted_text.json")
    print(f"  Total pages: {len(pages)}")

if __name__ == "__main__":
    main()
