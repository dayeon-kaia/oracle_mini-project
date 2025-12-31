const oracledb = require("oracledb");
const path = require("path");
require("dotenv").config({ path: path.join(__dirname, "../../../.env") });

// Thick 모드 활성화 (Mac)
try {
  oracledb.initOracleClient({ libDir: "/opt/oracle/instantclient_19_16" });
} catch (err) {
  console.error("Thick 모드 초기화 실패:", err);
}

const dbConfig = {
  user: process.env.ORACLE_USER,
  password: process.env.ORACLE_PASSWORD,
  connectString: process.env.ORACLE_CONNECTION_STRING,
  privilege: oracledb.SYSDBA,
};

// 쿼리 실행 함수
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

// 연결 테스트
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

// 직접 실행 시 테스트
if (require.main === module) {
  testConnection();
}
