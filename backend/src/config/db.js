/**
 * Oracle DB 연결 설정
 *
 * 역할:
 * - Oracle DB 연결 (Thick 모드)
 * - 쿼리 실행 함수 제공
 * - 연결 테스트
 *
 * 사용법:
 * const db = require('./config/db');
 * const result = await db.execute('SELECT * FROM patients');
 *
 * 환경변수 필요 (.env):
 * - ORACLE_USER: DB 계정명
 * - ORACLE_PASSWORD: DB 비밀번호
 * - ORACLE_CONNECTION_STRING: IP:포트/서비스명
 */

const oracledb = require("oracledb");
const path = require("path");
require("dotenv").config({ path: path.join(__dirname, "../../../.env") });

// ========================
// Thick 모드 활성화
// ========================
// Oracle Native Network Encryption 사용을 위해 필요
// Mac: /opt/oracle/instantclient_19_16
// Windows: C:\\oracle\\instantclient_19_16
// Linux: /opt/oracle/instantclient_19_16
try {
  oracledb.initOracleClient({ libDir: "/opt/oracle/instantclient_19_16" });
} catch (err) {
  console.error("Thick 모드 초기화 실패:", err);
}

// ========================
// DB 연결 설정
// ========================
const dbConfig = {
  user: process.env.ORACLE_USER,
  password: process.env.ORACLE_PASSWORD,
  connectString: process.env.ORACLE_CONNECTION_STRING,
  privilege: oracledb.SYSDBA,
};

// ========================
// 쿼리 실행 함수
// ========================
/**
 * SQL 쿼리 실행
 * @param {string} sql - 실행할 SQL 쿼리
 * @param {Array} params - 바인드 파라미터 (선택)
 * @returns {Object} - 쿼리 결과 { rows: [...], metaData: [...] }
 *
 * 예시:
 * const result = await execute('SELECT * FROM patients WHERE id = :id', [1]);
 */
async function execute(sql, params = []) {
  let connection;
  try {
    connection = await oracledb.getConnection(dbConfig);
    const result = await connection.execute(sql, params, {
      outFormat: oracledb.OUT_FORMAT_OBJECT,
    });
    return result;
  } finally {
    if (connection) {
      await connection.close();
    }
  }
}

// ========================
// 연결 테스트
// ========================
/**
 * DB 연결 테스트
 * @returns {boolean} - 연결 성공 여부
 */
async function testConnection() {
  let connection;
  try {
    connection = await oracledb.getConnection(dbConfig);
    console.log("Oracle DB 연결 성공!");

    const result = await connection.execute("SELECT 1 FROM DUAL");
    console.log("쿼리 테스트 성공:", result.rows);
    return true;
  } catch (err) {
    console.error("Oracle DB 연결 실패:", err.message);
    return false;
  } finally {
    if (connection) {
      await connection.close();
      console.log("연결 종료");
    }
  }
}

module.exports = { execute, testConnection };

// 직접 실행 시 테스트: node src/config/db.js
if (require.main === module) {
  testConnection();
}
