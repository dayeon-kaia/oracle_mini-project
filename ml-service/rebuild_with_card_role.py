#!/usr/bin/env python3
"""VectorDB 재구축 - enhanced metadata 포함"""
import os, json, shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
PERSIST_DIR, COLLECTION_NAME, HF_MODEL = "./db_medical_md", "medical_md", "BAAI/bge-m3"

def rebuild_with_enhanced_metadata():
    chunks = []
    with open("protocol_chunks_enhanced.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
    
    print(f"✅ Loaded {len(chunks)} enhanced chunks")
    
    embeddings = HuggingFaceEmbeddings(model_name=HF_MODEL, model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
    
    documents, ids = [], []
    for chunk in chunks:
        serialized_metadata = {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in chunk["metadata"].items()}
        documents.append(Document(page_content=chunk["text"], metadata=serialized_metadata))
        ids.append(chunk["id"])
    
    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings, collection_name=COLLECTION_NAME, persist_directory=PERSIST_DIR, ids=ids)
    print(f"✅ VectorDB created with {len(chunks)} chunks")
    
    # 검증
    test_queries = [
        ("MAP 60 저혈압", {"card_role": "ACTION"}),
        ("Lactate 상승", {"card_role": "TRIGGER"}),
    ]
    
    for query, expected_meta in test_queries:
        results = vectorstore.similarity_search(query, k=1)
        if results:
            actual_role = results[0].metadata.get('card_role')
            print(f"✓ '{query}' → {actual_role}")
    
    print("\n✨ VectorDB rebuild complete with card_role metadata!")

if __name__ == "__main__":
    rebuild_with_enhanced_metadata()
