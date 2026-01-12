#!/usr/bin/env python3
"""
프로토콜 카드 2(저혈압), 3(고혈압) 추가 임베딩 스크립트
기존 VectorDB에 추가 청크 적재
"""

import os
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# 설정
PERSIST_DIR = os.getenv("PERSIST_DIR", "./db_medical_md")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_md")
HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")

def create_hypotension_chunks():
    """프로토콜 카드 2: 저혈압 및 쇼크 초기 대응 청크 생성"""
    chunks = []
    
    # Chunk 1: Trigger - Shock Suspicion
    chunks.append({
        "id": "SHOCK_BUNDLE.Trigger.Initial_Suspicion.v1",
        "text": """# CARD: 저혈압 및 쇼크 초기 대응 통합 프로토콜 (Shock Bundle)
## SECTION: Trigger
### SUBSECTION: Initial Suspicion

다음 지표 중 **하나 이상**이 감지되면 쇼크 가능성을 인지하고 즉시 평가를 시작합니다.

- **MAP 하락:** 평균동맥압(MAP) < **65 mmHg** 지속. [2024 성인 패혈증 초기치료지침서]
- **고젖산혈증:** 혈청 젖산(Lactate) ≥ **4 mmol/L**. [2024 성인 패혈증 초기치료지침서, 2021 SSC 가이드라인]
- **소변량 감소(Oliguria):** < **0.5 mL/kg/h**가 **2시간 이상 지속**. [2020년 한국심폐소생술 가이드라인, Early Deterioration Command Center 기획서]
- **감염 의심 징후:** 체온 상승과 함께 RR > **22회/분** 동반. [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SHOCK_BUNDLE",
            "card_title": "저혈압 및 쇼크 초기 대응 통합 프로토콜 (Shock Bundle)",
            "section": "Trigger",
            "subsection": "Initial_Suspicion",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care", "sepsis"],
            "intended_users": ["clinician"],
            "inputs_required": ["MAP", "Lactate", "UO", "Temp", "RR"],
            "outputs": ["alert", "recommendation"],
            "keywords": ["쇼크", "저혈압", "MAP<65", "고젖산혈증", "Lactate≥4", "소변량감소", "Oliguria"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]",
                "[2021 SSC 가이드라인]",
                "[2020년 한국심폐소생술 가이드라인]",
                "[Early Deterioration Command Center 기획서]"
            ],
            "signals": ["MAP", "Lactate", "UO", "Temp", "RR"],
            "decision_points": ["shock_screening"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 2: Action - Fluid Resuscitation
    chunks.append({
        "id": "SHOCK_BUNDLE.Action.Fluid_Resuscitation.v1",
        "text": """# CARD: 저혈압 및 쇼크 초기 대응 통합 프로토콜
## SECTION: Action
### SUBSECTION: Fluid Resuscitation (3시간 묶음)

- **수액 투여:** 최소 **30 mL/kg 정질액(crystalloid)** 정맥 투여. [2021 SSC 가이드라인, 2024 성인 패혈증 초기치료지침서]
- **재평가 원칙(Dynamic measures):** 추가 수액 필요성은 **PLR, 심박출량 변화, 맥압 변이(PPV)** 등 **동적 지표**로 판단하며, 혈압 수치만 보고 과다 투여하지 않도록 주의. [2021 SSC 가이드라인, 2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SHOCK_BUNDLE",
            "card_title": "저혈압 및 쇼크 초기 대응 통합 프로토콜",
            "section": "Action",
            "subsection": "Fluid_Resuscitation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care", "sepsis"],
            "intended_users": ["clinician"],
            "inputs_required": ["체중"],
            "outputs": ["recommendation"],
            "keywords": ["수액소생술", "30mL/kg", "정질액", "crystalloid", "Dynamic measures", "PLR", "PPV"],
            "citations": [
                "[2021 SSC 가이드라인]",
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": [],
            "decision_points": ["fluid_resuscitation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 3: Action - Vasopressor Strategy
    chunks.append({
        "id": "SHOCK_BUNDLE.Action.Vasopressor.v1",
        "text": """# CARD: 저혈압 및 쇼크 초기 대응 통합 프로토콜
## SECTION: Action
### SUBSECTION: Vasopressor Strategy

- **1차 약제 – 노르에피네프린 시작:** 수액 투여 중 또는 투여 후에도 **MAP < 65 mmHg** 지속 시, 중심정맥관을 기다리지 말고 **말초정맥을 통해서라도 조기 투여** 시작. [2024 성인 패혈증 초기치료지침서, 2021 SSC 가이드라인]
- **병용 요법 전환 – 바소프레신 추가:** 노르에피네프린 용량이 **0.25~0.5 μg/kg/min**에 도달했음에도 목표 MAP 유지 실패 시 바소프레신 추가 고려. [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SHOCK_BUNDLE",
            "card_title": "저혈압 및 쇼크 초기 대응 통합 프로토콜",
            "section": "Action",
            "subsection": "Vasopressor",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care", "sepsis"],
            "intended_users": ["clinician"],
            "inputs_required": ["MAP"],
            "outputs": ["recommendation"],
            "keywords": ["승압제", "노르에피네프린", "Norepinephrine", "바소프레신", "Vasopressin", "MAP 65", "말초정맥"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]",
                "[2021 SSC 가이드라인]"
            ],
            "signals": ["MAP"],
            "decision_points": ["start_vasopressor", "vasopressin_addition"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 4: Action - HTN Management During Shock
    chunks.append({
        "id": "SHOCK_BUNDLE.Action.HTN_Management.v1",
        "text": """# CARD: 저혈압 및 쇼크 초기 대응 통합 프로토콜
## SECTION: Action
### SUBSECTION: HTN Management

※ 이 섹션은 쇼크 치료 중 또는 기저 심혈관 질환 환자에서 발생 가능한 고혈압 관리를 다룸

- **심부전 환자의 고혈압 치료 시작 기준:** 혈압 ≥ **140/90 mmHg** → 약물 치료 권고. [2022 대한심부전학회 심부전 진료지침]
- **목표 혈압:** 수축기 혈압 **120–130 mmHg** 범위 유지가 예후 개선에 도움. [2022 대한심부전학회 심부전 진료지침]
- **급성 고혈압성 심부전:** 초기 수 시간 동안 **혈압 강하 폭 ≤ 25%**로 제한. [2022 대한심부전학회 심부전 진료지침]
- **승압제 투여 중 고혈압 부작용 모니터링:** 과용량 시 심한 고혈압·빈맥성 부정맥 위험 → **침습적 동맥압 + 심전도 지속 모니터링 필수**. [2024 성인 패혈증 초기치료지침서, 2020년 한국심폐소생술 가이드라인]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SHOCK_BUNDLE",
            "card_title": "저혈압 및 쇼크 초기 대응 통합 프로토콜",
            "section": "Action",
            "subsection": "HTN_Management",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["BP"],
            "outputs": ["recommendation"],
            "keywords": ["고혈압", "심부전", "140/90", "120-130", "혈압강하 25%", "침습적동맥압", "부정맥"],
            "citations": [
                "[2022 대한심부전학회 심부전 진료지침]",
                "[2024 성인 패혈증 초기치료지침서]",
                "[2020년 한국심폐소생술 가이드라인]"
            ],
            "signals": ["BP"],
            "decision_points": ["htn_treatment", "invasive_monitoring"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 5: Rationale
    chunks.append({
        "id": "SHOCK_BUNDLE.Rationale.v1",
        "text": """# CARD: 저혈압 및 쇼크 초기 대응 통합 프로토콜
## SECTION: Rationale

- **MAP ≥ 65 mmHg**는 뇌·심장·신장 관류를 위한 최소 압력 목표. [2024 성인 패혈증 초기치료지침서]
- 그러나 혈압이 정상화되어도 **조직 저관류는 지속**될 수 있으므로, **젖산 감소(Lactate clearance)**와 **소변량 회복**을 함께 확인해야 소생술 성공 여부를 판단 가능. [2024 성인 패혈증 초기치료지침서, 2020년 한국심폐소생술 가이드라인]
- 바소프레신 병용은 **catecholamine-sparing effect**를 제공하며, 메타분석에서 **RRT 필요성 감소 효과**가 확인됨. [2021 Surviving_Sepsis_Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SHOCK_BUNDLE",
            "card_title": "저혈압 및 쇼크 초기 대응 통합 프로토콜",
            "section": "Rationale",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": [],
            "keywords": ["MAP 65", "조직관류", "젖산감소", "바소프레신", "RRT"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]",
                "[2020년 한국심폐소생술 가이드라인]",
                "[2021 Surviving_Sepsis_Campaign]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 6: XAI
    chunks.append({
        "id": "SHOCK_BUNDLE.XAI.v1",
        "text": """# CARD: 저혈압 및 쇼크 초기 대응 통합 프로토콜
## SECTION: XAI

- "MAP이 **65 mmHg 미만**으로 지속되고 젖산이 **{lactate} mmol/L**로 상승해 쇼크가 의심됩니다. 가이드라인에 따라 수액 30 mL/kg 투여 및 조기 노르에피네프린 시작을 권고합니다." [2024 성인 패혈증 초기치료지침서, 2021 SSC 가이드라인]
- "노르에피네프린 용량이 **0.25 μg/kg/min** 이상임에도 혈압 유지가 불안정하여 바소프레신 병용을 고려할 시점입니다." [2024 성인 패혈증 초기치료지침서, 2021 Surviving_Sepsis_Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SHOCK_BUNDLE",
            "card_title": "저혈압 및 쇼크 초기 대응 통합 프로토콜",
            "section": "XAI",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["xai_message"],
            "keywords": ["설명", "메시지", "권고"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]",
                "[2021 SSC 가이드라인]",
                "[2021 Surviving_Sepsis_Campaign]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    return chunks

def create_hypertension_chunks():
    """프로토콜 카드 3: 고혈압 및 급성 혈압 상승 대응 청크 생성"""
    chunks = []
    
    # Chunk 1: Trigger - Chronic HTN
    chunks.append({
        "id": "HTN_BUNDLE.Trigger.Chronic_HTN.v1",
        "text": """# CARD: 고혈압 및 급성 혈압 상승 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: Chronic HTN Recognition

- **심부전 환자에서 고혈압:** 좌심실 박출률과 관계없이 혈압이 **140/90 mmHg 이상**인 경우. [2022 대한심부전학회 심부전 진료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "HTN_BUNDLE",
            "card_title": "고혈압 및 급성 혈압 상승 대응 프로토콜",
            "section": "Trigger",
            "subsection": "Chronic_HTN",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["BP"],
            "outputs": ["alert"],
            "keywords": ["고혈압", "심부전", "140/90", "만성고혈압"],
            "citations": [
                "[2022 대한심부전학회 심부전 진료지침]"
            ],
            "signals": ["BP"],
            "decision_points": ["htn_recognition"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 2: Trigger - Acute BP Elevation
    chunks.append({
        "id": "HTN_BUNDLE.Trigger.Acute_Elevation.v1",
        "text": """# CARD: 고혈압 및 급성 혈압 상승 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: Acute BP Elevation

- **급성 고혈압성 심부전 의심:** 급격한 혈압 상승과 함께 호흡곤란, 폐울혈 등 임상 악화 동반 시. [2022 대한심부전학회 심부전 진료지침]
- **약물 유발 고혈압 위험 (승압제 투여 중):** 노르에피네프린·에피네프린 사용 중 혈압이 과도하게 상승하는 경우. [2020년 한국심폐소생술 가이드라인]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "HTN_BUNDLE",
            "card_title": "고혈압 및 급성 혈압 상승 대응 프로토콜",
            "section": "Trigger",
            "subsection": "Acute_Elevation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["BP", "승압제용량"],
            "outputs": ["alert"],
            "keywords": ["급성고혈압", "고혈압성심부전", "승압제부작용", "호흡곤란", "폐울혈"],
            "citations": [
                "[2022 대한심부전학회 심부전 진료지침]",
                "[2020년 한국심폐소생술 가이드라인]"
            ],
            "signals": ["BP"],
            "decision_points": ["acute_htn_recognition"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 3: Action - Chronic HF HTN Management
    chunks.append({
        "id": "HTN_BUNDLE.Action.Chronic_Management.v1",
        "text": """# CARD: 고혈압 및 급성 혈압 상승 대응 프로토콜
## SECTION: Action
### SUBSECTION: Chronic HF HTN Management

- **치료 시작 기준:** 혈압 **≥ 140/90 mmHg** → 약물 치료 권고. [2022 대한심부전학회 심부전 진료지침]
- **목표 혈압:** 수축기 혈압 **120–130 mmHg 범위**로 조절. [2022 대한심부전학회 심부전 진료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "HTN_BUNDLE",
            "card_title": "고혈압 및 급성 혈압 상승 대응 프로토콜",
            "section": "Action",
            "subsection": "Chronic_Management",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular"],
            "intended_users": ["clinician"],
            "inputs_required": ["BP"],
            "outputs": ["recommendation"],
            "keywords": ["혈압목표", "120-130", "140/90", "약물치료"],
            "citations": [
                "[2022 대한심부전학회 심부전 진료지침]"
            ],
            "signals": ["BP"],
            "decision_points": ["htn_treatment"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 4: Action - Acute HTN HF Management
    chunks.append({
        "id": "HTN_BUNDLE.Action.Acute_Management.v1",
        "text": """# CARD: 고혈압 및 급성 혈압 상승 대응 프로토콜
## SECTION: Action
### SUBSECTION: Acute HTN HF Management

- **감압 원칙:** 급격한 혈압 저하는 장기 관류 저하를 유발할 수 있으므로, **초기 수 시간 동안 혈압 강하 폭을 25% 이내로 제한**. [2022 대한심부전학회 심부전 진료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "HTN_BUNDLE",
            "card_title": "고혈압 및 급성 혈압 상승 대응 프로토콜",
            "section": "Action",
            "subsection": "Acute_Management",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["BP"],
            "outputs": ["recommendation"],
            "keywords": ["급성고혈압", "혈압강하", "25%제한", "감압원칙"],
            "citations": [
                "[2022 대한심부전학회 심부전 진료지침]"
            ],
            "signals": ["BP"],
            "decision_points": ["controlled_bp_reduction"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 5: Action - Vasopressor HTN Monitoring
    chunks.append({
        "id": "HTN_BUNDLE.Action.Vasopressor_Monitoring.v1",
        "text": """# CARD: 고혈압 및 급성 혈압 상승 대응 프로토콜
## SECTION: Action
### SUBSECTION: Vasopressor HTN Monitoring

- **부작용 모니터링:** 노르에피네프린, 에피네프린 등 강력한 혈관수축제 과용량 시 **심한 고혈압 및 빈맥성 부정맥** 발생 가능. [2020년 한국심폐소생술 가이드라인]
- **필수 모니터링:**
    - 침습적 동맥 카테터를 통한 **지속적 혈압 감시**
    - **심전도(ECG) 모니터링** 병행
    [2024 성인 패혈증 초기치료지침서, 2020년 한국심폐소생술 가이드라인]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "HTN_BUNDLE",
            "card_title": "고혈압 및 급성 혈압 상승 대응 프로토콜",
            "section": "Action",
            "subsection": "Vasopressor_Monitoring",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["BP", "ECG"],
            "outputs": ["recommendation"],
            "keywords": ["승압제부작용", "침습적동맥압", "ECG모니터링", "부정맥", "고혈압"],
            "citations": [
                "[2020년 한국심폐소생술 가이드라인]",
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["BP", "ECG"],
            "decision_points": ["invasive_monitoring"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 6: XAI
    chunks.append({
        "id": "HTN_BUNDLE.XAI.v1",
        "text": """# CARD: 고혈압 및 급성 혈압 상승 대응 프로토콜
## SECTION: XAI

- "현재 혈압이 **140/90 mmHg 이상**으로, 심부전 환자에서 치료가 필요한 고혈압 범위에 해당합니다. 가이드라인에 따라 약물 치료 및 목표 수축기 혈압 120–130 mmHg 유지를 권고합니다." [2022 대한심부전학회 심부전 진료지침]
- "급성 고혈압성 심부전이 의심되어, 장기 관류 저하를 피하기 위해 초기 수 시간 동안 혈압 강하 폭을 25% 이내로 제한해야 합니다." [2022 대한심부전학회 심부전 진료지침]
- "승압제 투여 중 혈압이 과도하게 상승하고 있어, 고혈압 및 부정맥 부작용 감시를 위해 침습적 혈압 및 심전도 모니터링이 필요합니다." [2020년 한국심폐소생술 가이드라인]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "HTN_BUNDLE",
            "card_title": "고혈압 및 급성 혈압 상승 대응 프로토콜",
            "section": "XAI",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["xai_message"],
            "keywords": ["설명", "메시지", "권고"],
            "citations": [
                "[2022 대한심부전학회 심부전 진료지침]",
                "[2020년 한국심폐소생술 가이드라인]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    return chunks

def add_chunks_to_vectordb(new_chunks):
    """기존 VectorDB에 새 청크 추가"""
    print(f"📝 Adding {len(new_chunks)} new chunks to existing VectorDB...")
    
    # HuggingFace 임베딩 모델
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # 기존 VectorDB 로드
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    
    # 새 청크 준비 (메타데이터 직렬화)
    texts = []
    metadatas = []
    ids = []
    
    for chunk in new_chunks:
        texts.append(chunk["text"])
        ids.append(chunk["id"])
        
        # ChromaDB용 메타데이터 직렬화
        serialized_metadata = {}
        for key, value in chunk["metadata"].items():
            if isinstance(value, (list, dict)):
                serialized_metadata[key] = json.dumps(value, ensure_ascii=False)
            else:
                serialized_metadata[key] = value
        metadatas.append(serialized_metadata)
    
    # VectorDB에 추가
    vectorstore.add_texts(
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Successfully added {len(new_chunks)} chunks")
    
    return vectorstore

def verify_additions():
    """추가된 청크 검증"""
    print("\n🔍 Verifying new chunks...")
    
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
    test_cases = [
        {
            "query": "MAP이 65 미만일 때 어떻게 하나요?",
            "expected_card": "SHOCK_BUNDLE"
        },
        {
            "query": "노르에피네프린 용량은?",
            "expected_card": "SHOCK_BUNDLE"
        },
        {
            "query": "심부전 환자의 고혈압 목표는?",
            "expected_card": "HTN_BUNDLE"
        },
        {
            "query": "급성 고혈압성 심부전 혈압 강하 속도",
            "expected_card": "HTN_BUNDLE"
        }
    ]
    
    for test in test_cases:
        results = vectorstore.similarity_search(
            test["query"], 
            k=2,
            filter={"exclusion_group": ""}
        )
        print(f"\n📝 Query: {test['query']}")
        if results:
            actual_card = results[0].metadata.get('card_id')
            print(f"   Expected: {test['expected_card']}, Got: {actual_card}")
            print(f"   Section: {results[0].metadata.get('section')}")
            print(f"   Match: {'✓' if actual_card == test['expected_card'] else '✗'}")
    
    print("\n✅ Verification complete")

def export_to_jsonl(chunks, filename):
    """JSONL로 내보내기"""
    print(f"\n📤 Exporting chunks to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            json.dump(chunk, f, ensure_ascii=False)
            f.write('\n')
    print(f"✅ Exported to {filename}")

def main():
    print("=" * 80)
    print("🚀 Adding Protocol Cards 2-3 to VectorDB")
    print("=" * 80)
    
    # 1. 새 청크 생성
    print("\n📝 Creating chunks for Protocol Card 2 (저혈압)...")
    shock_chunks = create_hypotension_chunks()
    print(f"✅ Created {len(shock_chunks)} chunks for SHOCK_BUNDLE")
    
    print("\n📝 Creating chunks for Protocol Card 3 (고혈압)...")
    htn_chunks = create_hypertension_chunks()
    print(f"✅ Created {len(htn_chunks)} chunks for HTN_BUNDLE")
    
    all_new_chunks = shock_chunks + htn_chunks
    print(f"\n✅ Total new chunks: {len(all_new_chunks)}")
    
    # 2. VectorDB에 추가
    vectorstore = add_chunks_to_vectordb(all_new_chunks)
    
    # 3. 검증
    verify_additions()
    
    # 4. JSONL 내보내기
    export_to_jsonl(all_new_chunks, "protocol_cards_2_3.jsonl")
    
    print("\n" + "=" * 80)
    print("✨ Successfully added Protocol Cards 2-3!")
    print("=" * 80)
    print(f"\n💡 Summary:")
    print(f"   - SHOCK_BUNDLE: {len(shock_chunks)} chunks")
    print(f"   - HTN_BUNDLE: {len(htn_chunks)} chunks")
    print(f"   - Total VectorDB now contains: 19 + {len(all_new_chunks)} = {19 + len(all_new_chunks)} chunks")

if __name__ == "__main__":
    main()
