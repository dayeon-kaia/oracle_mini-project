/**
 * AI 요약 관련 API 라우터
 *
 * 엔드포인트:
 * - GET /api/summary/:id : 환자 상태 AI 요약
 *
 * 연결할 서비스:
 * - RAG Service: Supabase 벡터 검색 + LLM 호출
 *
 * 요약 타입:
 * - medical: 의료진용 (수치, 확률 포함)
 * - family: 보호자용 (수치 없이 쉬운 설명)
 *
 * TODO:
 * - [ ] LLM 서비스 연결 (OpenAI / Claude)
 * - [ ] 프롬프트 템플릿 적용 (rag/prompts/)
 * - [ ] 의료진 확인 후 보호자용 생성 로직
 */

const express = require("express");
const router = express.Router();
// const ragService = require('../services/ragService');  // RAG 서비스 연결 시 주석 해제

// ========================
// GET /api/summary/:id
// ========================
/**
 * 환자 상태 AI 요약
 *
 * 파라미터:
 * - id: 환자 ID
 *
 * 쿼리 파라미터:
 * - type: 'medical' (기본값) 또는 'family'
 *
 * 응답:
 * - summary: LLM이 생성한 요약 텍스트
 *
 * TODO: 실제 구현 시
 * 1. 환자의 최근 vitals/labs 트렌드 조회
 * 2. 예측 결과 + SHAP Top5 조회
 * 3. 프롬프트 템플릿에 데이터 삽입
 * 4. LLM 호출하여 요약 생성
 *
 * 의료진용 프롬프트 예시 (rag/prompts/medical_summary.txt):
 * "환자의 최근 6시간 데이터를 바탕으로 위험 요인을 요약해주세요.
 *  - Vitals: {vitals}
 *  - Labs: {labs}
 *  - 예측 결과: {prediction}
 *  - 주요 기여 특성: {shap_top5}"
 */
router.get("/:id", async (req, res) => {
  const { id } = req.params;
  const { type } = req.query; // 'medical' or 'family'

  // TODO: LLM 서비스 호출
  // const summary = await ragService.generateSummary(id, type);

  const summaries = {
    medical:
      "지난 4시간 MAP 하락(78→65mmHg)과 lactate 상승(1.2→2.8mmol/L), 소변량 감소(40→15ml/hr)가 동반되며 pressor_start 위험이 급상승했습니다. Norepinephrine 준비를 권장합니다.",
    family:
      "현재 상태가 빠르게 변하고 있어 경과가 급변할 수 있습니다. 의료진이 주의 깊게 모니터링하고 있으며, 변화가 있으면 바로 알려드리겠습니다.",
  };

  res.json({
    message: "AI 요약",
    data: {
      patient_id: id,
      type: type || "medical",
      summary: summaries[type] || summaries.medical,
      generated_at: new Date().toISOString(),
    },
  });
});

module.exports = router;
