/**
 * 환자 관련 API 라우터
 *
 * 엔드포인트:
 * - GET /api/patients          : 환자 목록 조회
 * - GET /api/patients/:id      : 환자 상세 정보
 * - GET /api/patients/:id/risk : 환자 위험도 조회
 *
 * TODO:
 * - [ ] DB 연결 후 실제 쿼리로 교체
 * - [ ] 환자 목록 페이지네이션 추가
 * - [ ] 위험도 기준 정렬 기능 추가
 */

const express = require("express");
const router = express.Router();
// const db = require('../config/db');  // DB 연결 시 주석 해제

// ========================
// GET /api/patients
// ========================
/**
 * 환자 목록 조회
 *
 * 응답 예시:
 * {
 *   data: [
 *     { id: 1, name: '환자1', risk: 'high' },
 *     { id: 2, name: '환자2', risk: 'medium' }
 *   ]
 * }
 *
 * TODO: 실제 구현 시 아래 쿼리 사용
 * SELECT patient_id, name, risk_level FROM patients ORDER BY risk_level DESC
 */
router.get("/", async (req, res) => {
  // TODO: DB 연결 후 실제 데이터로 교체
  // const result = await db.execute('SELECT * FROM patients');
  // res.json({ data: result.rows });

  res.json({
    message: "환자 목록",
    data: [
      { id: 1, name: "환자1", risk: "high" },
      { id: 2, name: "환자2", risk: "medium" },
    ],
  });
});

// ========================
// GET /api/patients/:id
// ========================
/**
 * 환자 상세 정보
 *
 * 파라미터:
 * - id: 환자 ID
 *
 * 응답에 포함될 정보:
 * - 기본 정보 (이름, 나이, 성별)
 * - 현재 vitals (심박수, 혈압, 호흡수, SpO2)
 * - 최근 labs (lactate, creatinine 등)
 *
 * TODO: 실제 구현 시
 * 1. patients 테이블에서 기본 정보 조회
 * 2. vitals 테이블에서 최근 vitals 조회
 * 3. labs 테이블에서 최근 labs 조회
 */
router.get("/:id", async (req, res) => {
  const { id } = req.params;

  res.json({
    message: "환자 상세",
    data: {
      id,
      name: `환자${id}`,
      age: 65,
      gender: "M",
      admission_date: "2024-12-30",
      vitals: {
        heart_rate: 85,
        blood_pressure: "120/80",
        respiratory_rate: 18,
        spo2: 96,
      },
      labs: {
        lactate: 2.1,
        creatinine: 1.2,
      },
    },
  });
});

// ========================
// GET /api/patients/:id/risk
// ========================
/**
 * 환자 위험도 조회
 *
 * 파라미터:
 * - id: 환자 ID
 *
 * 응답:
 * - mortality: 24시간 내 사망 확률 (0-1)
 * - vent_start: 12/24시간 내 인공호흡기 시작 확률 (0-1)
 * - pressors_start: 12/24시간 내 승압제 시작 확률 (0-1)
 *
 * TODO: 실제 구현 시
 * 1. predictions 테이블에서 최근 예측 결과 조회
 * 2. 또는 ML 서비스 호출하여 실시간 예측
 */
router.get("/:id/risk", async (req, res) => {
  const { id } = req.params;

  res.json({
    message: "환자 위험도",
    data: {
      id,
      mortality: 0.75, // 24h 내 사망 확률
      vent_start: 0.45, // 12/24h 내 인공호흡기 확률
      pressors_start: 0.6, // 12/24h 내 승압제 확률
      updated_at: new Date().toISOString(),
    },
  });
});

module.exports = router;
