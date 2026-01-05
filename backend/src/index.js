/**
 * Express 서버 진입점
 *
 * 역할:
 * - 미들웨어 설정 (CORS, JSON 파싱)
 * - 라우터 연결
 * - 서버 시작
 */

const express = require("express");
const cors = require("cors");
require("dotenv").config({
  path: require("path").join(__dirname, "../../.env"),
});

const app = express();
const PORT = process.env.PORT || 3000;

// ========================
// 미들웨어 설정
// ========================
app.use(cors()); // 프론트엔드에서 API 호출 허용
app.use(express.json()); // JSON 요청 body 파싱

// ========================
// 라우터 연결
// ========================
const patientsRouter = require("./routes/patients");
const predictionRouter = require("./routes/prediction");
const summaryRouter = require("./routes/summary");
const guidelinesRouter = require("./routes/guidelines");
const authRouter = require("./routes/auth");

app.use("/api/patients", patientsRouter); // 환자 관련 API
app.use("/api/prediction", predictionRouter); // 예측 관련 API
app.use("/api/summary", summaryRouter); // AI 요약 API
app.use("/api/guidelines", guidelinesRouter); // 가이드라인 API
app.use("/api/auth", authRouter); // 계정 기반 로그인 API

// ========================
// 헬스 체크
// ========================
// 서버 정상 동작 확인용 엔드포인트
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// ========================
// 서버 시작
// ========================
app.listen(PORT, () => {
  console.log(`서버 실행 중: http://localhost:${PORT}`);
});
