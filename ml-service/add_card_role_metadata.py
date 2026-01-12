#!/usr/bin/env python3
"""
기존 청크에 card_role, bundle, urgency_compatible 메타데이터 추가
"""
import os
import json
from pathlib import Path

def load_all_chunks():
    """Load all chunks from JSONL files"""
    chunks = []
    jsonl_files = [
        "protocol_chunks.jsonl",
        "protocol_cards_2_3.jsonl",
        "protocol_card_4_sepsis.jsonl",
        "protocol_card_5_urine_output.jsonl"
    ]
    
    for filename in jsonl_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    chunks.append(json.loads(line))
    
    return chunks

def determine_card_role(metadata: dict) -> str:
    """Determine card_role from section"""
    section = metadata.get("section", "")
    card_id = metadata.get("card_id", "")
    
    if section == "Trigger":
        return "TRIGGER"
    elif section == "Action":
        return "ACTION"
    elif section == "Rationale":
        return "RATIONALE"
    elif section == "XAI":
        return "MONITORING"
    elif section == "Exceptions":
        return "ADVERSE_EFFECT"
    elif "SAFETY" in card_id:
        return "ADVERSE_EFFECT"
    else:
        return "RATIONALE"  # default

def determine_bundles(card_id: str) -> list:
    """Determine bundle tags from card_id"""
    bundles = []
    
    if "RESP" in card_id or "ARDS" in card_id or "O2" in card_id:
        bundles.append("RESPIRATORY")
    
    if "SHOCK" in card_id:
        bundles.extend(["SHOCK", "SEPSIS"])
    
    if "SEPSIS" in card_id or "LACTATE" in card_id:
        bundles.append("SEPSIS")
    
    if "AKI" in card_id or "DIURETIC" in card_id:
        bundles.append("AKI")
    
    if "HTN" in card_id:
        bundles.append("HTN")
    
    if "VASOPRESSOR" in card_id:
        bundles.extend(["SHOCK", "SEPSIS"])
    
    return list(set(bundles))

def determine_urgency_compatible(card_role: str) -> list:
    """Determine which urgency levels this card should appear in"""
    if card_role in ["ACTION", "TRIGGER"]:
        return ["STAT", "URGENT", "ROUTINE"]
    elif card_role == "ADVERSE_EFFECT":
        return ["ROUTINE"]  # 기본 비활성, 의사 클릭 시만
    else:
        return ["URGENT", "ROUTINE"]

def add_metadata_to_chunks(chunks: list) -> list:
    """Add card_role, bundle, urgency_compatible to all chunks"""
    enhanced_chunks = []
    
    for chunk in chunks:
        meta = chunk["metadata"]
        
        # Add card_role
        meta["card_role"] = determine_card_role(meta)
        
        # Add bundle
        meta["bundle"] = determine_bundles(meta.get("card_id", ""))
        
        # Add urgency_compatible
        meta["urgency_compatible"] = determine_urgency_compatible(meta["card_role"])
        
        enhanced_chunks.append(chunk)
    
    return enhanced_chunks

def export_enhanced_chunks(chunks: list, output_file: str):
    """Export enhanced chunks to JSONL"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            json.dump(chunk, f, ensure_ascii=False)
            f.write('\n')

def main():
    print("=" * 80)
    print("🔧 Adding card_role metadata to chunks")
    print("=" * 80)
    
    # Load existing chunks
    chunks = load_all_chunks()
    print(f"\n✅ Loaded {len(chunks)} chunks")
    
    # Add metadata
    enhanced_chunks = add_metadata_to_chunks(chunks)
    print(f"✅ Added card_role, bundle, urgency_compatible metadata")
    
    # Analyze distribution
    role_counts = {}
    bundle_counts = {}
    
    for chunk in enhanced_chunks:
        role = chunk["metadata"]["card_role"]
        role_counts[role] = role_counts.get(role, 0) + 1
        
        for bundle in chunk["metadata"]["bundle"]:
            bundle_counts[bundle] = bundle_counts.get(bundle, 0) + 1
    
    print("\n📊 card_role Distribution:")
    for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"   {role}: {count} chunks")
    
    print("\n📊 Bundle Distribution:")
    for bundle, count in sorted(bundle_counts.items(), key=lambda x: -x[1]):
        print(f"   {bundle}: {count} chunks")
    
    # Export
    output_file = "protocol_chunks_enhanced.jsonl"
    export_enhanced_chunks(enhanced_chunks, output_file)
    print(f"\n✅ Exported to {output_file}")
    
    # Show sample
    print("\n📝 Sample chunk metadata:")
    sample = enhanced_chunks[0]["metadata"]
    print(f"   card_id: {sample.get('card_id')}")
    print(f"   section: {sample.get('section')}")
    print(f"   card_role: {sample.get('card_role')}")
    print(f"   bundle: {sample.get('bundle')}")
    print(f"   urgency_compatible: {sample.get('urgency_compatible')}")
    
    print("\n" + "=" * 80)
    print("✨ Metadata enhancement complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
