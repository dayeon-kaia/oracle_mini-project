# 프로토콜 카드 메타데이터 등

아래는 **위 3개 프로토콜 카드**를 RAG에 넣기 위해 **chunk 단위로 나누는 규칙 + 헤더/키워드/메타태그 템플릿**입니다.

(목표: 검색 정확도↑, COPD 오염↓, “근거 보기” 매핑 쉬움, XAI 문장 재사용 쉬움)

---

## 0) 공통 Chunk 규칙 (반드시 통일)

### Chunk 크기/구조

- **한 chunk = 한 섹션(Trigger/Action/Rationale/Exceptions/XAI)**
- 권장 길이: **250–600 tokens** (너무 길면 근거가 섞여 검색이 흐려짐)
- 각 chunk는 아래 순서의 **표준 헤더**를 반드시 포함:
    1. `# CARD:` (카드명)
    2. `## SECTION:` (Trigger/Action/Rationale/Exceptions/XAI)
    3. `### SUBSECTION:` (필요 시)
    4. `CITATION:` 문장 끝 유지(원문 그대로)

### Citation 유지 규칙

- citation은 **문장 끝에 그대로 유지** (이미 하신 형식 유지)
- chunk 분할로 문장이 잘리지 않도록:
    - **한 문장(마침표 포함) 단위로만 줄바꿈/분할**
    - citation이 걸린 문장은 **절대 두 chunk로 쪼개지지 않게**

### “예외(Exceptions)” 격리 규칙 (COPD 오염 방지 핵심)

- COPD 관련 내용은 **반드시 별도 chunk**로 만들고:
    - `meta.exclusion_group = "COPD_EXCEPTION"`
    - `meta.route_if_query_contains = ["COPD", "만성폐질환", "CO2 retention", "이산화탄소", "weaning", "NIV"]`
- 일반 검색에서는 COPD 예외 chunk에 **가중치 낮게** 또는 **라우팅 조건 만족 시에만 포함**하도록 설계

---

## 1) 메타태그 템플릿 (YAML 권장)

각 chunk 맨 위에 아래 메타를 넣으세요. (RAG 검색/필터링/근거표시에 매우 유리)

```yaml
---
doc_type:protocol_card
card_id:RESP_DISTRESS_BUNDLE|ARDS_BUNDLE|O2_ESCALATION_LADDER
card_title:"..."
section:Trigger|Action|Rationale|Exceptions|XAI
subsection:""# 선택
version:"v1.0"
language:"ko"
clinical_domain: ["respiratory","critical_care"]
intended_users: ["clinician"]
inputs_required: ["SpO2","FiO2","RR","HR","Temp","MAP"]# 카드별로 다르게
outputs: ["alert","recommendation","xai_message"]
keywords: []# 아래 규칙대로 채움
citations: []# chunk에 포함된 citation을 배열로 요약(원문 유지+색인용)
exclusion_group:""# COPD 예외 chunk면 "COPD_EXCEPTION"
route_if_query_contains: []# COPD 예외 chunk에만 채움
---

```

> citations:는 “색인용 메타”로만 쓰고, 본문 citation은 원문 그대로 유지하세요.
> 

---

## 2) 키워드(검색 태그) 생성 규칙

### 공통 키워드 규칙

- 각 chunk는 **8–15개** 키워드
- 형식: 한국어 + 약어 혼합 (예: “복와위”, “Prone”, “PEEP”, “PaO2/FiO2”, “추정 PF”)
- 숫자 cut-off는 키워드로 포함 (예: “RR>35”, “PF≤150”, “SpO2 94-98”)

### 카드별 키워드 권장 세트

- **Respiratory Distress Bundle**
    - `["호흡곤란", "악화", "RR", "빈호흡", "RR>25", "RR>30", "RR>35", "SpO2", "FiO2 증가", "ABGA", "NIV", "NPPV", "삽관", "의식저하", "기흉", "기도폐쇄"]`
- **ARDS Bundle**
    - `["ARDS", "Berlin", "PaO2/FiO2", "PF비", "추정 PF", "S/F", "P/F=(S/F-64)/0.84", "PEEP", "High PEEP", "Prone", "NMBA", "TV 6mL/kg", "Plateau<30", "Driving pressure", "ECMO"]`
