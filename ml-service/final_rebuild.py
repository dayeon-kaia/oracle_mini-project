#!/usr/bin/env python3
"""
VectorDB 최종 재구축 - langchain_chroma 사용
"""
import os, json, shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
PERSIST_DIR, COLLECTION_NAME, HF_MODEL = "./db_medical_md", "medical_md", "BAAI/bge-m3"

# 모든 청크를 한 번에 로드 (이전에 생성한 JSONL 파일들 사용)
def load_all_chunks():
    chunks = []
    files = [
        "protocol_chunks.jsonl",
        "protocol_cards_2_3.jsonl", 
        "protocol_card_4_sepsis.jsonl",
        "protocol_card_5_urine_output.jsonl"
    ]
    for f in files:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                for line in file:
                    chunks.append(json.loads(line))
    return chunks

def rebuild_vectordb():
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    
    chunks = load_all_chunks()
    print(f"✅ Loaded {len(chunks)} chunks from JSONL files")
    
    embeddings = HuggingFaceEmbeddings(model_name=HF_MODEL, model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
    
    documents, ids = [], []
    for chunk in chunks:
        serialized_metadata = {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in chunk["metadata"].items()}
        documents.append(Document(page_content=chunk["text"], metadata=serialized_metadata))
        ids.append(chunk["id"])
    
    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings, collection_name=COLLECTION_NAME, persist_directory=PERSIST_DIR, ids=ids)
    print(f"✅ VectorDB created with {len(chunks)} chunks")
    
    # 검증
    test_queries = ["RR 30 이상", "MAP 65 미만", "패혈증 진단", "소변량 감소"]
    for q in test_queries:
        results = vectorstore.similarity_search(q, k=1, filter={"exclusion_group": ""})
        if results:
            print(f"✓ '{q}' → {results[0].metadata.get('card_id')}")
    print("\n✨ VectorDB rebuild complete!")

if __name__ == "__main__":
    rebuild_vectordb()
