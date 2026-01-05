/**
 * 가이드라인 관련 API 라우터
 *
 * 엔드포인트:
 * - GET /api/guidelines/suggest : 상황별 가이드라인 제안
 *
 * 연결할 서비스:
 * - RAG Service: Supabase 벡터 검색
 *
 * 데이터 소스:
 * - 대한중환자의학회 가이드라인
 * - 패혈증 초기 치료 지침서
 * - 기타 임상 프로토콜 (rag/documents/)
 *
 * TODO:
 * - [ ] Supabase 벡터 검색 연결
 * - [ ] Citation 포함 응답 구현
 * - [ ] 위험 타입별 자동 쿼리 생성
 */

const express = require("express");
const router = express.Router();
// const ragService = require('../services/ragService');  // RAG 서비스 연결 시 주석 해제

// ========================
// GET /api/guidelines/suggest
// ========================
/**
 * 상황별 가이드라인 제안
 *
 * 쿼리 파라미터:
 * - risk_type: 'mortality', 'vent_start', 'pressors_start'
 * - query: 직접 검색어 입력 (선택)
 *
 * 응답:
 * - guidelines: 관련 가이드라인 목록
 *   - title: 가이드라인 제목
 *   - content: 핵심 내용
 *   - source: 출처 (Citation)
 *
 * TODO: 실제 구현 시
 * 1. risk_type에 따른 검색 쿼리 생성
 *    - pressors_start → "패혈증 승압제 초기 치료"
 *    - vent_start → "기계환기 적응증 프로토콜"
 *    - mortality → "중환자 악화 대응 체크리스트"
 * 2. Supabase에서 벡터 유사도 검색
 * 3. 상위 3개 문서 청크 반환 (출처 포함)
 */
router.get("/suggest", async (req, res) => {
  const { risk_type, query } = req.query;

  // TODO: RAG 서비스 호출
  // const guidelines = await ragService.searchGuidelines(risk_type, query);

  // risk_type별 기본 가이드라인 매핑
  const guidelinesByType = {
    pressors_start: {
      title: "패혈증 초기 치료 지침",
      content:
        "1. 1시간 이내 광범위 항생제 투여\n2. 30ml/kg 수액 소생술\n3. MAP ≥ 65mmHg 목표\n4. Norepinephrine 1차 승압제로 권장",
      source: "대한중환자의학회 2024 패혈증 가이드라인 p.23",
    },
    vent_start: {
      title: "기계환기 시작 기준",
      content:
        "1. PaO2 < 60mmHg (FiO2 > 0.5)\n2. PaCO2 > 50mmHg with pH < 7.30\n3. 호흡수 > 35/min\n4. 호흡 보조근 사용",
      source: "대한중환자의학회 기계환기 프로토콜 p.15",
    },
    mortality: {
      title: "중환자 악화 대응 체크리스트",
      content:
        "1. 기도 확보 확인\n2. 산소 공급 증가\n3. 수액 반응성 평가\n4. 가족 면담 준비",
      source: "중환자 간호 매뉴얼 2024 p.45",
    },
  };

  const selectedGuideline =
    guidelinesByType[risk_type] || guidelinesByType.pressors_start;

  res.json({
    message: "가이드라인 제안",
    data: {
      risk_type: risk_type || "pressors_start",
      query: query || null,
      guidelines: [selectedGuideline],
      retrieved_at: new Date().toISOString(),
    },
  });
});

module.exports = router;
