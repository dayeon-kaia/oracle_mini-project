/**
 * 인증 관련 API 라우터
 *
 * 엔드포인트:
 * - POST /api/auth/login : 로그인
 *
 * Mock 계정 (하드코딩):
 * - patient1 / 1234 : 환자/보호자
 * - resident1 / 1234 : 레지던트
 * - doctor1 / 1234 : 의사
 * - admin / 1234 : 관리자
 *
 * 참고: 실제 프로덕션에서는 JWT + DB 사용해야 하지만, MVP인 관계로 간단하게 구현했습니다!!
 */

const express = require("express");
const router = express.Router();

// ========================
// Mock 계정 (하드코딩)
// ========================
const mockUsers = [
  { id: "patient1", password: "1234", role: "patient", name: "보호자" },
  { id: "resident1", password: "1234", role: "resident", name: "레저던트" },
  { id: "doctor1", password: "1234", role: "doctor", name: "닥터" },
  { id: "admin", password: "1234", role: "admin", name: "시스템 관리자" },
];

// ========================
// POST /api/auth/login
// ========================
/**
 * 로그인
 *
 * 요청 body:
 * {
 *   id: "doctor1",
 *   password: "1234"
 * }
 *
 * 성공 응답:
 * {
 *   success: true,
 *   user: { id, role, name }
 * }
 *
 * 실패 응답:
 * {
 *   success: false,
 *   message: "아이디 또는 비밀번호가 올바르지 않습니다"
 * }
 */
router.post("/login", (req, res) => {
  const { id, password } = req.body;

  // Mock 계정에서 찾기
  const user = mockUsers.find((u) => u.id === id && u.password === password);

  if (user) {
    res.json({
      success: true,
      user: {
        id: user.id,
        role: user.role,
        name: user.name,
      },
    });
  } else {
    res.status(401).json({
      success: false,
      message: "아이디 또는 비밀번호가 올바르지 않습니다",
    });
  }
});

// ========================
// GET /api/auth/me
// ========================
/**
 * 현재 로그인 정보 확인 (프론트에서 localStorage 기반)
 * 실제로는 토큰 검증 로직 필요
 */
router.get("/me", (req, res) => {
  // TODO: 실제 구현 시 토큰 검증
  res.json({
    message: "토큰 기반 인증은 미구현 상태입니다",
  });
});

module.exports = router;
