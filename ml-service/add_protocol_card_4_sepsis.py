#!/usr/bin/env python3
"""
프로토콜 카드 4 (Sepsis) 추가 임베딩 스크립트
기존 VectorDB에 패혈증 관련 청크 적재
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

def create_sepsis_chunks():
    """프로토콜 카드 4: 패혈증 및 패혈쇼크 초기 대응 청크 생성"""
    chunks = []
    
    # ==================== 프로토콜 카드 1: 패혈증 및 패혈쇼크 ====================
    
    # Chunk 1: Trigger - Sepsis Recognition
    chunks.append({
        "id": "SEPSIS_BUNDLE.Trigger.Sepsis_Recognition.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: Sepsis Recognition

- 감염이 의심되면서 **SOFA가 2점 이상 증가**한 경우 패혈증으로 진단합니다. [2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]
- **스크리닝:** NEWS, MEWS, qSOFA 등의 도구와 함께 머신러닝 예측 모델을 활용하여 조기 인지율을 높일 수 있습니다. [2024 성인 패혈증 초기치료지침서, 요약문, 소스 31, 62]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Trigger",
            "subsection": "Sepsis_Recognition",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care", "infectious_disease"],
            "intended_users": ["clinician"],
            "inputs_required": ["SOFA", "감염징후"],
            "outputs": ["alert", "recommendation"],
            "keywords": ["패혈증", "Sepsis", "SOFA", "SOFA≥2", "감염", "스크리닝", "NEWS", "qSOFA"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]",
                "[2024 성인 패혈증 초기치료지침서, 요약문, 소스 31, 62]"
            ],
            "signals": ["SOFA"],
            "decision_points": ["sepsis_screening"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 2: Trigger - Septic Shock Diagnosis
    chunks.append({
        "id": "SEPSIS_BUNDLE.Trigger.Septic_Shock.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: Septic Shock Diagnosis

- 적절한 수액 소생술 후에도 **MAP 65 mmHg 이상** 유지를 위해 **승압제가 필요한 경우**. [2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]
- 동시에 혈청 **젖산(Lactate) > 2 mmol/L (18 mg/dL)** 인 경우. [2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Trigger",
            "subsection": "Septic_Shock",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["MAP", "Lactate", "승압제사용"],
            "outputs": ["alert"],
            "keywords": ["패혈쇼크", "Septic Shock", "MAP 65", "Lactate>2", "승압제"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]"
            ],
            "signals": ["MAP", "Lactate"],
            "decision_points": ["septic_shock_diagnosis"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 3: Action - Hour-1 Bundle
    chunks.append({
        "id": "SEPSIS_BUNDLE.Action.Hour1_Bundle.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Action
### SUBSECTION: Hour-1 Bundle

- **젖산 측정 및 지표 활용:** 내원 직후 젖산 농도를 측정하며, 수액 소생술의 지표로 ScvO2보다 **젖산 청소율(Lactate clearance)을 우선적으로 사용**할 것을 권고합니다. [2024 성인 패혈증 초기치료지침서, 요약문 및 38쪽, 소스 31, 38, 62, 70]
- **항생제 투여 적기(Time to Antibiotics):**
    - **패혈쇼크:** 인지 후 **1시간 이내** 광범위 항생제 시작. [2024 성인 패혈증 초기치료지침서, 46쪽, 소스 46, 78]
    - **패혈증(쇼크 없음):** 감염 가능성을 신속히 평가 후 인지 후 **3시간 이내** 투여 권고. [2024 성인 패혈증 초기치료지침서]
    - 원칙: 원인균 확인 전 **경험적 광범위 항생제**를 즉시 시작하고, 균 배양 결과에 따라 추후 조정합니다. [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Action",
            "subsection": "Hour1_Bundle",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["Lactate"],
            "outputs": ["recommendation"],
            "keywords": ["Hour-1 Bundle", "젖산청소율", "Lactate clearance", "항생제", "1시간", "3시간", "광범위항생제"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 요약문 및 38쪽, 소스 31, 38, 62, 70]",
                "[2024 성인 패혈증 초기치료지침서, 46쪽, 소스 46, 78]",
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["Lactate"],
            "decision_points": ["antibiotics_timing", "lactate_monitoring"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 4: Action - Fluid Resuscitation
    chunks.append({
        "id": "SEPSIS_BUNDLE.Action.Fluid_Resuscitation.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Action
### SUBSECTION: Fluid Resuscitation

- **초기 투여량:** 저혈압 혹은 저관류(Lactate ≥ 4 mmol/L) 동반 시 **3시간 이내 30 mL/kg 정질액** 투여. [2024 성인 패혈증 초기치료지침서, 요약문 및 40쪽]
- **수액 종류:** 평형정질액(Balanced crystalloids) 또는 0.9% 생리식염수 사용 가능. [2024 성인 패혈증 초기치료지침서]
- **추가 수액 결정:** 정적 지표보다 **동적 지표(Dynamic parameter)**로 수액 반응성 평가. [2024 성인 패혈증 초기치료지침서, 핵심질문 5]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Action",
            "subsection": "Fluid_Resuscitation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["MAP", "Lactate"],
            "outputs": ["recommendation"],
            "keywords": ["수액소생술", "30mL/kg", "정질액", "Lactate≥4", "Dynamic parameter"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 요약문 및 40쪽]",
                "[2024 성인 패혈증 초기치료지침서]",
                "[2024 성인 패혈증 초기치료지침서, 핵심질문 5]"
            ],
            "signals": ["MAP", "Lactate"],
            "decision_points": ["fluid_resuscitation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 5: Action - Vasopressor Strategy
    chunks.append({
        "id": "SEPSIS_BUNDLE.Action.Vasopressor.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Action
### SUBSECTION: Vasopressor Strategy

- **목표 혈압:** **MAP ≥ 65 mmHg** 유지 목표. [2024 성인 패혈증 초기치료지침서, 1]
- **1차 승압제:** **노르에피네프린(Norepinephrine)** 우선 사용. [2024 성인 패혈증 초기치료지침서]
- **승압제 추가 전략:**
    - 노르에피네프린 **0.25~0.5 μg/kg/min** 도달에도 목표 MAP 유지 실패 시, 무조건 증량보다 **바소프레신 추가** 권고. [2024 성인 패혈증 초기치료지침서]
    - 바소프레신 추가 후에도 혈압 유지가 안 되면 **에피네프린 추가** 고려. [2024 성인 패혈증 초기치료지침서]
- **심기능 저하 시:** 심기능 저하와 저관류 동반 패혈쇼크 환자에서 **도부타민(Dobutamine)** 고려. [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Action",
            "subsection": "Vasopressor",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["MAP"],
            "outputs": ["recommendation"],
            "keywords": ["승압제", "노르에피네프린", "Norepinephrine", "MAP 65", "바소프레신", "Vasopressin", "도부타민", "Dobutamine"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 1]",
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["MAP"],
            "decision_points": ["vasopressor_initiation", "vasopressin_addition"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 6: Action - Monitoring
    chunks.append({
        "id": "SEPSIS_BUNDLE.Action.Monitoring.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Action
### SUBSECTION: Monitoring

- **심초음파 시행:** 심장 기능 및 혈역학 상태 확인을 위해 **심장초음파 시행** 권고. [2024 성인 패혈증 초기치료지침서, 요약문 및 35쪽, 소스 35, 67]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Action",
            "subsection": "Monitoring",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["recommendation"],
            "keywords": ["심초음파", "Echocardiography", "혈역학", "모니터링"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 요약문 및 35쪽, 소스 35, 67]"
            ],
            "signals": [],
            "decision_points": ["echocardiography"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 7: Rationale - Vasopressin Addition
    chunks.append({
        "id": "SEPSIS_BUNDLE.Rationale.Vasopressin.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: Rationale
### SUBSECTION: Vasopressin Addition

- **용량 기준:** 노르에피네프린 **0.25~0.5 μg/kg/min** 범위 도달에도 MAP ≥ 65 유지 어려우면, 노르에피네프린 추가 증량 대신 **바소프레신 추가 권고**.
- **최적의 개입 시점:** 노르에피네프린 **0.25 μg/kg/min을 초과**하는 시점에서 바소프레신 추가 고려가 가장 적절.
- **카테콜아민 절약 효과:** catecholamine-sparing effect.
- **생존율 및 예후:** VASST 연구 아군 분석에서 노르에피네프린 **15 μg/min 이하**로 투여받는 환자에서 바소프레신 추가 시 생존율 향상.
- **신장 기능 보호:** 메타분석에서 RRT 필요성 유의한 감소.
[2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "Rationale",
            "subsection": "Vasopressin",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": [],
            "keywords": ["바소프레신", "catecholamine-sparing", "RRT", "생존율", "신장보호"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 8: XAI
    chunks.append({
        "id": "SEPSIS_BUNDLE.XAI.v1",
        "text": """# CARD: 패혈증 및 패혈쇼크 초기 대응 프로토콜
