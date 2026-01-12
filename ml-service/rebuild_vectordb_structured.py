#!/usr/bin/env python3
"""
프로토콜 카드 1 구조화 청킹 및 VectorDB 적재 스크립트
chunk.md 방법론에 따른 구조화 청킹 구현
"""

import os
import shutil
import json
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# 설정
PERSIST_DIR = os.getenv("PERSIST_DIR", "./db_medical_md")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_md")
HF_MODEL = os.getenv("HF_MODEL", "BAAI/bge-m3")

def create_chunks():
    """프로토콜 카드 1의 구조화된 청크 생성 (chunk.md 방법론 준수)"""
    chunks = []
    
    # ==================== 프로토콜 카드 1: 호흡곤란 악화 대응 ====================
    
    # Chunk 1: Trigger - Core
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.Trigger.Core.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)
## SECTION: Trigger
### SUBSECTION: Core

- **빈호흡:** RR **> 25–30/min** 지속 상승. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
- **산소화 저하:** SpO₂가 목표 범위 아래로 하락. [2020년 한국심폐소생술 가이드라인]
- **FiO₂ 요구량 증가:** 동일 SpO₂ 유지를 위해 FiO₂를 계속 올려야 하는 상황. [Early Deterioration Command Center 기획서]
- (시스템 동작) 위 변화를 실시간 감지하여 ARDS 진행 전 '호흡곤란 악화' 경보 생성. [Early Deterioration Command Center 기획서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)",
            "section": "Trigger",
            "subsection": "Core",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["RR", "SpO2", "FiO2"],
            "outputs": ["alert", "recommendation"],
            "keywords": ["호흡곤란", "악화", "빈호흡", "RR>25", "RR>30", "SpO2 저하", "FiO2 증가", "조기경보"],
            "citations": [
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]",
                "[2020년 한국심폐소생술 가이드라인]",
                "[Early Deterioration Command Center 기획서]"
            ],
            "signals": ["RR", "SpO2", "FiO2"],
            "decision_points": ["respiratory_distress_alert"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 2: Trigger - Associated Signs
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.Trigger.Associated.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)
## SECTION: Trigger
### SUBSECTION: Associated Signs

