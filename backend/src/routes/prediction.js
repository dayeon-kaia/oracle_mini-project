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
const mlService = require("../services/mlService"); // ML 서비스 연결 시 주석 해제

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
  try {
    const { patient_id, features } = req.body;

    if (!patient_id) {
      return res.status(400).json({ error: "patient_id is required" });
    }

    // TODO: features 없으면 DB에서 조회해서 가져오기
    // const features = await dbService.getPatientFeatures(patient_id);

    // ML Service 호출
    const result = await mlService.predict(patient_id, features || {});

    res.json({
      message: "예측 결과",
      data: result,
    });
  } catch (error) {
    console.error("예측 API 에러:", error.message);
    res.status(500).json({ error: error.message });
  }
});

// ========================
// POST /api/prediction/batch
// ========================
/**
 * 다중 환자 배치 예측
 */
router.post("/batch", async (req, res) => {
  try {
    const { patients } = req.body;

    if (!patients || !Array.isArray(patients)) {
      return res.status(400).json({ error: "patients array is required" });
    }

    // ML Service 배치 호출
    const result = await mlService.predictBatch(patients);

    res.json({
      message: "배치 예측 결과",
      data: result,
    });
  } catch (error) {
    console.error("배치 예측 API 에러:", error.message);
    res.status(500).json({ error: error.message });
  }
});

// ========================
// GET /api/prediction/health
// ========================
/**
 * ML Service 상태 확인
 */
router.get("/health", async (req, res) => {
  const status = await mlService.healthCheck();
  res.json(status);
});

module.exports = router;
