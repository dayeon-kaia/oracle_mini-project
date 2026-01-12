#!/usr/bin/env python3
"""
패혈증 가이드라인 Evidence를 VectorDB에 ingestion
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

# Evidence JSON 파일 경로
EVIDENCE_JSON = "/home/hykim/projects/mimic_dev/ml-service/guidelines/sepsis_evidence.json"

# 섹션별 bundle 매핑
SECTION_TO_BUNDLE = {
    "lactate": ["SEPSIS", "LACTATE"],
    "fluid": ["SEPSIS", "FLUID"],
    "map": ["SEPSIS", "HYPOTENSION", "PRESSOR"],
    "abx": ["SEPSIS", "INFECTION"],
    "pressor": ["SEPSIS", "HYPOTENSION", "PRESSOR"],
    "diagnosis": ["SEPSIS"]
}

# 섹션별 section 이름 매핑
SECTION_KEY_TO_NAME = {
    "lactate": "Action",
    "fluid": "Action",
    "map": "Action",
    "abx": "Action",
    "pressor": "Action",
    "diagnosis": "Trigger"
}


def load_evidence():
    """Evidence JSON 로드"""
    print(f"📥 Loading Evidence from {EVIDENCE_JSON}...")
    with open(EVIDENCE_JSON, 'r', encoding='utf-8') as f:
        evidence_list = json.load(f)
    print(f"✓ Loaded {len(evidence_list)} Evidence items")
    return evidence_list


def extract_keywords(content):
    """콘텐츠에서 키워드 추출 (간단한 버전)"""
    # 주요 키워드 추출 (공백 기준 분리 후 빈도 높은 단어)
    keywords = []
    
    # 패혈증 관련 주요 용어
    terms = [
        "패혈증", "패혈쇼크", "sepsis", "shock",
        "젖산", "lactate", "수액", "fluid", "crystalloid",
        "MAP", "평균동맥압", "승압제", "vasopressor", "norepinephrine", "vasopressin",
        "항생제", "antibiotics", "배양", "culture",
        "1시간", "3시간", "소생술", "resuscitation"
    ]
    
    content_lower = content.lower()
    for term in terms:
        if term.lower() in content_lower:
            keywords.append(term)
    
    return keywords[:10]  # 최대 10개


def evidence_to_document(evidence):
    """Evidence를 Langchain Document로 변환"""
    
    # card_role 결정
    card_role = "ACTION" if evidence.get("is_recommendation", False) else "RATIONALE"
    
    # bundle 결정
    section_key = evidence.get("section", "diagnosis")
    bundle = SECTION_TO_BUNDLE.get(section_key, ["SEPSIS"])
    
    # section 이름
    section_name = SECTION_KEY_TO_NAME.get(section_key, "Action")
    
    # keywords 추출
    keywords = extract_keywords(evidence.get("content", ""))
    
    # 메타데이터 준비 (리스트는 JSON 문자열로 변환!)
    metadata = {
        "doc_type": "guideline_evidence",
        "card_id": evidence["evidence_id"],
        "card_title": "2024 질병관리청 성인 패혈증 초기치료지침서",
        "section": section_name,
        "card_role": card_role,
        "bundle": json.dumps(bundle, ensure_ascii=False),  # JSON 문자열!
        "citations": json.dumps([evidence["anchor"]], ensure_ascii=False),  # JSON 문자열!
        "keywords": json.dumps(keywords, ensure_ascii=False),  # JSON 문자열!
        "source": evidence["doc"],
        "page": evidence["pdf_page_start"],
        "language": "ko",
        "clinical_domain": json.dumps(["sepsis", "critical_care"], ensure_ascii=False)
    }
    
    # Document 생성
    return Document(
        page_content=evidence["content"],
        metadata=metadata
    )


def ingest_to_vectordb(evidence_list):
    """Evidence를 VectorDB에 삽입"""
    print(f"\n🔧 Creating embeddings model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    print(f"📝 Converting {len(evidence_list)} Evidence to Documents...")
    documents = []
    ids = []
    
    for evidence in evidence_list:
        doc = evidence_to_document(evidence)
        documents.append(doc)
        ids.append(evidence["evidence_id"])
    
    print(f"✓ Converted {len(documents)} Documents")
    
    # VectorDB에 추가
    print(f"\n💾 Adding Documents to VectorDB...")
    print(f"   Persist directory: {PERSIST_DIR}")
    print(f"   Collection: {COLLECTION_NAME}")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        ids=ids
    )
    
    print(f"✓ Successfully added {len(documents)} Documents to VectorDB")
    
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
        "패혈증 환자 젖산 측정",
        "패혈쇼크 수액 투여",
        "노르에피네프린 승압제",
        "항생제 1시간 이내"
    ]
    
    print(f"\n📊 Sample query tests:")
    for query in test_queries:
        results = vectorstore.similarity_search(query, k=3)
        print(f"\n  Query: '{query}'")
        if results:
            print(f"  ✓ Found {len(results)} results")
            print(f"    Top result: {results[0].metadata.get('card_id')} ({results[0].metadata.get('card_role')})")
            print(f"    Section: {results[0].metadata.get('section')}")
            print(f"    Content preview: {results[0].page_content[:100]}...")
        else:
            print(f"  ✗ No results found")
    
    # card_role 분포 확인
    print(f"\n📈 Metadata distribution:")
    all_docs = collection.get(include=["metadatas"])
    
    if all_docs and all_docs["metadatas"]:
        role_count = {}
        section_count = {}
        
        for meta in all_docs["metadatas"]:
            role = meta.get("card_role", "UNKNOWN")
            section = meta.get("section", "UNKNOWN")
            
            role_count[role] = role_count.get(role, 0) + 1
            section_count[section] = section_count.get(section, 0) + 1
        
        print(f"  card_role distribution: {role_count}")
        print(f"  section distribution: {section_count}")


def main():
    print("=" * 80)
    print("🚀 패혈증 가이드라인 Evidence → VectorDB Ingestion")
    print("=" * 80)
    
    # 1. Evidence 로드
    evidence_list = load_evidence()
    
    # 2. VectorDB에 삽입
    vectorstore = ingest_to_vectordb(evidence_list)
    
    # 3. 검증
    verify_ingestion(vectorstore)
    
    print("\n" + "=" * 80)
    print("✨ Ingestion Complete!")
    print("=" * 80)
    print(f"\n💡 Summary:")
    print(f"   - Evidence ingested: {len(evidence_list)}")
    print(f"   - VectorDB location: {PERSIST_DIR}")
    print(f"   - Collection: {COLLECTION_NAME}")
    print(f"\n📌 Next steps:")
    print(f"   - Test RAG API: python3 test_vectordb.py")
    print(f"   - Start ML service: cd /home/hykim/projects/mimic_dev/ml-service && python3 app.py")


if __name__ == "__main__":
    main()
