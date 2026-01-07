/**
 * ============================================================
 * ML Service 연동 모듈
 * ============================================================
 *
 * 역할:
 * - Flask ML Service API 호출
 * - 예측 결과 반환
 *
 * 사용법:
 * const mlService = require('./services/mlService');
 * const result = await mlService.predict(patientId, features);
 *
 * TODO:
 * - [ ] 전처리 완료 후 features 포맷 확정
 * - [ ] 에러 핸들링 강화
 * - [ ] 타임아웃 설정 조정
 * ============================================================
 */

const axios = require("axios");

// ============================================================
// 설정
// ============================================================
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || "http://localhost:5001";
const TIMEOUT = 10000; // 10초

// axios 인스턴스
const mlClient = axios.create({
  baseURL: ML_SERVICE_URL,
  timeout: TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================
// 헬스 체크
// ============================================================
/**
 * ML Service 상태 확인
 * @returns {Object} { status, model_loaded, timestamp }
 */
async function healthCheck() {
  try {
    const response = await mlClient.get("/health");
    return response.data;
  } catch (error) {
    console.error("❌ ML Service 헬스 체크 실패:", error.message);
    return {
      status: "error",
      model_loaded: false,
      error: error.message,
    };
  }
}

// ============================================================
// 단일 환자 예측
// ============================================================
/**
 * 단일 환자 예측 요청
 *
 * @param {string} patientId - 환자 ID
 * @param {Object} features - 특성 데이터 (전처리 후 확정)
 * @returns {Object} 예측 결과
 *
 * 예시:
 * const result = await predict('P-1024', {
 *   heart_rate_mean: 92,
 *   lactate: 2.1,
 *   ...
 * });
 *
 * 반환값:
 * {
 *   patient_id: 'P-1024',
 *   predictions: {
 *     mortality_24h: 0.75,
 *     vent_start_12h: 0.45,
 *     pressors_start_12h: 0.60
 *   },
 *   shap_top5: [...],
 *   predicted_at: '2024-01-01T11:00:00Z'
 * }
 */
async function predict(patientId, features) {
  try {
    const response = await mlClient.post("/predict", {
      patient_id: patientId,
      features: features,
    });

    return response.data;
  } catch (error) {
    console.error(`❌ 예측 실패 (${patientId}):`, error.message);
    throw new Error(`ML Service 예측 실패: ${error.message}`);
  }
}

// ============================================================
// 다중 환자 예측 (배치)
// ============================================================
/**
 * 다중 환자 배치 예측 요청
 *
 * @param {Array} patients - [{ patient_id, features }, ...]
 * @returns {Object} 배치 예측 결과
 *
 * 예시:
 * const result = await predictBatch([
 *   { patient_id: 'P-1024', features: {...} },
 *   { patient_id: 'P-2156', features: {...} }
 * ]);
 */
async function predictBatch(patients) {
  try {
    const response = await mlClient.post("/predict/batch", {
      patients: patients,
    });

    return response.data;
  } catch (error) {
    console.error("❌ 배치 예측 실패:", error.message);
    throw new Error(`ML Service 배치 예측 실패: ${error.message}`);
  }
}

// ============================================================
// Export
// ============================================================
module.exports = {
  healthCheck,
  predict,
  predictBatch,
};
