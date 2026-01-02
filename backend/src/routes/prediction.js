/**
 * 예측 관련 API 라우터
 *
 * 엔드포인트:
 * - POST /api/prediction : 환자 예측 요청
 *
 * 연결할 서비스:
 * - ML Service (Flask): 모델 추론 + SHAP 분석
 *
 * TODO:
 * - [ ] ML Service API 호출 구현
 * - [ ] 예측 결과 DB 저장
 * - [ ] 배치 예측 (여러 환자 동시) 구현
 */

const express = require("express");
const router = express.Router();
// const mlService = require('../services/mlService');  // ML 서비스 연결 시 주석 해제

// ========================
// POST /api/prediction
// ========================
/**
 * 환자 예측 요청
 *
 * 요청 body:
 * {
 *   patient_id: 1,
 *   features: { ... }  // 선택: 직접 features 전달 시
 * }
 *
 * 응답:
 * - mortality: 사망 확률
 * - vent_start: 인공호흡기 시작 확률
 * - pressors_start: 승압제 시작 확률
 * - shap_top5: 예측에 기여한 상위 5개 특성
 *
 * TODO: 실제 구현 시
 * 1. patient_id로 DB에서 최근 vitals/labs 조회
 * 2. features 전처리 (6h/12h 윈도우 통계값)
 * 3. ML Service POST /predict 호출
 * 4. 결과 DB 저장 후 반환
 */
router.post("/", async (req, res) => {
  const { patient_id } = req.body;

  // TODO: ML 서비스 호출
  // const prediction = await mlService.predict(patient_id);

  res.json({
    message: "예측 결과",
    data: {
      patient_id,
      mortality: 0.75,
      vent_start: 0.45,
      pressors_start: 0.6,
      shap_top5: [
        { feature: "lactate", contribution: 0.23 },
        { feature: "map_mean", contribution: 0.18 },
        { feature: "heart_rate_std", contribution: 0.12 },
        { feature: "spo2_min", contribution: 0.09 },
        { feature: "creatinine", contribution: 0.07 },
      ],
      predicted_at: new Date().toISOString(),
    },
  });
});

module.exports = router;
