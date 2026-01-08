
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

HF_MODEL = "BAAI/bge-m3"
embeddings = HuggingFaceEmbeddings(model_name=HF_MODEL)

db_paths = [
    "/home/hykim/projects/mimic_dev/ml-service/db_medical_md",
    "/home/hykim/projects/mimic_dev/ml-service/guidelines/db_medical_md"
]

for path in db_paths:
    print(f"--- Checking DB at: {path} ---")
    if not os.path.exists(path):
        print("Path does not exist")
        continue
        
    try:
        db = Chroma(
            persist_directory=path,
            collection_name="medical_md",
            embedding_function=embeddings
        )
        count = db._collection.count()
        print(f"Document count: {count}")
        
        # Check bundle distribution if possible
        if count > 0:
            docs = db._collection.get(include=["metadatas"])
            bundles = {}
            for m in docs["metadatas"]:
                b_str = m.get("bundle", "[]")
                # simplify for display
                bundles[b_str] = bundles.get(b_str, 0) + 1
            print("Bundle distribution:")
            for b, c in bundles.items():
                print(f"  {b}: {c}")
                
    except Exception as e:
        print(f"Error loading DB: {e}")
    print("\n")
