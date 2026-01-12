"""
LLM Service Module using LangChain

This module provides core LLM functionality using LangChain framework:
- ChatOpenAI model initialization
- Prompt template management
- Output parsers
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class ClinicalSummaryOutput(BaseModel):
    """Output schema for clinical summary"""

    risk_level: str = Field(description="위험도 수준 (high/medium/low)")
    risk_score: float = Field(description="위험도 점수 (0-1)")
    summary: str = Field(description="임상 상황 요약 (정상 범위 비교, 추세 분석, 의사결정 필요 사항)")
    key_features: List[Dict[str, Any]] = Field(
        description="근거 피처 목록 (최대 3개)"
    )
    data_quality_alerts: List[str] = Field(
        description="데이터 품질 경고 사항", default_factory=list
    )


class GentleReportOutput(BaseModel):
    """Output schema for gentle report"""

    status: str = Field(description="환자 상태 (안정/불안정/매우 불안정)")
    simple_explanation: str = Field(description="쉬운 언어로 작성된 상태 설명")
    what_to_expect: str = Field(description="예상되는 상황 설명")
    family_guidance: str = Field(description="보호자 안내 사항")


class QueryFilterOutput(BaseModel):
    """Output schema for Q&A query filters"""

    filters: Dict[str, Any] = Field(description="필터 파라미터")
    interpretation: str = Field(description="질의 해석 설명")
    sort_by: Optional[str] = Field(description="정렬 기준", default=None)


class LLMService:
    """Core LLM service using LangChain"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM service

        Args:
            model_name: OpenAI model name (default: from env or gpt-4o-mini)
            temperature: LLM temperature
            api_key: OpenAI API key (default: from env)
        """
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=temperature,
            openai_api_key=self.api_key,
        )

    def create_clinical_summary_chain(self):
        """
        Create LangChain chain for clinical summary generation using LCEL

        Returns:
            Runnable chain for clinical summary
        """
        parser = PydanticOutputParser(pydantic_object=ClinicalSummaryOutput)

        template = """당신은 중환자실 전문의를 돕는 AI 기반 임상 의사결정 지원 시스템입니다.

⚠️ **윤리적 사용 원칙:**
- 본 결과는 임상 의사결정을 **보조**하기 위한 참고 정보입니다.
- 단독으로 치료 결정에 사용되어서는 안 됩니다.
- 모든 표현은 "가능성", "시사", "권장" 형태로 작성하세요.
- "사망 예정", "임종 준비", "회복 불가" 같은 결정적 표현은 금지됩니다.

환자의 생체 신호(vitals), 검사 결과(labs), 그리고 AI 모델 예측 결과를 종합 분석하여 
의료진의 신속한 판단과 의사결정을 돕는 진단 보조 정보를 제공하세요.

**정상 참고 범위 (ICU Standard Ranges):**
- SpO2: 95-100% (정상), 90-94% (주의), <90% (심각)
- MAP (평균동맥압): 70-100 mmHg (정상), 65-69 mmHg (주의), <65 mmHg (심각)
- HR (심박수): 60-100 bpm (정상), 100-120 bpm (주의), >120 bpm (심각)
- RR (호흡수): 12-20 bpm (정상), 20-25 bpm (주의), >25 bpm (심각)
- Lactate (젖산): <2 mmol/L (정상), 2-4 mmol/L (주의), >4 mmol/L (심각)

**입력 데이터:**
- 환자 ID: {patient_id}
- 현재 Vitals: {vitals}
- 현재 Labs: {labs}
- AI 모델 SHAP 분석: {shap_features}
- 데이터 품질 상태: {data_quality_flags}
- AI 예측 위험도: {prediction_risk}

**출력 요구사항:**

1. **위험도 평가 (Risk Assessment):**
   - risk_level: "high" (예후 악화 가능성이 높음 또는 다중 바이탈 이상)
   - risk_level: "medium" (예후 악화 가능성이 중등도 또는 일부 바이탈 주의)
   - risk_level: "low" (현재 기준에서 단기 위험은 낮은 편)
   - risk_score: 예측된 최대 위험도 (0-1, 내부 참고용)

