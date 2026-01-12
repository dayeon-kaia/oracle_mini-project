#!/usr/bin/env python3
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = "./db_medical_md"
COLLECTION_NAME = "medical_md"
HF_MODEL = "BAAI/bge-m3"

embeddings = HuggingFaceEmbeddings(model_name=HF_MODEL, model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
vectorstore = Chroma(persist_directory=PERSIST_DIR, collection_name=COLLECTION_NAME, embedding_function=embeddings)

# app.py와 동일한 방식으로 검색
query = "패혈증 lactate 측정"
query_embedding = vectorstore._embedding_function.embed_query(query)
res = vectorstore._collection.query(
    query_embeddings=[query_embedding],
    n_results=8,
    where=None,
    include=["documents", "metadatas", "distances"],
)

print(f"🔍 Query: '{query}'")
print(f"📊 Results count: {len(res['documents'][0]) if res.get('documents') else 0}")

if res.get("documents") and res["documents"][0]:
    for i, (doc, meta) in enumerate(zip(res["documents"][0][:3], res["metadatas"][0][:3])):
        print(f"\n{i+1}. {meta.get('card_id')} / {meta.get('section')}")
        print(f"   {doc[:100]}...")
else:
    print("❌ NO RESULTS")
