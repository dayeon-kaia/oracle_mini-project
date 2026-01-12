import json
import re
from pathlib import Path
import fitz  # PyMuPDF

PDF_PATH = Path("data/kdca_sepsis_2024.pdf")
OUT_JSONL = Path("build/evidence.jsonl")

# 사용자가 지정한 문서 페이지(1-based)
RANGES = [
    ("index", "권고문 요약표", 6, 6),
    ("lactate", "젖산", 38, 45),
    ("fluid", "수액", 46, 62),
    ("map", "MAP 목표", 63, 67),
    ("abx", "항생제", 77, 88),
    ("pressor", "승압제", 93, 143),
]

def normalize_text(t: str) -> str:
    t = t.replace("\u00a0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def split_paragraphs(text: str, max_chars=900):
    """
    너무 긴 문단은 잘라서 Evidence chunk로 만듭니다.
    권고문/표가 한 줄로 뭉개지는 경우가 있어, 일단 문단 단위 → 길이 기준 분할.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    for p in paras:
        if len(p) <= max_chars:
            chunks.append(p)
        else:
            # 긴 문단은 문장 단위로 대충 분할
            sentences = re.split(r"(?<=[.!?])\s+|(?<=\.)\n+", p)
            buf = ""
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(buf) + len(s) + 1 <= max_chars:
                    buf = (buf + " " + s).strip()
                else:
                    if buf:
                        chunks.append(buf)
                    buf = s
            if buf:
                chunks.append(buf)
    return chunks

def guess_chunk_type(text: str) -> str:
    """
    매우 단순한 휴리스틱.
    실제로는 '권고문'이라는 표현/형식이 있는 문단이 가장 중요하므로 recommendation으로 태깅될 확률을 높입니다.
    """
    key = text[:200]
    if re.search(r"권고|권\s*고|Recommendation|권고문", key):
        return "recommendation"
    if re.search(r"PICO|핵심질문|Key Question|KQ", key):
        return "pico"
    if re.search(r"근거|GRADE|무작위|연구|메타분석", key):
        return "evidence"
    return "basic"

def main():
    assert PDF_PATH.exists(), f"PDF not found: {PDF_PATH}"

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(PDF_PATH)
    total_pages = doc.page_count
    print(f"PDF loaded. total_pages={total_pages}")

    rows = []
    for topic, label, start_p, end_p in RANGES:
        # 문서 페이지(1-based)를 PyMuPDF 인덱스(0-based)로 변환
        # p1 -> index 0
        start_i = start_p - 1
        end_i = end_p - 1

        if start_i < 0 or end_i >= total_pages:
            print(f"[WARN] Range out of bounds: {label} p{start_p}-p{end_p} -> idx {start_i}-{end_i}")
            continue

        for i in range(start_i, end_i + 1):
            page = doc.load_page(i)
            text = page.get_text("text")
            text = normalize_text(text)

            if not text:
                continue

            # 페이지 전체를 한 덩어리로 넣지 말고 문단 단위로 분할
            chunks = split_paragraphs(text, max_chars=900)

            for j, chunk in enumerate(chunks):
                chunk_type = guess_chunk_type(chunk)
                _id = f"KDCA_2024_EVID_p{(i+1):03d}_{topic}_{j:03d}"
                rows.append({
                    "id": _id,
                    "content": chunk,
                    "metadata": {
                        "doc": "KDCA_Sepsis_2024",
                        "doc_type": "evidence",
                        "topic": topic,
                        "label": label,
                        "chunk_type": chunk_type,
                        "pdf_page": i + 1,             # 파일 내부 페이지 기준(1-based로 표시)
                        "pdf_page_start": i + 1,
                        "pdf_page_end": i + 1,
                        "anchor": f"p{i+1}",
                        "lang": "ko",
                    }
                })

    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Saved evidence chunks: {len(rows)} -> {OUT_JSONL}")

    # 빠른 검증: 첫 3개만 출력
    for r in rows[:3]:
        print("\n--- SAMPLE ---")
        print(r["id"], r["metadata"])
        print(r["content"][:300])

if __name__ == "__main__":
    main()
