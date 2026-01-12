#!/usr/bin/env python3
"""
VectorDB 재구축 스크립트
- 기존 VectorDB 삭제
- 프로토콜 카드 1 (호흡) 임베딩
- ChromaDB에 적재
"""

import os
import shutil
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 설정
PERSIST_DIR = os.getenv("PERSIST_DIR", "./db_medical_md")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_md")
HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")
GUIDELINE_PATH = "./guidelines/프로토콜 카드 1 - 호흡 2e00e84c442f804281f8cdce151000c1.md"

def delete_vectordb():
    """기존 VectorDB 삭제"""
    if os.path.exists(PERSIST_DIR):
        print(f"🗑️  Deleting existing VectorDB at {PERSIST_DIR}...")
        shutil.rmtree(PERSIST_DIR)
        print("✅ VectorDB deleted successfully")
    else:
        print("⚠️  No existing VectorDB found")

def load_and_split_document():
    """마크다운 문서를 헤더 기반으로 분할"""
    print(f"📄 Loading document: {GUIDELINE_PATH}")
    
    # 마크다운 헤더 기반 분할
    headers_to_split_on = [
        ("#", "프로토콜카드"),
        ("##", "섹션"),
        ("###", "서브섹션"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    
    with open(GUIDELINE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    docs = markdown_splitter.split_text(content)
    print(f"✅ Split into {len(docs)} chunks")
    
    # 메타데이터 추가
    for i, doc in enumerate(docs):
        doc.metadata['source'] = 'protocol_card_1_respiratory'
        doc.metadata['topic'] = 'respiratory'
        doc.metadata['chunk_id'] = i
        doc.metadata['file'] = GUIDELINE_PATH
        
        # 프로토콜 카드 번호 추출 (헤더에서)
        if '프로토콜 카드' in doc.page_content[:100]:
            if '카드 1' in doc.page_content[:100]:
                doc.metadata['card_number'] = 1
            elif '카드 2' in doc.page_content[:100]:
                doc.metadata['card_number'] = 2
            elif '카드 3' in doc.page_content[:100]:
                doc.metadata['card_number'] = 3
    
    return docs

def create_vectordb(docs):
    """VectorDB 생성 및 문서 임베딩"""
    print(f"🔧 Creating VectorDB with {HF_MODEL}...")
    
    # HuggingFace 임베딩 모델 초기화
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # ChromaDB 생성 및 문서 추가
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR
    )
    
    print(f"✅ VectorDB created at {PERSIST_DIR}")
    print(f"📊 Total documents embedded: {len(docs)}")
    
    return vectorstore

def verify_vectordb():
    """VectorDB 검증"""
    print("\n🔍 Verifying VectorDB...")
    
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
    test_queries = [
        "RR이 30 이상일 때 어떻게 해야 하나요?",
        "NIV 적용 기준은?",
        "ARDS 중증도 분류는?",
        "복와위는 언제 하나요?"
    ]
    
    for query in test_queries:
        results = vectorstore.similarity_search(query, k=2)
        print(f"\n📝 Query: {query}")
        if results:
            print(f"   Top result: {results[0].page_content[:100]}...")
            print(f"   Metadata: {results[0].metadata}")
    
    print("\n✅ Verification complete")

def main():
    print("=" * 60)
    print("🚀 VectorDB Rebuild Script")
    print("=" * 60)
    
    # 1. 기존 DB 삭제
    delete_vectordb()
    
    # 2. 문서 로드 및 분할
    docs = load_and_split_document()
    
    # 3. VectorDB 생성
    vectorstore = create_vectordb(docs)
    
    # 4. 검증
    verify_vectordb()
    
    print("\n" + "=" * 60)
    print("✨ VectorDB rebuild completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
