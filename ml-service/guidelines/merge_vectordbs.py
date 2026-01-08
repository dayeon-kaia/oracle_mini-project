#!/usr/bin/env python3
"""
두 VectorDB 병합: 패혈증 + 호흡
"""

import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")

def merge_vectordbs():
    """두 VectorDB를 병합"""
    print("=" * 80)
    print("🔀 VectorDB 병합: 패혈증 + 호흡")
    print("=" * 80)
    
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # 1. 패혈증 DB 로드 (ml-service/db_medical_md)
    print("\n📥 Loading 패혈증 VectorDB...")
    sepsis_db = Chroma(
        persist_directory="../db_medical_md",
        collection_name="medical_md",
        embedding_function=embeddings
    )
    sepsis_count = sepsis_db._collection.count()
    print(f"✓ 패혈증 documents: {sepsis_count}")
    
    # 2. 호흡 DB 로드 (guidelines/db_medical_md)
    print("\n📥 Loading 호흡 VectorDB...")
    resp_db = Chroma(
        persist_directory="./db_medical_md",
        collection_name="medical_md",
        embedding_function=embeddings
    )
    resp_count = resp_db._collection.count()
    print(f"✓ 호흡 documents: {resp_count}")
    
    # 3. 호흡 DB의 모든 문서 가져오기
    print(f"\n📦 Extracting documents from 호흡 DB...")
    resp_data = resp_db._collection.get(include=["documents", "metadatas", "embeddings"])
    
    resp_docs = resp_data.get("documents", [])
    resp_metas = resp_data.get("metadatas", [])
    resp_ids = resp_data.get("ids", [])
    resp_embeddings = resp_data.get("embeddings", [])
    
    print(f"✓ Extracted {len(resp_docs)} documents")
    
    # 4. 패혈증 DB에 추가
    print(f"\n💾 Adding 호흡 documents to 패혈증 DB...")
    
    # Document 객체로 변환
    from langchain_core.documents import Document
    documents = []
    for doc_text, meta in zip(resp_docs, resp_metas):
        documents.append(Document(page_content=doc_text, metadata=meta))
    
    # 추가
    sepsis_db.add_documents(documents=documents, ids=resp_ids)
    
    # 5. 최종 확인
    final_count = sepsis_db._collection.count()
    print(f"✓ Added successfully")
    print(f"✓ Final count: {sepsis_count} + {resp_count} = {final_count}")
    
    print("\n" + "=" * 80)
    print("✨ Merge Complete!")
    print("=" * 80)
    print(f"\n💡 Next steps:")
    print(f"   1. guidelines/db_medical_md 삭제")
    print(f"   2. ml-service/db_medical_md 사용")
    
    return final_count

if __name__ == "__main__":
    merge_vectordbs()
