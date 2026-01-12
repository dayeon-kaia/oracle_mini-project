#!/usr/bin/env python3
"""
VectorDB RAG 검증 스크립트
"""

import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import json

load_dotenv()

PERSIST_DIR = os.getenv("PERSIST_DIR", "./db_medical_md")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_md")
HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")

def test_rag_queries():
    """RAG 쿼리 테스트"""
    print("=" * 80)
    print("🧪 RAG VectorDB 검증 테스트")
    print("=" * 80)
    
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    
    # 테스트 쿼리
    test_cases = [
        {
            "name": "젖산 측정",
            "query": "패혈증 환자에서 젖산을 언제 측정해야 하나요?",
            "expected_keywords": ["젖산", "lactate", "측정"]
        },
        {
            "name": "수액 소생술",
            "query": "패혈쇼크 환자에게 수액을 얼마나 투여해야 하나요?",
            "expected_keywords": ["30 ml/kg", "수액", "3시간"]
        },
        {
            "name": "승압제 선택",
            "query": "패혈쇼크에서 승압제는 무엇을 사용하나요?",
            "expected_keywords": ["norepinephrine", "노르에피네프린"]
        },
        {
            "name": "항생제 투여",
            "query": "패혈증 환자 항생제는 언제 투여하나요?",
            "expected_keywords": ["1시간", "항생제", "광범위"]
        },
        {
            "name": "MAP 목표",
            "query": "패혈쇼크에서 혈압 목표는?",
            "expected_keywords": ["MAP", "65", "mmHg"]
        }
    ]
    
    print(f"\n📊 총 {len(test_cases)}개 쿼리 테스트\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}/{len(test_cases)}: {test['name']}")
        print(f"{'─' * 80}")
        print(f"Query: {test['query']}")
        
        results = vectorstore.similarity_search(test['query'], k=3)
        
        if results:
            print(f"✓ Found {len(results)} results\n")
            
            for j, result in enumerate(results, 1):
                meta = result.metadata
                content_preview = result.page_content[:150].replace('\n', ' ')
                
                print(f"  [{j}] {meta.get('card_id')}")
                print(f"      Role: {meta.get('card_role')}")
                print(f"      Section: {meta.get('section')}")
                print(f"      Page: p{meta.get('page')}")
                
                # bundle 파싱
                bundle_str = meta.get('bundle', '[]')
                try:
                    bundle = json.loads(bundle_str) if isinstance(bundle_str, str) else bundle_str
                    print(f"      Bundle: {bundle}")
                except:
                    print(f"      Bundle: {bundle_str}")
                
                print(f"      Content: {content_preview}...")
                
                # 키워드 매칭 확인
                matched_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in result.page_content.lower()]
                if matched_keywords:
                    print(f"      ✓ Matched keywords: {matched_keywords}")
                print()
        else:
            print(f"✗ No results found\n")
    
    # 통계
    print(f"\n{'=' * 80}")
    print(f"📈 VectorDB 통계")
    print(f"{'=' * 80}")
    
    collection = vectorstore._collection
    total_count = collection.count()
    print(f"  총 Document 수: {total_count}")
    
    all_docs = collection.get(include=["metadatas"])
    if all_docs and all_docs["metadatas"]:
        role_count = {}
        section_count = {}
        
        for meta in all_docs["metadatas"]:
            role = meta.get("card_role", "UNKNOWN")
            section = meta.get("section", "UNKNOWN")
            
            role_count[role] = role_count.get(role, 0) + 1
            section_count[section] = section_count.get(section, 0) + 1
        
        print(f"\n  card_role 분포:")
        for role, count in sorted(role_count.items()):
            print(f"    - {role}: {count}")
        
        print(f"\n  section 분포:")
        for section, count in sorted(section_count.items()):
            print(f"    - {section}: {count}")
    
    print(f"\n{'=' * 80}")
    print(f"✅ 검증 완료!")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    test_rag_queries()
