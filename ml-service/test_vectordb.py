#!/usr/bin/env python3
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
vectorstore = Chroma(persist_directory="./db_medical_md", collection_name="medical_md", embedding_function=embeddings)

# 테스트 쿼리 
queries = ["lactate", "패혈증", "젖산", "Lactate 3.1", "젖산 측정"]
for q in queries:
    results = vectorstore.similarity_search(q, k=3)
    print(f"\n🔍 Query: '{q}'")
    if results:
        for i, r in enumerate(results[:2]):
            card = r.metadata.get('card_id', 'unknown')
            section = r.metadata.get('section', 'unknown')
            print(f"   {i+1}. {card} / {section}")
            print(f"      {r.page_content[:80]}...")
    else:
        print("   ❌ No results")