2. **임상 상태 요약 (Clinical Summary):**
   **단순 수치 나열을 지양**하고, **"환자의 현재 상태(Condition)"**를 종합적으로 진단/해석하여 서술하세요.
   
   - **종합 상태 정의 (Condition Synthesis):**
     - "현재 환자는 [임상 상태 정의] 상태인 것으로 보입니다."
     - 예시: "현재 환자는 패혈성 쇼크(Septic Shock)가 의심되는 매우 불안정한 상태입니다."
   
   - **상태 근거 (Evidence Context):**
     - 왜 그런 상태인지 임상 지표를 연결하여 설명 (수치는 근거로 괄호 병기).
     - 예시: "지속적인 저혈압(MAP 58)과 젖산 수치 상승(4.2)은 조직 관류 부전을 시사합니다."
   
   - **변화 양상 (Trajectory):**
     - "임상 경과는 [악화/호전/정체] 양상을 보이고 있습니다."
     - 예시: "승압제 투여에도 불구하고 젖산 수치가 상승하여 임상 경과가 악화되고 있습니다."
   
   - **권고 (Recommendation):**
     - 치료 목표 논의 필요성 언급
     - 예시: "임상 경과를 종합할 때 치료 목표에 대한 재논의가 권장됩니다."

3. **핵심 위험 인자 (Key Risk Features):**
   SHAP 기반 상위 3개 피처, 각각:
   {{"feature": "피처명", "value": 측정값, "contribution": SHAP 값, "interpretation": "임상적 의미 설명"}}
   
   interpretation 예시:
   - "RR 32 bpm (정상의 1.6배)은 호흡부전 진행 가능성을 시사하며, 기계환기 준비를 고려할 수 있습니다."
   - "Lactate 4.2 mmol/L은 조직 관류 부전의 가능성이 있으며, 패혈증을 시사할 수 있습니다."

4. **데이터 품질 경고 (data_quality_alerts):**
   - 입력된 데이터 품질 플래그가 있으면 포함
   - 없으면 빈 리스트

**작성 원칙:**
✓ 모든 수치는 정상 범위와 명시적 비교 (예: "정상보다 X% 높음/낮음")
✓ 의학적 해석 포함 (단순 나열이 아닌 임상적 의미 설명)
✓ 추세 정보 활용 (상승/하락/안정 및 속도)
✓ 비결정적 표현 필수 - "의심", "시사", "가능성", "고려" 등 사용
✓ 결정적 단언 금지 - "반드시", "확정", "불가피" 등 사용 금지
✓ 구체적 치료 권고는 제외 (RAG 프로토콜에서 별도 제공)
✓ 의료진이 신속히 상황을 파악할 수 있도록 간결하고 명확하게

{format_instructions}
"""

        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "patient_id",
                "vitals",
                "labs",
                "shap_features",
                "data_quality_flags",
                "prediction_risk",
            ],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Use LCEL (LangChain Expression Language)
        chain = prompt | self.llm | parser
        return chain

    def create_gentle_report_chain(self):
        """
        Create LangChain chain for gentle report generation using LCEL

        Returns:
            Runnable chain for gentle report
        """
        parser = PydanticOutputParser(pydantic_object=GentleReportOutput)

        template = """당신은 환자 보호자에게 환자의 상태를 설명하는 의료 커뮤니케이터입니다.

⚠️ **윤리적 사용 원칙 (보호자용):**
- 확률 수치는 직접 노출하지 않습니다.
- "사망 예정", "임종 준비", "회복 불가" 같은 표현은 절대 금지입니다.
- 논의의 목적은 "사망 예고"가 아니라 "치료 목표 재정렬"입니다.
- 위험 수준 + 임상 상태 설명만 허용됩니다.

의료진용 임상 요약을 기반으로, 보호자가 이해하기 쉬운 언어로 환자 상태를 설명하세요.