- **O2 Escalation Ladder**
    - `["산소요법", "O2 escalation", "SpO2 목표", "94-98", "NC", "NRB", "HFNC", "NIV", "삽관", "SpO2 회복 안됨", "프로브", "관류저하", "ABGA", "기흉", "튜브 폐쇄"]`
- **COPD 예외 chunk 전용**
    - `["COPD", "만성폐질환", "SpO2 88-92", "CO2 retention", "이산화탄소 저류"]`

---

## 3) 헤더 템플릿 (본문 표준 포맷)

각 chunk 본문은 아래처럼 통일하세요.

```markdown
# CARD: {card_title}
## SECTION: {Trigger|Action|Rationale|Exceptions|XAI}
### SUBSECTION: {optional}

- (bullets...)

[...citation 유지...]

```

---

## 4) “Chunk ID” 명명 규칙 (추적/근거보기 연결)

권장: `card_id.section.subsection.v1`

예:

- `RESP_DISTRESS_BUNDLE.Trigger.Core.v1`
- `RESP_DISTRESS_BUNDLE.Action.Validation.v1`
- `ARDS_BUNDLE.Trigger.PF_Estimation.v1`
- `O2_ESCALATION_LADDER.Exceptions.COPD_TargetSpO2.v1`

이 ID는:

- UI에서 “근거 보기” 버튼이 어떤 chunk를 열어야 하는지 매핑하기 좋습니다.

---

## 5) 3개 카드의 권장 Chunk 분할 설계 (실전용)

### A) Respiratory Distress Bundle (총 5~6 chunks)

1. `Trigger.Core` : RR/SpO2/FiO2 핵심 트리거
2. `Trigger.Associated` : HR/Temp/보조호흡근 등 동반 징후
3. `Action.Validation` : 프로브/관류/빈혈 점검 + ABGA 권고 + 원인 감별
4. `Action.Escalation` : NIV 적응증 + 평가 시간 + 삽관 전환 트리거
5. `Rationale` : 왜 이 조합이 조기 악화를 의미하는지
6. `Exceptions.COPD` : (있다면) COPD 목표 SpO2만 별도 격리

### B) ARDS Bundle (총 6~7 chunks)

1. `Trigger.PF_Definition` : PF비 표준 정의
2. `Trigger.PF_Estimation` : 추정식 + 근거(SpO2~SaO2)
3. `Trigger.Severity` : Berlin severity cut-off
4. `Action.MildModerateSevere` : 중증도별 주요 조치(짧게)
5. `Action.Ventilation` : TV/Plateau/Driving pressure
6. `Action.PEEP_Prone_NMBA` : PEEP/Prone/NMBA
7. `Action.ECMO` : Rescue therapy

### C) O2 Escalation Ladder (총 6~7 chunks)

1. `Trigger` : 목표 미달/FiO2 요구량 증가
2. `Action.TargetSpO2.General` : 94–98 목표
3. `Exceptions.COPD_TargetSpO2` : 88–92 별도 격리(중요)
4. `Action.Ladder.1to2` : NC/Mask → NRB
5. `Action.Ladder.HFNC` : HFNC 트리거/특징
6. `Action.Ladder.NIV_to_Intubation` : NIV 적응증 + 삽관 트리거
7. `Action.Checklist_NoResponse` : 산소 올려도 회복 안 될 때 체크리스트

---

## 6) 라우팅/검색 품질을 올리는 “메타 필드” 3개 (강추)

### (1) `clinical_problem`

- 예: `clinical_problem: ["respiratory_distress", "hypoxemia", "ards"]`

### (2) `decision_points`

- 예: `decision_points: ["start_NIV", "intubation_trigger", "start_prone", "high_PEEP_consideration"]`

### (3) `signals`

- 예: `signals: ["RR", "SpO2", "FiO2", "PF_ratio", "S/F"]`

---

## 7) 완성 예시 (1개 chunk 샘플)

