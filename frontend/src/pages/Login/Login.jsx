import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Login.css";

function Login() {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await api.post("/auth/login", { id, password });

      if (response.data.success) {
        localStorage.setItem("user", JSON.stringify(response.data.user));
        const role = response.data.user.role;
        navigate(`/dashboard/${role}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || "로그인 실패");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">EDCC</h1>
        <p className="login-subtitle">Early Deterioration Command Center</p>

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="text"
            placeholder="아이디"
            value={id}
            onChange={(e) => setId(e.target.value)}
            className="login-input"
          />
          <input
            type="password"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login-input"
          />
          {error && <p className="login-error">{error}</p>}
          <button type="submit" className="login-button">
            로그인
          </button>
        </form>

        <div className="login-hint">
          <p className="login-hint-title">테스트 계정</p>
          <p>환자/보호자: patient1 / 1234</p>
          <p>레지던트: resident1 / 1234</p>
          <p>의사: doctor1 / 1234</p>
          <p>관리자: admin / 1234</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
