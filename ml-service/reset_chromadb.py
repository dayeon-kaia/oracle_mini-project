#!/usr/bin/env python3
"""
ChromaDB 리셋 스크립트
기존 VectorDB를 백업하고 초기화
"""

import os
import shutil
from datetime import datetime

PERSIST_DIR = "./db_medical_md"
BACKUP_DIR = "./db_medical_md_backup"

def reset_chromadb():
    """ChromaDB 디렉토리를 백업하고 리셋"""
    
    print("=" * 60)
    print("ChromaDB 리셋")
    print("=" * 60)
    
    # 백업 디렉토리 생성
    if os.path.exists(PERSIST_DIR):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{BACKUP_DIR}_{timestamp}"
        
        print(f"\n📦 기존 DB 백업 중...")
        print(f"   {PERSIST_DIR} → {backup_path}")
        shutil.copytree(PERSIST_DIR, backup_path)
        print(f"✓ 백업 완료: {backup_path}")
        
        # 기존 디렉토리 삭제
        print(f"\n🗑️  기존 DB 삭제 중...")
        shutil.rmtree(PERSIST_DIR)
        print(f"✓ 삭제 완료: {PERSIST_DIR}")
    else:
        print(f"\n⚠️  기존 DB가 없습니다: {PERSIST_DIR}")
    
    # 새 디렉토리 생성
    print(f"\n📁 새 DB 디렉토리 생성...")
    os.makedirs(PERSIST_DIR, exist_ok=True)
    print(f"✓ 생성 완료: {PERSIST_DIR}")
    
    print(f"\n✅ ChromaDB 리셋 완료!")
    print(f"   백업: {backup_path if os.path.exists(PERSIST_DIR) else 'N/A'}")
    print(f"   현재: {PERSIST_DIR} (비어있음)")

if __name__ == "__main__":
    reset_chromadb()