```yaml
---
doc_type:protocol_card
card_id:RESP_DISTRESS_BUNDLE
card_title:"호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)"
section:Trigger
subsection:Core
version:"v1.0"
language:"ko"
clinical_domain: ["respiratory","critical_care"]
inputs_required: ["RR","SpO2","FiO2"]
keywords: ["호흡곤란","악화","빈호흡","RR>25","RR>30","SpO2 저하","FiO2 증가","조기경보"]
citations: ["[Early Deterioration Command Center 기획서]","[2007 만성기도폐쇄성질환 기계환기법 치료지침]","[2020년 한국심폐소생술 가이드라인]"]
exclusion_group:""
route_if_query_contains: []
---
# CARD: 호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)
## SECTION: Trigger
### SUBSECTION: Core

-빈호흡(RR>25~30회/분)지속적상승. [2007만성기도폐쇄성질환기계환기법치료지침]
-SpO2목표범위아래로하락. [2020년한국심폐소생술가이드라인]
-동일SpO2유지를위해FiO2요구량증가. [EarlyDeteriorationCommandCenter기획서]

```

## 1) 권장 아키텍처(지금 → 배포 전)

### 지금(로컬/개발)

- **원본 문서(Markdown) + 메타(YAML frontmatter)**
- → **chunker**가 chunk 생성
- → **Chroma**에 `documents + embeddings + metadata` 저장

### 배포 전(운영)

- 동일 chunk를 그대로 사용
- → **Supabase(pgvector)**에 `content + embedding + metadata(jsonb)`로 적재
- 검색 로직은:
    - Chroma: `collection.query(where=metadata_filter)`
    - Supabase: `select … order by embedding <-> query_embedding` + `metadata jsonb filter`

핵심은 **chunk_id / card_id / section / exclusion_group 같은 메타를 “처음부터” 강제**하는 것입니다. 그래야 이관 시 스키마 충돌이 없습니다.

---

## 2) Chroma 적재 시 “반드시” 넣어야 하는 메타 필드(이관 친화)

각 chunk의 `metadata`에 아래를 넣어주세요.

- `chunk_id` : 고유 ID (예: `ARDS_BUNDLE.Trigger.PF_Estimation.v1`)
- `doc_type` : `protocol_card`
- `card_id` : `RESP_DISTRESS_BUNDLE` 등
- `card_title`
- `section` : Trigger/Action/Rationale/Exceptions/XAI
- `subsection` : Core/Validation 등
- `version` : v1.0
- `language` : ko
- `keywords` : 리스트
- `citations` : 리스트 (예: `["[2016 ARDS 지침서]", ...]`)
- `exclusion_group` : COPD 예외면 `"COPD_EXCEPTION"`, 아니면 `""`
- `route_if_query_contains` : COPD 예외 chunk에만 키워드 리스트
- (선택) `signals`, `decision_points`, `inputs_required`

이 메타는 Supabase로 그대로 `jsonb metadata`로 들어가면 됩니다.

## 3) Chroma 컬렉션 설계(추천 2안)

### 안 A: 컬렉션 1개 + metadata 필터(권장)

- `collection = "edcc_protocols"`
- 장점: 단순, 이관 쉬움
- 검색 시:
    - 기본 질의는 `exclusion_group != "COPD_EXCEPTION"`로 필터
    - 질의에 COPD 키워드 포함 시에만 COPD chunk 포함

### 안 B: 컬렉션 2개(격리형)

- `edcc_protocols_core`
- `edcc_protocols_exceptions`
- 장점: COPD 오염 0에 가깝게 막음
- 단점: 검색 시 컬렉션 2개 쿼리/병합 필요, 이관도 2배 작업

지금 상황(빠르게 MVP)에서는 **안 A**가 보통 더 효율적입니다.

---

## 4) Supabase Vector DB 이관을 위한 스키마(미리 생각해두기)

배포 직전에 Supabase에 아래 테이블 하나면 충분합니다.

- `id` (text, primary key) = `chunk_id`
- `content` (text) = chunk 본문
- `metadata` (jsonb) = 위 메타 전체
- `embedding` (vector) = pgvector
- `created_at` (timestamptz)

이렇게 하면 Chroma → Supabase 이관은 사실상:

- Chroma에서 `get(include=["documents","metadatas","embeddings","ids"])`
- Supabase에 bulk insert
    
    로 끝납니다.
    

