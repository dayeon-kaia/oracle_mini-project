#!/usr/bin/env python3
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
vectorstore = Chroma(persist_directory="./db_medical_md", collection_name="medical_md", embedding_function=embeddings)

# SEPSIS_STEP_QUERIES에서 가져온 쿼리들 테스트
queries = [
    "패혈증 초기 번들 lactate 측정 재측정",
    "패혈증 blood culture 항생제 투여 1시간",
    "패혈증 30 ml/kg crystalloid 3시간",
    "패혈증 MAP 65 norepinephrine 승압제",
]

for q in queries:
    query_embedding = vectorstore._embedding_function.embed_query(q)
    res = vectorstore._collection.query(
        query_embeddings=[query_embedding],
        n_results=4,
        where=None,
        include=["documents", "metadatas", "distances"],
    )
    print(f"\n🔍 '{q}'")
    if res["documents"] and res["documents"][0]:
        print(f"   ✅ {len(res['documents'][0])} results")
        print(f"   Top: {res['metadatas'][0][0].get('card_id')}")
    else:
        print("   ❌ NO RESULTS")