## SECTION: XAI

- "감염이 의심되고 SOFA가 2점 이상 상승해 패혈증 기준에 해당합니다. 젖산 측정 및 젖산 청소율을 중심으로 소생술 반응을 평가하십시오." [2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]
- "수액 소생술 후에도 MAP 65 mmHg 유지에 승압제가 필요하고 젖산이 2 mmol/L 초과하여 패혈쇼크 기준에 해당합니다. 노르에피네프린을 1차로 시작하고 목표 MAP 65 이상을 유지하십시오." [2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]
- "노르에피네프린 용량이 0.25–0.5 μg/kg/min 범위에도 MAP ≥ 65 유지가 어려워 바소프레신 추가를 검토할 시점입니다." [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "SEPSIS_BUNDLE",
            "card_title": "패혈증 및 패혈쇼크 초기 대응 프로토콜",
            "section": "XAI",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["xai_message"],
            "keywords": ["설명", "메시지", "권고"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서, 1쪽, 소스 32, 63]",
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # ==================== 프로토콜 카드 2: Lactate Trend ====================
    
    # Chunk 9: Lactate Trend - Trigger
    chunks.append({
        "id": "LACTATE_TREND.Trigger.v1",
        "text": """# CARD: Lactate 트렌드 기반 치료 반응 평가 프로토콜
## SECTION: Trigger

- **Lactate > 2 mmol/L:** 패혈쇼크 진단 기준의 하나(승압제 필요한 저혈압과 동반 시).
- **Lactate ≥ 4 mmol/L:** 심각한 저관류 신호로 **3시간 이내 30 mL/kg 정질액 투여** 트리거.
[2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "LACTATE_TREND",
            "card_title": "Lactate 트렌드 기반 치료 반응 평가 프로토콜",
            "section": "Trigger",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["Lactate"],
            "outputs": ["alert"],
            "keywords": ["Lactate", "젖산", "Lactate>2", "Lactate≥4", "저관류"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["Lactate"],
            "decision_points": ["lactate_threshold"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 10: Lactate Trend - Analysis
    chunks.append({
        "id": "LACTATE_TREND.Action.Trend_Analysis.v1",
        "text": """# CARD: Lactate 트렌드 기반 치료 반응 평가 프로토콜
## SECTION: Action
### SUBSECTION: Trend Analysis

- 단일 수치보다 **개입 후 2–6시간 이내 하강 추세** 확인이 치료 반응 평가에 중요.
- **하강 추세:** 수액/승압제 효과 및 관류 개선 의미.
- **지속 상승/변화 없음:** 초기 처치 실패로 판단 → 동적 지표 재평가, 추가 수액, 노르에피네프린 용량 조절 및 바소프레신 추가 검토.
[2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "LACTATE_TREND",
            "card_title": "Lactate 트렌드 기반 치료 반응 평가 프로토콜",
            "section": "Action",
            "subsection": "Trend_Analysis",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["Lactate"],
            "outputs": ["recommendation"],
            "keywords": ["Lactate clearance", "젖산청소율", "트렌드", "2-6시간", "치료반응"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["Lactate"],
            "decision_points": ["lactate_clearance_evaluation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 11: Lactate - Lethal Triad
    chunks.append({
        "id": "LACTATE_TREND.Action.Lethal_Triad.v1",
        "text": """# CARD: Lactate 트렌드 기반 치료 반응 평가 프로토콜
## SECTION: Action
### SUBSECTION: Lethal Triad

- **Lactate 상승 + MAP < 65 + Oliguria** 동시 감지 시 즉각적 집중 관리 필요.
[2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "LACTATE_TREND",
            "card_title": "Lactate 트렌드 기반 치료 반응 평가 프로토콜",
            "section": "Action",
            "subsection": "Lethal_Triad",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["Lactate", "MAP", "UO"],
            "outputs": ["alert"],
            "keywords": ["Lethal Triad", "치명적삼합증", "Lactate", "MAP<65", "Oliguria"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["Lactate", "MAP", "UO"],
            "decision_points": ["critical_triad_alert"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 12: Lactate - XAI
    chunks.append({
        "id": "LACTATE_TREND.XAI.v1",
        "text": """# CARD: Lactate 트렌드 기반 치료 반응 평가 프로토콜
## SECTION: XAI

- "젖산이 {lactate}로 상승했고, (MAP {map}) 및 소변량 감소가 동반되어 저관류 위험 조합이 감지되었습니다. 가이드라인에 따라 30 mL/kg 수액 및 승압제 전략을 재평가하십시오." [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "LACTATE_TREND",
            "card_title": "Lactate 트렌드 기반 치료 반응 평가 프로토콜",
            "section": "XAI",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["sepsis", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["xai_message"],
            "keywords": ["설명", "메시지", "권고"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # ==================== 승압제 안전성 모니터링 ====================
    
    # Chunk 13: Norepinephrine Safety - Adverse Effects
    chunks.append({
        "id": "VASOPRESSOR_SAFETY.Action.Adverse_Effects.v1",
        "text": """# CARD: 승압제 안전성: 노르에피네프린 부정맥/부작용 및 모니터링 프로토콜
## SECTION: Action
### SUBSECTION: Adverse Effects

- **주요 부작용:** 노르에피네프린은 말단의 알파 및 베타 아드레날린 수용체에 작용하여 강력한 심근 수축과 혈관 수축을 유발하며, 이 과정에서 **부정맥, 고혈압, 기관 허혈**이 주요 부작용으로 나타날 수 있습니다. [2024 성인 패혈증 초기치료지침서]
- **상대적 위험도:** 노르에피네프린은 도파민과 비교했을 때 **부정맥 발생 위험이 유의하게 낮습니다**(상대위험도 0.48). 도파민은 용량 의존적인 베타-1 활성화로 인해 부정맥 유발 가능성이 더 높은 것으로 보고되었습니다. [2024 성인 패혈증 초기치료지침서]
- **심박수 영향:** 노르에피네프린은 평균동맥압(MAP)을 상승시키면서도 **심박수에는 미미한 영향**을 주는 특성이 있습니다. [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "VASOPRESSOR_SAFETY",
            "card_title": "승압제 안전성: 노르에피네프린 부정맥/부작용 및 모니터링 프로토콜",
            "section": "Action",
            "subsection": "Adverse_Effects",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["alert"],
            "keywords": ["노르에피네프린", "부정맥", "부작용", "도파민", "고혈압", "허혈"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": [],
            "decision_points": ["vasopressor_safety"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 14: Norepinephrine Safety - Monitoring
    chunks.append({
        "id": "VASOPRESSOR_SAFETY.Action.Monitoring.v1",
        "text": """# CARD: 승압제 안전성: 노르에피네프린 부정맥/부작용 및 모니터링 프로토콜
## SECTION: Action
### SUBSECTION: Monitoring Methods

- **지속적 심전도 감시:** 약물 투여에 따른 심장 리듬 변화와 부정맥 발생을 즉각적으로 확인하기 위해 **지속적인 심전도(ECG) 모니터링**이 필수적입니다. [2024 성인 패혈증 초기치료지침서]
- **침습적 혈역학 모니터링:**
    - **동맥내 도관(A-line):** 지속적이고 정확한 혈압 감시를 위해 침습적인 동맥압 측정법이 권장됩니다. [2024 성인 패혈증 초기치료지침서]
    - **중심정맥 카테터:** 심장 기능과 순환 혈액 상태에 대한 정보를 얻기 위해 내목정맥이나 쇄골 아래정맥을 통한 **중심정맥압(CVP) 감시**를 병행할 수 있습니다. [2024 성인 패혈증 초기치료지침서]
- **투여 경로 관리:** 노르에피네프린은 혈관 밖으로 샐 경우 국소 조직의 허혈과 괴사를 유발할 수 있으므로 반드시 **안전한 중심정맥 경로**를 통해 투여해야 합니다. [2024 성인 패혈증 초기치료지침서]
- **포괄적 상태 평가:** 카테콜아민 계열 약물을 사용할 때는 단순히 수치뿐만 아니라 혈압, 산소포화도, 젖산 농도 등을 종합하여 환자의 혈역학적 상태를 파악해야 합니다. [2024 성인 패혈증 초기치료지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "VASOPRESSOR_SAFETY",
            "card_title": "승압제 안전성: 노르에피네프린 부정맥/부작용 및 모니터링 프로토콜",
            "section": "Action",
            "subsection": "Monitoring",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["cardiovascular", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["ECG", "BP"],
            "outputs": ["recommendation"],
            "keywords": ["ECG모니터링", "A-line", "침습적동맥압", "CVP", "중심정맥", "혈역학모니터링"],
            "citations": [
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["ECG", "BP"],
            "decision_points": ["invasive_monitoring"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    return chunks

def add_chunks_to_vectordb(new_chunks):
    """기존 VectorDB에 새 청크 추가"""
    print(f"📝 Adding {len(new_chunks)} new chunks to existing VectorDB...")
    
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
    
    texts = []
    metadatas = []
    ids = []
    
    for chunk in new_chunks:
        texts.append(chunk["text"])
        ids.append(chunk["id"])
        
        serialized_metadata = {}
        for key, value in chunk["metadata"].items():
            if isinstance(value, (list, dict)):
                serialized_metadata[key] = json.dumps(value, ensure_ascii=False)
            else:
                serialized_metadata[key] = value
        metadatas.append(serialized_metadata)
    
    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
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
    
    test_cases = [
        {"query": "패혈증 진단 기준은?", "expected_card": "SEPSIS_BUNDLE"},
        {"query": "항생제는 언제 투여하나요?", "expected_card": "SEPSIS_BUNDLE"},
        {"query": "젖산 청소율이 중요한 이유", "expected_card": "LACTATE_TREND"},
        {"query": "노르에피네프린 부작용은?", "expected_card": "VASOPRESSOR_SAFETY"}
    ]
    
    for test in test_cases:
        results = vectorstore.similarity_search(test["query"], k=2, filter={"exclusion_group": ""})
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
    print("🚀 Adding Protocol Card 4 (Sepsis) to VectorDB")
    print("=" * 80)
    
    print("\n📝 Creating chunks for Protocol Card 4 (Sepsis)...")
    sepsis_chunks = create_sepsis_chunks()
    print(f"✅ Created {len(sepsis_chunks)} chunks")
    print(f"   - SEPSIS_BUNDLE: 8 chunks")
    print(f"   - LACTATE_TREND: 4 chunks")
    print(f"   - VASOPRESSOR_SAFETY: 2 chunks")
    
    add_chunks_to_vectordb(sepsis_chunks)
    verify_additions()
    export_to_jsonl(sepsis_chunks, "protocol_card_4_sepsis.jsonl")
    
    print("\n" + "=" * 80)
    print("✨ Successfully added Protocol Card 4!")
    print("=" * 80)
    print(f"\n💡 Summary:")
    print(f"   - Total new chunks: {len(sepsis_chunks)}")
    print(f"   - Total VectorDB now contains: 31 + {len(sepsis_chunks)} = {31 + len(sepsis_chunks)} chunks")

if __name__ == "__main__":
    main()