- **동반 위험 징후:** HR 20% 이상 증가, 체온 상승(감염/폐렴 의심). [2007 만성기도폐쇄성질환 기계환기법 치료지침, 2024 성인 패혈증 초기치료지침서]
- **임상 관찰 징후:** 보조 호흡근 사용, 기이 복부 운동. [2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜",
            "section": "Trigger",
            "subsection": "Associated",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["HR", "Temp"],
            "outputs": ["alert"],
            "keywords": ["HR 증가", "체온 상승", "보조호흡근", "복부운동", "감염", "폐렴"],
            "citations": [
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]",
                "[2024 성인 패혈증 초기치료지침서]"
            ],
            "signals": ["HR", "Temp"],
            "decision_points": ["infection_screening"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 3: Action - Validation
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.Action.Validation.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜
## SECTION: Action
### SUBSECTION: Validation

- **SpO₂ 데이터 신뢰도 점검:** 프로브 부착 상태, 말초 관류 저하(저혈압), 심한 빈혈 여부 확인. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
- **ABGA 권고:** SpO₂ 오차를 고려해 산소화/산염기 상태 확인 위해 ABGA 시행. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
- **원인 감별:** 기흉, 분비물에 의한 기도 폐쇄, 패혈증으로 인한 환기 요구량 증가 여부 평가. [2007 만성기도폐쇄성질환 기계환기법 치료지침, 2020년 한국심폐소생술 가이드라인]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜",
            "section": "Action",
            "subsection": "Validation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2", "MAP"],
            "outputs": ["recommendation"],
            "keywords": ["SpO2 신뢰도", "프로브", "관류", "빈혈", "ABGA", "기흉", "기도폐쇄", "패혈증"],
            "citations": [
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]",
                "[2020년 한국심폐소생술 가이드라인]"
            ],
            "signals": ["SpO2", "MAP"],
            "decision_points": ["data_validation", "cause_evaluation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 4: Action - NIV Escalation
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.Action.Escalation.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜
## SECTION: Action
### SUBSECTION: Escalation

- **NIV/NPPV 조기 적용 대상:** 최선의 내과적 치료에도 RR **> 25/min**, pH ≤ 7.35, PaCO₂ ≥ 45 mmHg. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
- **NIV 반응 평가:** 적용 **1–2시간 이내** RR 감소, pH 정상화 등 호전 여부 감시. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
- **기관내삽관/침습환기 전환 트리거:**
    - NIV 1–2시간 후 pH 악화, 또는 4시간 후에도 개선 없음. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
    - RR **> 35/min**. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
    - 의식 저하(기면) 또는 호흡 정지 징후. [2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜",
            "section": "Action",
            "subsection": "Escalation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["RR", "pH", "PaCO2"],
            "outputs": ["recommendation"],
            "keywords": ["NIV", "NPPV", "RR>25", "RR>35", "pH", "PaCO2", "삽관", "의식저하"],
            "citations": [
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
            ],
            "signals": ["RR", "pH", "PaCO2"],
            "decision_points": ["start_NIV", "intubation_trigger"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 5: Rationale
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.Rationale.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜
## SECTION: Rationale

- RR 증가/SpO₂ 저하/FiO₂ 요구량 상승은 급성 호흡부전 악화를 조기 포착하는 핵심 신호이며, 시스템이 이를 기반으로 조기 경보를 생성한다. [Early Deterioration Command Center 기획서]
- SpO₂는 관류/빈혈 등 상황에서 신뢰도가 저하될 수 있어 ABGA로 정밀 평가가 필요하다. [2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜",
            "section": "Rationale",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": [],
            "keywords": ["급성호흡부전", "조기포착", "SpO2 신뢰도", "ABGA"],
            "citations": [
                "[Early Deterioration Command Center 기획서]",
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 6: Exceptions - COPD (격리)
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.Exceptions.COPD.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜
## SECTION: Exceptions
### SUBSECTION: COPD

- **COPD/만성 폐질환 산소 목표:** SpO₂ 목표가 일반 환자(94–98%)와 다를 수 있음(88–92%). [2020년 한국심폐소생술 가이드라인, 2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜",
            "section": "Exceptions",
            "subsection": "COPD",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2"],
            "outputs": ["alert"],
            "keywords": ["COPD", "만성폐질환", "SpO2 88-92", "산소 목표"],
            "citations": [
                "[2020년 한국심폐소생술 가이드라인]",
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
            ],
            "signals": ["SpO2"],
            "decision_points": ["oxygen_target_exception"],
            "exclusion_group": "COPD_EXCEPTION",
            "route_if_query_contains": ["COPD", "만성폐질환", "CO2", "이산화탄소"]
        }
    })
    
    # Chunk 7: XAI Messages
    chunks.append({
        "id": "RESP_DISTRESS_BUNDLE.XAI.v1",
        "text": """# CARD: 호흡곤란 악화 대응 프로토콜
## SECTION: XAI

- "RR이 **{rr}/min**로 상승했고, SpO₂가 목표 범위 아래로 하락했으며 FiO₂ 요구량이 증가하고 있습니다. 호흡곤란 악화로 판단되어 장비/관류 상태를 점검하고 ABGA를 권고합니다." [Early Deterioration Command Center 기획서, 2007 만성기도폐쇄성질환 기계환기법 치료지침]
- "NIV 적용 후 1–2시간 내 호전이 없거나 RR>35, 의식저하가 동반되면 기관내삽관 전환을 고려하십시오." [2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "RESP_DISTRESS_BUNDLE",
            "card_title": "호흡곤란 악화 대응 프로토콜",
            "section": "XAI",
            "subsection": "",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["xai_message"],
            "keywords": ["설명", "메시지", "권고", "NIV", "삽관"],
            "citations": [
                "[Early Deterioration Command Center 기획서]",
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
            ],
            "signals": [],
            "decision_points": [],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # ==================== 프로토콜 카드 2: ARDS Bundle ====================
    
    # Chunk 8: ARDS - PF Definition
    chunks.append({
        "id": "ARDS_BUNDLE.Trigger.PF_Definition.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: PF Definition

- **표준 PF비:** PaO₂/FiO₂는 ARDS 중증도 분류 표준. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Trigger",
            "subsection": "PF_Definition",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["PaO2", "FiO2"],
            "outputs": ["alert"],
            "keywords": ["ARDS", "PF비", "PaO2/FiO2", "중증도"],
            "citations": [
                "[2016 ARDS 지침서]",
                "[2021 Surviving Sepsis Campaign]"
            ],
            "signals": ["PaO2", "FiO2"],
            "decision_points": ["ards_severity_classification"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 9: ARDS - PF Estimation
    chunks.append({
        "id": "ARDS_BUNDLE.Trigger.PF_Estimation.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: PF Estimation

- **ABGA 부재 시 추정 PF비:**
    - **Estimated P/F = (S/F − 64) / 0.84**. [Early Deterioration Command Center 기획서]
    - SpO₂–SaO₂ 변화는 임상적으로 비례 → 추세/반응 평가에 유용. [2007 만성기도폐쇄성질환 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Trigger",
            "subsection": "PF_Estimation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2", "FiO2"],
            "outputs": ["alert", "recommendation"],
            "keywords": ["ARDS", "PF비", "추정 PF", "S/F", "P/F=(S/F-64)/0.84"],
            "citations": [
                "[Early Deterioration Command Center 기획서]",
                "[2007 만성기도폐쇄성질환 치료지침]"
            ],
            "signals": ["SpO2", "FiO2"],
            "decision_points": ["pf_estimation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 10: ARDS - Berlin Severity
    chunks.append({
        "id": "ARDS_BUNDLE.Trigger.Severity.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Trigger
### SUBSECTION: Berlin Severity

- **경증:** PaO₂/FiO₂ 200–300 (SaO₂ 기반 추정 PF비 200–300). [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]
- **중등도:** PaO₂/FiO₂ 100–200 (SaO₂ 기반 추정 PF비 100–200). [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]
- **중증:** PaO₂/FiO₂ ≤100 (SaO₂ 기반 추정 PF비 ≤100). [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Trigger",
            "subsection": "Severity",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["PaO2", "FiO2"],
            "outputs": ["alert"],
            "keywords": ["ARDS", "Berlin", "경증", "중등도", "중증", "PF 200-300", "PF 100-200", "PF≤100"],
            "citations": [
                "[2016 ARDS 지침서]",
                "[2021 Surviving Sepsis Campaign]"
            ],
            "signals": ["PaO2", "FiO2"],
            "decision_points": ["ards_severity_classification"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 11: ARDS - Action Mild
    chunks.append({
        "id": "ARDS_BUNDLE.Action.Mild.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Action
### SUBSECTION: Mild (200-300)

- 폐 보호 환기 준수 점검: TV **≤ 6 mL/kg PBW**. [2016 ARDS 지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Action",
            "subsection": "Mild",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["TV", "PBW"],
            "outputs": ["recommendation"],
            "keywords": ["경증 ARDS", "폐보호환기", "TV 6mL/kg"],
            "citations": [
                "[2016 ARDS 지침서]"
            ],
            "signals": ["TV"],
            "decision_points": ["lung_protective_ventilation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 12: ARDS - Action Moderate
    chunks.append({
        "id": "ARDS_BUNDLE.Action.Moderate.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Action
### SUBSECTION: Moderate (100-200)

- **High PEEP 적용 고려**, **복와위 준비**. [2016 ARDS 지침서]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Action",
            "subsection": "Moderate",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["recommendation"],
            "keywords": ["중등도 ARDS", "High PEEP", "복와위 준비"],
            "citations": [
                "[2016 ARDS 지침서]"
            ],
            "signals": [],
            "decision_points": ["high_PEEP_consideration", "prone_preparation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 13: ARDS - Action Severe
    chunks.append({
        "id": "ARDS_BUNDLE.Action.Severe.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Action
### SUBSECTION: Severe (≤100)

- **복와위 즉각 시행(최소 16시간 이상)**, **NMBA 투여 검토**. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Action",
            "subsection": "Severe",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["recommendation"],
            "keywords": ["중증 ARDS", "복와위", "Prone", "NMBA", "16시간"],
            "citations": [
                "[2016 ARDS 지침서]",
                "[2021 Surviving Sepsis Campaign]"
            ],
            "signals": [],
            "decision_points": ["start_prone", "nmba_consideration"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 14: ARDS - Ventilation Bundle
    chunks.append({
        "id": "ARDS_BUNDLE.Action.Ventilation.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Action
### SUBSECTION: Ventilation Bundle

- TV ≤6 mL/kg PBW, Plateau <30 cmH₂O, Driving pressure <12–15 cmH₂O. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]
- PaO₂/FiO₂ ≤200 (추정 PF비 ≤200)에서 High PEEP 권고. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]
- PaO₂/FiO₂ ≤150 (추정 PF비 ≤150)에서 Prone 12–16시간 이상. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]
- 기계환기 시작 48시간 이내 NMBA 고려(필요 시 일시 투여 우선). [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Action",
            "subsection": "Ventilation",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["TV", "Plateau", "DrivingPressure", "PEEP"],
            "outputs": ["recommendation"],
            "keywords": ["TV 6mL/kg", "Plateau<30", "Driving pressure", "High PEEP", "PF≤200", "PF≤150", "Prone", "NMBA"],
            "citations": [
                "[2016 ARDS 지침서]",
                "[2021 Surviving Sepsis Campaign]"
            ],
            "signals": ["TV", "Plateau", "DrivingPressure", "PEEP"],
            "decision_points": ["lung_protective_ventilation", "high_PEEP_consideration", "start_prone", "nmba_consideration"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 15: ARDS - ECMO
    chunks.append({
        "id": "ARDS_BUNDLE.Action.ECMO.v1",
        "text": """# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜
## SECTION: Action
### SUBSECTION: ECMO Rescue

- 복와위 등에도 불구하고 저산소혈증 지속 시 **VV ECMO 고려**. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "ARDS_BUNDLE",
            "card_title": "ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
            "section": "Action",
            "subsection": "ECMO",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": [],
            "outputs": ["recommendation"],
            "keywords": ["ECMO", "VV ECMO", "구조요법", "저산소혈증"],
            "citations": [
                "[2016 ARDS 지침서]",
                "[2021 Surviving Sepsis Campaign]"
            ],
            "signals": [],
            "decision_points": ["ecmo_consideration"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # ==================== 프로토콜 카드 3: O2 Escalation Ladder ====================
    
    # Chunk 16: O2 - Target SpO2 General
    chunks.append({
        "id": "O2_ESCALATION_LADDER.Action.TargetSpO2_General.v1",
        "text": """# CARD: 산소요법 단계별 상향 (O₂ Escalation Ladder)
## SECTION: Action
### SUBSECTION: Target SpO₂ - General

- **일반 환자:** SpO₂ **94–98%** 목표. [2020년 한국심폐소생술 가이드라인, 2021 Surviving Sepsis Campaign International]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "O2_ESCALATION_LADDER",
            "card_title": "산소요법 단계별 상향 (O₂ Escalation Ladder)",
            "section": "Action",
            "subsection": "TargetSpO2_General",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2"],
            "outputs": ["alert"],
            "keywords": ["산소요법", "SpO2 목표", "94-98", "일반환자"],
            "citations": [
                "[2020년 한국심폐소생술 가이드라인]",
                "[2021 Surviving Sepsis Campaign International]"
            ],
            "signals": ["SpO2"],
            "decision_points": ["oxygen_target"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 17: O2 - Target SpO2 COPD Exception (격리)
    chunks.append({
        "id": "O2_ESCALATION_LADDER.Exceptions.COPD_TargetSpO2.v1",
        "text": """# CARD: 산소요법 단계별 상향 (O₂ Escalation Ladder)
## SECTION: Exceptions
### SUBSECTION: COPD Target SpO₂

- **(예외: COPD/만성 폐질환)** SpO₂ **88–92%** 목표. [2020년 한국심폐소생술 가이드라인, 2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "O2_ESCALATION_LADDER",
            "card_title": "산소요법 단계별 상향 (O₂ Escalation Ladder)",
            "section": "Exceptions",
            "subsection": "COPD_TargetSpO2",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2"],
            "outputs": ["alert"],
            "keywords": ["COPD", "만성폐질환", "SpO2 88-92", "CO2 retention"],
            "citations": [
                "[2020년 한국심폐소생술 가이드라인]",
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
            ],
            "signals": ["SpO2"],
            "decision_points": ["oxygen_target_exception"],
            "exclusion_group": "COPD_EXCEPTION",
            "route_if_query_contains": ["COPD", "만성폐질환", "CO2", "이산화탄소"]
        }
    })
    
    # Chunk 18: O2 - Escalation Ladder
    chunks.append({
        "id": "O2_ESCALATION_LADDER.Action.Ladder.v1",
        "text": """# CARD: 산소요법 단계별 상향 (O₂ Escalation Ladder)
## SECTION: Action
### SUBSECTION: Escalation Steps

- **1단계:** 비강 캐뉼라(NC) / 단순 마스크.
- **2단계:** 비재호흡 마스크(NRB). [2012 JSCC 중환자실에서의 기도관리]
- **3단계:** 고유량 비강 캐뉼라(HFNC) - 단순 산소요법에도 저산소혈증성 호흡부전 지속 시 적용. [2021 Surviving Sepsis Campaign International]
- **4단계:** NIV/NPPV - RR >25/min, pH ≤7.35, PaCO₂ ≥45 mmHg에서 조기 적용. [2007 만성기도폐쇄성질환 기계환기법 치료지침]
- **5단계:** 기관내삽관 및 침습적 기계환기 - RR >35/min, pH <7.25 등. [2007 만성기도폐쇄성질환 기계환기법 치료지침]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "O2_ESCALATION_LADDER",
            "card_title": "산소요법 단계별 상향 (O₂ Escalation Ladder)",
            "section": "Action",
            "subsection": "Ladder",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2", "FiO2", "RR"],
            "outputs": ["recommendation"],
            "keywords": ["O2 escalation", "NC", "NRB", "HFNC", "NIV", "삽관", "단계상향"],
            "citations": [
                "[2012 JSCC 중환자실에서의 기도관리]",
                "[2021 Surviving Sepsis Campaign International]",
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
            ],
            "signals": ["SpO2", "FiO2", "RR"],
            "decision_points": ["oxygen_escalation"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    # Chunk 19: O2 - No Response Checklist
    chunks.append({
        "id": "O2_ESCALATION_LADDER.Action.NoResponse_Checklist.v1",
        "text": """# CARD: 산소요법 단계별 상향 (O₂ Escalation Ladder)
## SECTION: Action
### SUBSECTION: No Response Checklist

"산소 올려도 SpO₂ 회복 안 됨" 체크리스트:
1. 프로브/간섭요인 확인(탈착, 매니큐어, 강한 빛, 피부색 등). [2007 만성기도폐쇄성질환 기계환기법 치료지침]
2. 관류 상태 평가(저혈압, 말초관류 저하, 심한 빈혈). [2007 만성기도폐쇄성질환 기계환기법 치료지침]
3. ABGA 시행(SpO₂ 오차 ±5–7% 고려, SaO₂ 확인 권고). [2007 만성기도폐쇄성질환 기계환기법 치료지침]
4. 기도 개통성 확인(튜브 막힘/꺾임, 기흉 점검). [2020년 한국심폐소생술 가이드라인]""",
        "metadata": {
            "doc_type": "protocol_card",
            "card_id": "O2_ESCALATION_LADDER",
            "card_title": "산소요법 단계별 상향 (O₂ Escalation Ladder)",
            "section": "Action",
            "subsection": "NoResponse",
            "version": "v1.0",
            "language": "ko",
            "clinical_domain": ["respiratory", "critical_care"],
            "intended_users": ["clinician"],
            "inputs_required": ["SpO2"],
            "outputs": ["recommendation"],
            "keywords": ["SpO2 회복 안됨", "프로브", "관류저하", "ABGA", "기흉", "튜브 폐쇄"],
            "citations": [
                "[2007 만성기도폐쇄성질환 기계환기법 치료지침]",
                "[2020년 한국심폐소생술 가이드라인]"
            ],
            "signals": ["SpO2"],
            "decision_points": ["troubleshooting_hypoxemia"],
            "exclusion_group": "",
            "route_if_query_contains": []
        }
    })
    
    return chunks

def delete_vectordb():
    """기존 VectorDB 삭제"""
    if os.path.exists(PERSIST_DIR):
        print(f"🗑️  Deleting existing VectorDB at {PERSIST_DIR}...")
        shutil.rmtree(PERSIST_DIR)
        print("✅ VectorDB deleted successfully")
    else:
        print("⚠️  No existing VectorDB found")

def create_vectordb_from_chunks(chunks):
    """구조화된 청크로 VectorDB 생성"""
    print(f"🔧 Creating VectorDB with {len(chunks)} structured chunks...")
    
    # Document 객체 생성 및 메타데이터 직렬화
    documents = []
    for chunk in chunks:
        # ChromaDB는 metadata에 list를 허용하지 않으므로 JSON 문자열로 변환
        serialized_metadata = {}
        for key, value in chunk["metadata"].items():
            if isinstance(value, (list, dict)):
                serialized_metadata[key] = json.dumps(value, ensure_ascii=False)
            else:
                serialized_metadata[key] = value
        
        doc = Document(
            page_content=chunk["text"],
            metadata=serialized_metadata
        )
        documents.append((chunk["id"], doc))
    
    # HuggingFace 임베딩 모델
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # ChromaDB 생성
    ids = [item[0] for item in documents]
    docs = [item[1] for item in documents]
    
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        ids=ids
    )
    
    print(f"✅ VectorDB created at {PERSIST_DIR}")
    print(f"📊 Total chunks embedded: {len(chunks)}")
    
    return vectorstore

def verify_vectordb():
    """VectorDB 검증"""
    print("\n🔍 Verifying VectorDB...")
    
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
            "query": "RR이 30 이상일 때 어떻게 해야 하나요?",
            "where": {"exclusion_group": ""}  # COPD 예외 제외
        },
        {
            "query": "COPD 환자의 산소 목표는?",
            "where": None  # COPD 예외 포함
        },
        {
            "query": "복와위는 언제 하나요?",
            "where": {"exclusion_group": ""}
        },
        {
            "query": "추정 PF비 계산 방법",
            "where": {"exclusion_group": ""}
        }
    ]
    
    for test in test_cases:
        results = vectorstore.similarity_search(
            test["query"], 
            k=2,
            filter=test["where"]
        )
        print(f"\n📝 Query: {test['query']}")
        if results:
            print(f"   Top result ID: {results[0].metadata.get('chunk_id', results[0].metadata.get('source', 'unknown'))}")
            print(f"   Card: {results[0].metadata.get('card_id')}")
            print(f"   Section: {results[0].metadata.get('section')}")
            print(f"   Text preview: {results[0].page_content[:80]}...")
            if results[0].metadata.get('exclusion_group'):
                print(f"   ⚠️  COPD Exception chunk")
    
    print("\n✅ Verification complete")

def main():
    print("=" * 80)
    print("🚀 Structured VectorDB Rebuild (chunk.md 방법론 준수)")
    print("=" * 80)
    
    # 1. 구조화된 청크 생성
    print("\n📝 Creating structured chunks...")
    chunks = create_chunks()
    print(f"✅ Created {len(chunks)} chunks")
    
    # 2. 기존 DB 삭제
    delete_vectordb()
    
    # 3. VectorDB 생성
    vectorstore = create_vectordb_from_chunks(chunks)
    
    # 4. 검증
    verify_vectordb()
    
    # 5. JSONL 내보내기 (선택사항 - Supabase 이관용)
    output_file = "protocol_chunks.jsonl"
    print(f"\n📤 Exporting chunks to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            json.dump(chunk, f, ensure_ascii=False)
            f.write('\n')
    print(f"✅ Exported to {output_file}")
    
    print("\n" + "=" * 80)
    print("✨ VectorDB rebuild completed successfully!")
    print("=" * 80)
    print("\n💡 Key Features:")
    print("   - 19 structured chunks with rich metadata")
    print("   - COPD exceptions properly isolated (exclusion_group)")
    print("   - Citation tracking maintained")
    print("   - Ready for Supabase migration (JSONL exported)")

if __name__ == "__main__":
    main()
