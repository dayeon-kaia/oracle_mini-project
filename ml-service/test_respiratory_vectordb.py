#!/usr/bin/env python3
"""
호흡/환기 가이드라인 쿼리 테스트
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

def test_respiratory_queries():
    """호흡 가이드라인 쿼리 테스트"""
    print("=" * 80)
    print("🧪 호흡/환기 + 패혈증 통합 VectorDB 테스트")
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
            "name": "호흡곤란 산소 투여",
            "query": "호흡곤란 환자에게 산소를 어떻게 투여하나요?",
            "expected_bundle": "RESPIRATORY"
        },
        {
            "name": "ARDS 복와위",
            "query": "ARDS 환자 복와위 요법은 언제 시행하나요?",
            "expected_bundle": "RESPIRATORY"
        },
        {
            "name": "NIV 적응증",
            "query": "NIV는 언제 시작하나요?",
            "expected_bundle": "RESPIRATORY"
        },
        {
            "name": "기관삽관 기준",
            "query": "기관삽관은 언제 해야 하나요?",
            "expected_bundle": "RESPIRATORY"
        },
        {
            "name": "패혈증 젖산 (기존)",
            "query": "패혈증 환자 젖산 측정",
            "expected_bundle": "SEPSIS"
        },
        {
            "name": "패혈쇼크 승압제 (기존)",
            "query": "패혈쇼크 승압제",
            "expected_bundle": "SEPSIS"
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
                content_preview = result.page_content[:120].replace('\n', ' ')
                
                print(f"  [{j}] {meta.get('card_id')}")
                print(f"      Role: {meta.get('card_role')}")
                print(f"      Source: {meta.get('source')}")
                
                # bundle 파싱
                bundle_str = meta.get('bundle', '[]')
                try:
                    bundle = json.loads(bundle_str) if isinstance(bundle_str, str) else bundle_str
                    print(f"      Bundle: {bundle}")
                    
                    # expected bundle 확인
                    if test['expected_bundle'] in bundle:
                        print(f"      ✓ Correct bundle")
                except:
                    print(f"      Bundle: {bundle_str}")
                
                print(f"      Content: {content_preview}...")
                print()
        else:
            print(f"✗ No results found\n")
    
    # 통계
    print(f"\n{'=' * 80}")
    print(f"📈 VectorDB 통합 통계")
    print(f"{'=' * 80}")
    
    collection = vectorstore._collection
    total_count = collection.count()
    print(f"  총 Document 수: {total_count}")
    
    all_docs = collection.get(include=["metadatas"])
    if all_docs and all_docs["metadatas"]:
        source_count = {}
        bundle_count = {}
        
        for meta in all_docs["metadatas"]:
            source = meta.get("source", "UNKNOWN")
            source_count[source] = source_count.get(source, 0) + 1
            
            # bundle 분석
            bundle_str = meta.get("bundle", "[]")
            try:
                bundle = json.loads(bundle_str) if isinstance(bundle_str, str) else bundle_str
                for b in bundle:
                    bundle_count[b] = bundle_count.get(b, 0) + 1
            except:
                pass
        
        print(f"\n  source 분포:")
        for source, count in sorted(source_count.items()):
            print(f"    - {source}: {count}")
        
        print(f"\n  주요 bundle:")
        for bundle, count in sorted(bundle_count.items(), key=lambda x: -x[1])[:15]:
            print(f"    - {bundle}: {count}")
    
    print(f"\n{'=' * 80}")
    print(f"✅ 테스트 완료!")
    print(f"{'=' * 80}")
    print(f"\n💡 패혈증(26) + 호흡(51) = 총 {total_count}개 Evidence 통합 완료")


if __name__ == "__main__":
    test_respiratory_queries()
