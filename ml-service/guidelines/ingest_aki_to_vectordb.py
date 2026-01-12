#!/usr/bin/env python3
"""
AKI 가이드라인 Evidence를 기존 VectorDB에 추가
"""

import json
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# 설정
PERSIST_DIR = "/home/hykim/projects/mimic_dev/ml-service/db_medical_md"
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_md")
HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")

# JSONL 파일 경로
EVIDENCE_JSONL = "/home/hykim/projects/mimic_dev/ml-service/guidelines/aki_evidence.jsonl"

# Topic → Bundle 매핑 (AKI 전용)
TOPIC_TO_BUNDLE = {
    "definition": ["AKI", "RENAL"],
    "staging": ["AKI", "RENAL", "STAGING"],
    "urine_output": ["AKI", "RENAL", "URINE_OUTPUT"],
    "creatinine": ["AKI", "RENAL", "CREATININE"],
    "diagnosis": ["AKI", "RENAL", "DIAGNOSIS"],
    "evaluation": ["AKI", "RENAL", "EVALUATION"],
    "monitoring": ["AKI", "RENAL", "MONITORING"],
    "etiology": ["AKI", "RENAL", "ETIOLOGY"],
    "risk": ["AKI", "RENAL", "RISK"],
    "imaging": ["AKI", "RENAL", "IMAGING"],
    "labs": ["AKI", "RENAL", "LABS"],
    "note": ["AKI", "RENAL"]
}

# Document 제목
DOC_TITLE = "급성 신손상의 정의와 평가: 임상 진료 지침"


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
    topic = evidence.get("metadata", {}).get("topic", "")
    chunk_type = evidence.get("metadata", {}).get("chunk_type", "")
    
    # definition, criteria, table은 주로 ACTION
    if chunk_type in ["definition", "criteria", "table"]:
        return "ACTION"
    # steps는 ACTION
    elif chunk_type == "steps":
        return "ACTION"
    # note는 RATIONALE
    elif chunk_type == "note":
        return "RATIONALE"
    else:
        return "ACTION"


def evidence_to_document(evidence):
    """Evidence를 Langchain Document로 변환"""
    
    metadata_raw = evidence.get("metadata", {})
    
    # card_role 결정
    card_role = determine_card_role(evidence)
    
    # bundle 결정
    topic = metadata_raw.get("topic", "definition")
    bundle = TOPIC_TO_BUNDLE.get(topic, ["AKI", "RENAL"])
    
    # 메타데이터 준비 (리스트는 JSON 문자열로 변환!)
    metadata = {
        "doc_type": "guideline_evidence",
        "card_id": evidence["id"],
        "card_title": DOC_TITLE,
        "section": "Action",
        "card_role": card_role,
        "bundle": json.dumps(bundle, ensure_ascii=False),
        "citations": json.dumps([metadata_raw.get("anchor", "")], ensure_ascii=False),
        "keywords": json.dumps([topic], ensure_ascii=False),
        "source": metadata_raw.get("doc", "AKI_Guideline_KR"),
        "page": metadata_raw.get("pdf_page", 1),
        "language": "ko",
        "clinical_domain": json.dumps(["acute_kidney_injury", "nephrology", "critical_care"], ensure_ascii=False)
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
    try:
        count_before = collection.count()
    except (TypeError, AttributeError) as e:
        print(f"  ⚠️  ChromaDB count() error (Python 3.13 compatibility): {e}")
        print(f"  Using alternative method to get count...")
        try:
            all_ids = collection.get(limit=99999, include=[])
            count_before = len(all_ids['ids']) if all_ids and 'ids' in all_ids else 0
        except:
            count_before = 0
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
    try:
        count_after = collection.count()
    except (TypeError, AttributeError) as e:
        print(f"  ⚠️  ChromaDB count() error (Python 3.13 compatibility): {e}")
        print(f"  Using alternative method to get count...")
        try:
            all_ids = collection.get(limit=99999, include=[])
            count_after = len(all_ids['ids']) if all_ids and 'ids' in all_ids else 0
        except:
            count_after = 0
    print(f"✓ Successfully added {len(documents)} Documents")
    print(f"✓ Total documents: {count_before} → {count_after} (+{count_after - count_before})")
    
    return vectorstore


def verify_ingestion(vectorstore):
    """Ingestion 검증"""
    print(f"\n🔍 Verifying ingestion...")
    
    # 총 개수 확인
    collection = vectorstore._collection
    try:
        count = collection.count()
    except (TypeError, AttributeError) as e:
        print(f"  ⚠️  ChromaDB count() error (Python 3.13 compatibility): {e}")
        print(f"  Using alternative method to get count...")
        try:
            all_ids = collection.get(limit=99999, include=[])
            count = len(all_ids['ids']) if all_ids and 'ids' in all_ids else 0
        except:
            count = 0
    print(f"✓ Total documents in VectorDB: {count}")
    
    # 샘플 쿼리 테스트
    test_queries = [
        ("급성 신손상 진단 기준", "aki"),
        ("KDIGO stage 분류", "aki"),
        ("크레아티닌 상승", "aki"),
        ("ARDS 복와위", "respiratory"),  # 기존 데이터
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
            
            print(f"    Content preview: {results[0].page_content[:80]}...")
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
    print("🚀 AKI 가이드라인 Evidence → VectorDB Ingestion")
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
    print(f"   - AKI Evidence added: {len(evidence_list)}")
    print(f"   - Expected total: 77 (existing) + {len(evidence_list)} (AKI) = {77 + len(evidence_list)}")
    print(f"   - VectorDB location: {PERSIST_DIR}")
    print(f"   - Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()
