#!/usr/bin/env python3
"""
호흡/환기 가이드라인 Evidence를 기존 VectorDB에 추가
"""

import json
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# 설정
PERSIST_DIR = os.getenv("PERSIST_DIR", "./db_medical_md")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_md")
HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")

# JSONL 파일 경로
EVIDENCE_JSONL = "/home/hykim/projects/mimic_dev/ml-service/guidelines/respiratory_evidence.jsonl"

# Topic → Bundle 매핑
TOPIC_TO_BUNDLE = {
    "oxygenation": ["RESPIRATORY", "OXYGENATION"],
    "hfnc": ["RESPIRATORY", "OXYGENATION", "HFNC"],
    "niv": ["RESPIRATORY", "VENTILATION", "NIV"],
    "intubation": ["RESPIRATORY", "INTUBATION"],
    "vent_strategy": ["RESPIRATORY", "VENTILATION"],
    "ards": ["RESPIRATORY", "ARDS"],
    "peep": ["RESPIRATORY", "VENTILATION", "PEEP"],
    "prone": ["RESPIRATORY", "ARDS", "PRONE"],
    "weaning": ["RESPIRATORY", "VENTILATION", "WEANING"],
    "escalation": ["RESPIRATORY", "OXYGENATION"]
}

# Document 제목 매핑
DOC_TITLE_MAP = {
    "RESP_CARD_MD": "프로토콜 카드 1 - 호흡",
    "KSCCM_ARDS_2016": "2016 대한중환자의학회 ARDS 지침서",
    "JSCC_AIRWAY_2012": "2012 JSCC 중환자실에서의 기도관리"
}


def load_jsonl(filepath):
    """JSONL 파일 로드"""
    print(f"📥 Loading Evidence from {filepath}...")
    evidence_list = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    evidence_list.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"  ⚠️  Line {line_num}: JSON decode error - {e}")
    print(f"✓ Loaded {len(evidence_list)} Evidence items")
    return evidence_list


def determine_card_role(evidence):
    """Evidence 내용 기반 card_role 결정"""
    content = evidence.get("content", "").lower()
    
    # ACTION 키워드: 권고, 시행, 투여, 적용, 유지 등
    action_keywords = ["권고", "시행", "투여", "적용", "유지", "고려", "제한", "확인"]
    
    if any(kw in content for kw in action_keywords):
        return "ACTION"
    else:
        return "RATIONALE"


def evidence_to_document(evidence):
    """Evidence를 Langchain Document로 변환"""
    
    metadata_raw = evidence.get("metadata", {})
    
    # card_role 결정
    card_role = determine_card_role(evidence)
    
    # bundle 결정
    topic = metadata_raw.get("topic", "oxygenation")
    bundle = TOPIC_TO_BUNDLE.get(topic, ["RESPIRATORY"])
    
    # doc title
    doc_code = metadata_raw.get("doc", "RESP_CARD_MD")
    doc_title = DOC_TITLE_MAP.get(doc_code, doc_code)
    
    # 메타데이터 준비 (리스트는 JSON 문자열로 변환!)
    metadata = {
        "doc_type": "guideline_evidence",
        "card_id": evidence["id"],
        "card_title": doc_title,
        "section": "Action",  # 대부분 Action으로 통일
        "card_role": card_role,
        "bundle": json.dumps(bundle, ensure_ascii=False),
        "citations": json.dumps([metadata_raw.get("anchor", "")], ensure_ascii=False),
        "keywords": json.dumps([topic], ensure_ascii=False),
        "source": doc_code,
        "page": metadata_raw.get("pdf_page", 1),
        "language": "ko",
        "clinical_domain": json.dumps(["respiratory", "critical_care"], ensure_ascii=False)
    }
    
    # Document 생성
    return Document(
        page_content=evidence.get("content", ""),
        metadata=metadata
    )