**원칙:**
- 의학 용어를 최소화하고 일반인이 이해할 수 있는 단어 사용
- 불안감을 과도하게 조성하지 않되, 정확한 상황 전달
- 보호자가 준비해야 할 사항이 있으면 부드럽게 안내
- 의료진이 환자를 집중 치료 중임을 명시
- "가능성", "고려", "권장" 등 비결정적 표현 사용

**입력 데이터:**
- 환자 ID: {patient_id}
- 위험도 수준: {risk_level}
- 임상 요약: {clinical_summary}
- 주요 변화: {key_changes}

**출력 요구사항:**
1. 환자 상태 (안정/불안정/매우 불안정)
2. 쉬운 언어로 작성된 상태 설명 (의학 용어 최소화, 확률 수치 금지)
3. 예상되는 상황 설명 ("가능성", "고려" 표현 사용)
4. 보호자 안내 사항 (예: 환자 곁 지킬 준비, 의료진 문의 사항 등)

{format_instructions}
"""

        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "patient_id",
                "risk_level",
                "clinical_summary",
                "key_changes",
            ],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Use LCEL
        chain = prompt | self.llm | parser
        return chain

    def create_qa_filter_chain(self):
        """
        Create LangChain chain for Q&A filter generation using LCEL

        Returns:
            Runnable chain for Q&A filter
        """
        parser = PydanticOutputParser(pydantic_object=QueryFilterOutput)

        template = """당신은 자연어 질의를 환자 필터 쿼리로 변환하는 AI입니다.

사용자의 자연어 질문을 분석하여, 환자 목록을 필터링할 수 있는 파라미터로 변환하세요.

**Few-shot 예시:**

질의: "최근 2시간 내 위험도 급상승한 환자 보여줘"
→ filters: {{"time_range": "2h", "risk_change": "급상승", "threshold": "any"}}
   interpretation: "최근 2시간 동안 위험도가 급격히 상승한 환자를 조회합니다."
   sort_by: "risk_change_rate"

질의: "Pressor 위험 상위 5명"
→ filters: {{"risk_type": "pressor", "top_n": 5}}
   interpretation: "Pressor 시작 위험도가 가장 높은 상위 5명의 환자를 조회합니다."
   sort_by: "pressor_risk"

질의: "예후 악화 가능성 높은 환자"
→ filters: {{"risk_type": "mortality", "risk_level": "high"}}
   interpretation: "예후 악화 가능성이 높은 수준인 환자를 조회합니다."
   sort_by: "mortality_risk"

**사용자 질의:**
{query}

**사용 가능한 필터 옵션:**
- time_range: "1h", "2h", "4h", "12h", "24h"
- risk_type: "mortality", "pressor", "vent"
- risk_level: "high", "medium", "low"
- risk_change: "급상승", "상승", "안정", "하락"
- top_n: 정수 (상위 N명)

{format_instructions}
"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Use LCEL
        chain = prompt | self.llm | parser
        return chain


def create_llm_service(
    model_name: Optional[str] = None,
    temperature: float = 0.2,
    api_key: Optional[str] = None,
) -> LLMService:
    """
    Factory function to create LLMService instance

    Args:
        model_name: OpenAI model name
        temperature: LLM temperature
        api_key: OpenAI API key

    Returns:
        Initialized LLMService instance
    """
    return LLMService(model_name=model_name, temperature=temperature, api_key=api_key)


if __name__ == "__main__":
    # Test LLM service initialization
    service = create_llm_service()
    print("✅ LLM Service initialized successfully")
    print(f"Model: {service.model_name}")

    # Test chain creation
    clinical_chain = service.create_clinical_summary_chain()
    print("✅ Clinical Summary Chain created")

    gentle_chain = service.create_gentle_report_chain()
    print("✅ Gentle Report Chain created")

    qa_chain = service.create_qa_filter_chain()
    print("✅ Q&A Filter Chain created")