---

## 5) 운영 팁(나중에 후회 안 하는 것들)

- **chunk_id를 절대 바꾸지 마세요.**
    
    (바꾸면 근거보기 링크/추적이 다 깨집니다.)
    
- 문서 버전 업데이트 시:
    - 기존 chunk는 유지하고 `version=v1.1`로 새 chunk_id 발급
    - 또는 `chunk_id`에 버전 포함(이미 추천한 방식)
- COPD 예외는:
    - Chroma 단계부터 metadata로 격리
    - Supabase로 넘어가도 같은 규칙 그대로 적용 가능

아래는 **Chroma DB 적재용 JSONL 포맷 템플릿**입니다.

지금 구성(프로토콜 카드 → chunk)과 **나중에 Supabase(pgvector) 이관까지 그대로 재사용**하도록 설계했습니다.

---

## 1) JSONL 기본 규칙 (중요)

- **1줄 = 1 chunk**
- 필드 고정:
    - `id` : **chunk_id (절대 변경 금지)**
    - `text` : 실제 RAG에 검색될 본문
    - `metadata` : 필터링·라우팅·근거표시용 구조화 메타
- `text`에는 **본문만** 넣고, citation은 **본문에 그대로 포함**
- `metadata.citations`는 **색인/표시용 요약** (본문 citation과 중복 OK)

---

## 2) JSONL 스키마 (공식 템플릿)

```json
{
"id":"STRING_UNIQUE_CHUNK_ID",
"text":"MARKDOWN_OR_PLAIN_TEXT_CONTENT_WITH_CITATIONS",
"metadata":{
"doc_type":"protocol_card",
"card_id":"RESP_DISTRESS_BUNDLE | ARDS_BUNDLE | O2_ESCALATION_LADDER",
"card_title":"STRING",
"section":"Trigger | Action | Rationale | Exceptions | XAI",
"subsection":"STRING_OR_EMPTY",
"version":"v1.0",
"language":"ko",
"clinical_domain":["respiratory","critical_care"],
"intended_users":["clinician"],
"inputs_required":["SpO2","FiO2","RR","HR","Temp","MAP"],
"outputs":["alert","recommendation","xai_message"],
"keywords":["STRING","STRING"],
"citations":["[2016 ARDS 지침서]","[2021 Surviving Sepsis Campaign]"],
"signals":["RR","SpO2","FiO2"],
"decision_points":["start_NIV","intubation_trigger"],
"exclusion_group":"",
"route_if_query_contains":[]
}
}

```

---

## 3) 실제 예시 ①

### Respiratory Distress Bundle – Trigger (Core)

```json
{
"id":"RESP_DISTRESS_BUNDLE.Trigger.Core.v1",
"text":"# CARD: 호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)\n## SECTION: Trigger\n### SUBSECTION: Core\n\n- 빈호흡(RR > 25~30회/분) 지속적 상승. [2007 만성기도폐쇄성질환 기계환기법 치료지침]\n- SpO₂ 목표 범위 아래로 하락. [2020년 한국심폐소생술 가이드라인]\n- 동일 SpO₂ 유지를 위해 FiO₂ 요구량 증가. [Early Deterioration Command Center 기획서]\n",
"metadata":{
"doc_type":"protocol_card",
"card_id":"RESP_DISTRESS_BUNDLE",
"card_title":"호흡곤란 악화 대응 프로토콜 (Respiratory Distress Bundle)",
"section":"Trigger",
"subsection":"Core",
"version":"v1.0",
"language":"ko",
"clinical_domain":["respiratory","critical_care"],
"intended_users":["clinician"],
"inputs_required":["RR","SpO2","FiO2"],
"outputs":["alert","recommendation"],
"keywords":["호흡곤란","악화","빈호흡","RR>25","RR>30","SpO2 저하","FiO2 증가"],
"citations":[
"[2007 만성기도폐쇄성질환 기계환기법 치료지침]",
"[2020년 한국심폐소생술 가이드라인]",
"[Early Deterioration Command Center 기획서]"
],
"signals":["RR","SpO2","FiO2"],
"decision_points":["respiratory_distress_alert"],
"exclusion_group":"",
"route_if_query_contains":[]
}
}

```