def add_to_vectordb(evidence_list):
    """Evidence를 기존 VectorDB에 추가"""
    print(f"\n🔧 Loading existing VectorDB...")
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # 기존 VectorDB 로드
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    
    # 기존 개수 확인
    collection = vectorstore._collection
    count_before = collection.count()
    print(f"✓ Existing documents: {count_before}")
    
    print(f"\n📝 Converting {len(evidence_list)} Evidence to Documents...")
    documents = []
    ids = []
    
    for evidence in evidence_list:
        doc = evidence_to_document(evidence)
        documents.append(doc)
        ids.append(evidence["id"])
    
    print(f"✓ Converted {len(documents)} Documents")
    
    # VectorDB에 추가
    print(f"\n💾 Adding Documents to VectorDB...")
    print(f"   Persist directory: {PERSIST_DIR}")
    print(f"   Collection: {COLLECTION_NAME}")
    
    vectorstore.add_documents(documents=documents, ids=ids)
    
    # 추가 후 개수 확인
    count_after = collection.count()
    print(f"✓ Successfully added {len(documents)} Documents")
    print(f"✓ Total documents: {count_before} → {count_after} (+{count_after - count_before})")
    
    return vectorstore


def verify_ingestion(vectorstore):
    """Ingestion 검증"""
    print(f"\n🔍 Verifying ingestion...")
    
    # 총 개수 확인
    collection = vectorstore._collection
    count = collection.count()
    print(f"✓ Total documents in VectorDB: {count}")
    
    # 샘플 쿼리 테스트
    test_queries = [
        ("호흡곤란 환자 산소 투여", "respiratory"),
        ("ARDS 복와위 요법", "respiratory"),
        ("NIV 실패 기준", "respiratory"),
        ("패혈쇼크 승압제", "sepsis"),  # 기존 데이터
    ]
    
    print(f"\n📊 Sample query tests:")
    for query, expected_domain in test_queries:
        results = vectorstore.similarity_search(query, k=3)
        print(f"\n  Query: '{query}'")
        if results:
            print(f"  ✓ Found {len(results)} results")
            print(f"    Top result: {results[0].metadata.get('card_id')} ({results[0].metadata.get('card_role')})")
            
            # bundle 확인
            bundle_str = results[0].metadata.get('bundle', '[]')
            try:
                bundle = json.loads(bundle_str) if isinstance(bundle_str, str) else bundle_str
                print(f"    Bundle: {bundle}")
            except:
                print(f"    Bundle: {bundle_str}")
            
            print(f"    Content preview: {results[0].page_content[:100]}...")
        else:
            print(f"  ✗ No results found")
    
    # 메타데이터 분포 확인
    print(f"\n📈 Metadata distribution:")
    all_docs = collection.get(include=["metadatas"])
    
    if all_docs and all_docs["metadatas"]:
        role_count = {}
        source_count = {}
        
        for meta in all_docs["metadatas"]:
            role = meta.get("card_role", "UNKNOWN")
            source = meta.get("source", "UNKNOWN")
            
            role_count[role] = role_count.get(role, 0) + 1
            source_count[source] = source_count.get(source, 0) + 1
        
        print(f"  card_role distribution: {role_count}")
        print(f"  source distribution: {source_count}")


def main():
    print("=" * 80)
    print("🚀 호흡/환기 가이드라인 Evidence → VectorDB Ingestion")
    print("=" * 80)
    
    # 1. JSONL 로드
    evidence_list = load_jsonl(EVIDENCE_JSONL)
    
    # 2. VectorDB에 추가
    vectorstore = add_to_vectordb(evidence_list)
    
    # 3. 검증
    verify_ingestion(vectorstore)
    
    print("\n" + "=" * 80)
    print("✨ Ingestion Complete!")
    print("=" * 80)
    print(f"\n💡 Summary:")
    print(f"   - Respiratory Evidence added: {len(evidence_list)}")
    print(f"   - Expected total: 26 (sepsis) + {len(evidence_list)} (respiratory) = {26 + len(evidence_list)}")
    print(f"   - VectorDB location: {PERSIST_DIR}")
    print(f"   - Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()