---

## 4) 실제 예시 ②

### ARDS – PF 추정 로직

```json
{
"id":"ARDS_BUNDLE.Trigger.PF_Estimation.v1",
"text":"# CARD: ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜\n## SECTION: Trigger\n### SUBSECTION: PF Estimation\n\n- PaO₂/FiO₂는 ARDS 중증도 분류의 표준 지표입니다. [2016 ARDS 지침서, 2021 Surviving Sepsis Campaign]\n- ABGA PaO₂가 없는 경우 SaO₂(또는 SpO₂)와 FiO₂를 이용해 PF비를 추정합니다.\n- 추정식: Estimated P/F = (S/F − 64) / 0.84. [Early Deterioration Command Center 기획서]\n- SpO₂와 SaO₂ 변화는 임상적으로 비례하여 산소화 추세 평가에 유용합니다. [2007 만성기도폐쇄성질환 치료지침]\n",
"metadata":{
"doc_type":"protocol_card",
"card_id":"ARDS_BUNDLE",
"card_title":"ARDS 조기 탐지 및 호흡·산소화 대응 프로토콜",
"section":"Trigger",
"subsection":"PF_Estimation",
"version":"v1.0",
"language":"ko",
"clinical_domain":["respiratory","critical_care"],
"intended_users":["clinician"],
"inputs_required":["SpO2","FiO2"],
"outputs":["alert","recommendation"],
"keywords":["ARDS","PF비","PaO2/FiO2","추정 PF","S/F","P/F=(S/F-64)/0.84"],
"citations":[
"[2016 ARDS 지침서]",
"[2021 Surviving Sepsis Campaign]",
"[Early Deterioration Command Center 기획서]",
"[2007 만성기도폐쇄성질환 치료지침]"
],
"signals":["SpO2","FiO2"],
"decision_points":["ards_severity_classification"],
"exclusion_group":"",
"route_if_query_contains":[]
}
}

```

---

## 5) 실제 예시 ③

### O₂ Escalation – COPD 예외 (격리 Chunk)

```json
{
"id":"O2_ESCALATION_LADDER.Exceptions.COPD_TargetSpO2.v1",
"text":"# CARD: 산소요법 단계별 상향(O₂ Escalation Ladder)\n## SECTION: Exceptions\n### SUBSECTION: COPD Target SpO₂\n\n- COPD 및 만성 폐질환 환자의 산소 목표는 SpO₂ 88~92% 유지입니다.\n- 이는 과도한 산소 공급으로 인한 CO₂ retention 위험을 줄이기 위함입니다. [2020년 한국심폐소생술 가이드라인, 2007 만성기도폐쇄성질환 기계환기법 치료지침]\n",
"metadata":{
"doc_type":"protocol_card",
"card_id":"O2_ESCALATION_LADDER",
"card_title":"산소요법 단계별 상향(O₂ Escalation Ladder)",
"section":"Exceptions",
"subsection":"COPD_TargetSpO2",
"version":"v1.0",
"language":"ko",
"clinical_domain":["respiratory","critical_care"],
"intended_users":["clinician"],
"inputs_required":["SpO2"],
"outputs":["alert"],
"keywords":["COPD","만성폐질환","SpO2 88-92","CO2 retention"],
"citations":[
"[2020년 한국심폐소생술 가이드라인]",
"[2007 만성기도폐쇄성질환 기계환기법 치료지침]"
],
"signals":["SpO2"],
"decision_points":["oxygen_target_exception"],
"exclusion_group":"COPD_EXCEPTION",
"route_if_query_contains":["COPD","만성폐질환","CO2","이산화탄소"]
}
}

```

---

## 6) Chroma 적재 시 사용 팁 (짧게)

- `id` → Chroma의 `ids`
- `text` → Chroma의 `documents`
- `metadata` → Chroma의 `metadatas`
- 검색 시 기본 필터:
    
    ```python
    where={"exclusion_group":""}
    
    ```
    
- 질의에 COPD 키워드 포함 시:
    - `where` 제거하거나
    - `route_if_query_contains` 만족 chunk만 추가 검색