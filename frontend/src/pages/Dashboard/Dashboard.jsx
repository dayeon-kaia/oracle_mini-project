import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  const { role } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (!savedUser) {
      navigate("/login");
      return;
    }

    const userData = JSON.parse(savedUser);

    if (userData.role !== role) {
      navigate(`/dashboard/${userData.role}`);
      return;
    }

    setUser(userData);
  }, [role, navigate]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  if (!user) return null;

  // 보호자는 별도 뷰
  if (role === "patient") {
    return <PatientView user={user} onLogout={handleLogout} />;
  }

  // 의료진/관리자 뷰
  return (
    <div className="dashboard-container">
      <Header user={user} onLogout={handleLogout} />
      <main className="dashboard-main">
        <Sidebar role={role} />
        <div className="dashboard-content">
          {role === "resident" && <ResidentContent />}
          {role === "doctor" && <DoctorContent />}
          {role === "admin" && <AdminContent />}
        </div>
      </main>
    </div>
  );
}

// ========================
// 헤더
// ========================
function Header({ user, onLogout }) {
  return (
    <header className="dashboard-header">
      <div className="dashboard-header-left">
        <div className="dashboard-logo">
          <div className="dashboard-logo-icon">⚡</div>
          <div className="dashboard-logo-text">
            <h1>EDCC</h1>
            <p>Early Deterioration Command Center</p>
          </div>
        </div>
        <div className="dashboard-search">
          <span>🔍</span>
          <input
            type="text"
            placeholder="AI에게 명령을 내려주세요 (예: '최근 2시간 내 Pressor 위험 급상승 환자 필터링')"
          />
          <button className="ask-ai-btn">✨ Ask AI</button>
        </div>
      </div>
      <div className="dashboard-header-right">
        <span style={{ color: "#888", fontSize: "14px" }}>{user.name}</span>
        <span style={{ cursor: "pointer" }} onClick={onLogout}>
          🚪
        </span>
        <div className="dashboard-user-badge">{getRoleInitial(user.role)}</div>
      </div>
    </header>
  );
}

// ========================
// 사이드바 (역할별 다르게)
// ========================
function Sidebar({ role }) {
  if (role === "admin") {
    return (
      <aside className="dashboard-sidebar">
        <p
          style={{
            fontSize: "12px",
            color: "#666",
            marginBottom: "8px",
            textTransform: "uppercase",
          }}
        >
          System Control
        </p>

        <div className="stat-card purple">
          <div className="stat-card-icon">🖥️</div>
          <div className="stat-card-value">✓</div>
          <div className="stat-card-title">Backend API</div>
          <div className="stat-card-subtitle">Running on :3000</div>
        </div>

        <div className="stat-card orange">
          <div className="stat-card-icon">🤖</div>
          <div className="stat-card-value">✓</div>
          <div className="stat-card-title">ML Service</div>
          <div className="stat-card-subtitle">Running on :5000</div>
        </div>

        <div className="stat-card yellow">
          <div className="stat-card-icon">🗄️</div>
          <div className="stat-card-value">✓</div>
          <div className="stat-card-title">Oracle DB</div>
          <div className="stat-card-subtitle">Connected</div>
        </div>

        <div className="stat-card blue">
          <div className="stat-card-icon">⏰</div>
          <div className="stat-card-value">✓</div>
          <div className="stat-card-title">Airflow</div>
          <div className="stat-card-subtitle">3 DAGs active</div>
        </div>
      </aside>
    );
  }

  // 레지던트 / 의사 공통 사이드바
  return (
    <aside className="dashboard-sidebar">
      <p
        style={{
          fontSize: "12px",
          color: "#666",
          marginBottom: "8px",
          textTransform: "uppercase",
        }}
      >
        System Overview
      </p>

      <div className="stat-card purple">
        <div className="stat-card-icon">📊</div>
        <div className="stat-card-value">47</div>
        <div className="stat-card-title">Total Monitored</div>
        <div className="stat-card-subtitle">Active patients in ICU</div>
      </div>

      <div className="stat-card orange">
        <div className="stat-card-icon">⚠️</div>
        <div className="stat-card-value">5</div>
        <div className="stat-card-title">Critical Alerts</div>
        <div className="stat-card-subtitle">24h mortality high risk</div>
      </div>

      <div className="stat-card yellow">
        <div className="stat-card-icon">💉</div>
        <div className="stat-card-value">12</div>
        <div className="stat-card-title">Upcoming Interventions</div>
        <div className="stat-card-subtitle">12h Vent/Pressor predicted</div>
      </div>

      <div className="stat-card blue">
        <div className="stat-card-icon">📈</div>
        <div className="stat-card-value">3</div>
        <div className="stat-card-title">Data Integrity Issues</div>
        <div className="stat-card-subtitle">Sensor checks needed</div>
      </div>
    </aside>
  );
}

// ========================
// 레지던트 컨텐츠 (가이드라인 강조)
// ========================
function ResidentContent() {
  return (
    <>
      <ContentHeader title="High-Risk Patients" />
      <PatientTableSimple />
      <GuidelineHub />
    </>
  );
}

// ========================
// 의사 컨텐츠 (전체 뷰)
// ========================
function DoctorContent() {
  return (
    <>
      <ContentHeader title="Active Patient Monitor" />
      <PatientTable />
      <AIHub />
    </>
  );
}

// ========================
// 관리자 컨텐츠 (시뮬레이션 제어)
// ========================
function AdminContent() {
  return (
    <>
      <ContentHeader title="System Administration" />
      <SimulationControl />
      <SystemLogs />
    </>
  );
}

// ========================
// 컨텐츠 헤더
// ========================
function ContentHeader({ title }) {
  return (
    <div className="content-header">
      <h2>{title}</h2>
      <div className="live-indicator">
        <span className="live-dot"></span>
        Live Data Stream
      </div>
    </div>
  );
}

// ========================
// 환자 테이블 (의사용 - 상세)
// ========================
function PatientTable() {
  const patients = [
    {
      id: "P-1024",
      bed: "ICU-A Bed 03",
      composite: 92,
      mortality: 88,
      vent: 82,
      pressor: 96,
      status: "critical",
    },
    {
      id: "P-2156",
      bed: "ICU-B Bed 12",
      composite: 87,
      mortality: 91,
      vent: 75,
      pressor: 79,
      status: "critical",
    },
    {
      id: "P-3421",
      bed: "ICU-A Bed 07",
      composite: 79,
      mortality: 76,
      vent: 83,
      pressor: 71,
      status: "critical",
    },
    {
      id: "P-4782",
      bed: "ICU-C Bed 05",
      composite: 74,
      mortality: 72,
      vent: 68,
      pressor: 81,
      status: "critical",
    },
    {
      id: "P-5098",
      bed: "ICU-B Bed 08",
      composite: 68,
      mortality: 65,
      vent: 72,
      pressor: 64,
      status: "warning",
    },
    {
      id: "P-6234",
      bed: "ICU-A Bed 15",
      composite: 58,
      mortality: 61,
      vent: 54,
      pressor: 59,
      status: "warning",
    },
    {
      id: "P-7456",
      bed: "ICU-C Bed 11",
      composite: 52,
      mortality: 48,
      vent: 56,
      pressor: 51,
      status: "warning",
    },
    {
      id: "P-8901",
      bed: "ICU-B Bed 02",
      composite: 45,
      mortality: 42,
      vent: 48,
      pressor: 44,
      status: "stable",
    },
    {
      id: "P-9312",
      bed: "ICU-A Bed 09",
      composite: 38,
      mortality: 35,
      vent: 41,
      pressor: 37,
      status: "stable",
    },
    {
      id: "P-1067",
      bed: "ICU-C Bed 14",
      composite: 32,
      mortality: 28,
      vent: 35,
      pressor: 33,
      status: "stable",
    },
  ];

  return (
    <div className="patient-table">
      <div className="patient-table-header">
        <span>Patient Info</span>
        <span>Composite Risk</span>
        <span>Mortality (24h)</span>
        <span>Vent Start (12h)</span>
        <span>Pressor Start (12h)</span>
        <span>Key Trends</span>
        <span>Status</span>
      </div>
      {patients.map((patient) => (
        <div key={patient.id} className="patient-table-row">
          <div className="patient-info">
            <span className="patient-id">{patient.id}</span>
            <span className="patient-bed">{patient.bed}</span>
          </div>
          <RiskBadge value={patient.composite} />
          <RiskBadge value={patient.mortality} />
          <RiskBadge value={patient.vent} />
          <RiskBadge value={patient.pressor} />
          <TrendChart />
          <StatusBadge status={patient.status} />
        </div>
      ))}
    </div>
  );
}

// ========================
// 환자 테이블 (레지던트용 - 간단)
// ========================
function PatientTableSimple() {
  const patients = [
    {
      id: "P-1024",
      bed: "ICU-A Bed 03",
      risk: 92,
      status: "critical",
      alert: "승압제 필요 예상",
    },
    {
      id: "P-2156",
      bed: "ICU-B Bed 12",
      risk: 87,
      status: "critical",
      alert: "사망 위험 높음",
    },
    {
      id: "P-3421",
      bed: "ICU-A Bed 07",
      risk: 79,
      status: "critical",
      alert: "인공호흡기 필요 예상",
    },
    {
      id: "P-4782",
      bed: "ICU-C Bed 05",
      risk: 74,
      status: "critical",
      alert: "승압제 필요 예상",
    },
    {
      id: "P-5098",
      bed: "ICU-B Bed 08",
      risk: 68,
      status: "warning",
      alert: "주의 관찰",
    },
  ];

  return (
    <div className="patient-table">
      <div className="patient-table-header simple">
        <span>Patient Info</span>
        <span>Risk Score</span>
        <span>Alert</span>
        <span>Status</span>
      </div>
      {patients.map((patient) => (
        <div key={patient.id} className="patient-table-row simple">
          <div className="patient-info">
            <span className="patient-id">{patient.id}</span>
            <span className="patient-bed">{patient.bed}</span>
          </div>
          <RiskBadge value={patient.risk} />
          <span className="alert-text">{patient.alert}</span>
          <StatusBadge status={patient.status} />
        </div>
      ))}
    </div>
  );
}

// ========================
// 가이드라인 허브 (레지던트용)
// ========================
function GuidelineHub() {
  return (
    <div className="guideline-hub">
      <h3>📋 권장 가이드라인</h3>

      <div className="guideline-card">
        <div className="guideline-header">
          <span className="guideline-tag critical">Critical</span>
          <span className="guideline-title">패혈증 초기 치료 지침</span>
        </div>
        <ol className="guideline-list">
          <li>1시간 이내 광범위 항생제 투여</li>
          <li>30ml/kg 수액 소생술</li>
          <li>MAP ≥ 65mmHg 목표</li>
          <li>Norepinephrine 1차 승압제로 권장</li>
        </ol>
        <p className="guideline-source">
          출처: 대한중환자의학회 2024 패혈증 가이드라인 p.23
        </p>
      </div>

      <div className="guideline-card">
        <div className="guideline-header">
          <span className="guideline-tag warning">Warning</span>
          <span className="guideline-title">기계환기 시작 기준</span>
        </div>
        <ol className="guideline-list">
          <li>PaO2 &lt; 60mmHg (FiO2 &gt; 0.5)</li>
          <li>PaCO2 &gt; 50mmHg with pH &lt; 7.30</li>
          <li>호흡수 &gt; 35/min</li>
          <li>호흡 보조근 사용</li>
        </ol>
        <p className="guideline-source">
          출처: 대한중환자의학회 기계환기 프로토콜 p.15
        </p>
      </div>
    </div>
  );
}

// ========================
// AI Hub (의사용)
// ========================
function AIHub() {
  return (
    <div className="ai-hub">
      <h3>🧠 AI Decision Support Hub</h3>
      <div className="ai-summary">
        <div className="ai-summary-header">
          <span>P-1024 환자 분석</span>
          <span className="ai-badge">AI Generated</span>
        </div>
        <p className="ai-summary-text">
          지난 4시간 MAP 하락(78→65mmHg)과 lactate 상승(1.2→2.8mmol/L), 소변량
          감소(40→15ml/hr)가 동반되며 pressor_start 위험이 급상승했습니다.
          <strong> Norepinephrine 준비를 권장합니다.</strong>
        </p>
        <div className="ai-shap">
          <span className="shap-title">주요 위험 요인 (SHAP)</span>
          <div className="shap-bars">
            <div className="shap-item">
              <span>Lactate 상승</span>
              <div className="shap-bar" style={{ width: "92%" }}></div>
              <span>+23%</span>
            </div>
            <div className="shap-item">
              <span>MAP 하락</span>
              <div className="shap-bar" style={{ width: "78%" }}></div>
              <span>+18%</span>
            </div>
            <div className="shap-item">
              <span>HR 변동성</span>
              <div className="shap-bar" style={{ width: "52%" }}></div>
              <span>+12%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ========================
// 시뮬레이션 제어 (관리자용)
// ========================
function SimulationControl() {
  return (
    <div className="simulation-control">
      <h3>⏱️ 시뮬레이션 제어</h3>

      <div className="sim-status">
        <div className="sim-time">
          <span className="sim-label">현재 시뮬레이션 시각</span>
          <span className="sim-value">2024-01-01 11:00:00</span>
        </div>
        <div className="sim-speed">
          <span className="sim-label">시뮬레이션 속도</span>
          <span className="sim-value">1분 = 1시간</span>
        </div>
      </div>

      <div className="sim-buttons">
        <button className="sim-btn primary">▶️ 다음 1시간</button>
        <button className="sim-btn primary">⏩ 다음 6시간</button>
        <button className="sim-btn secondary">⏸️ 일시정지</button>
        <button className="sim-btn danger">🔄 리셋</button>
      </div>

      <div className="sim-progress">
        <span className="sim-label">진행률</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: "35%" }}></div>
        </div>
        <span className="progress-text">Day 1 / 3 (35%)</span>
      </div>
    </div>
  );
}

// ========================
// 시스템 로그 (관리자용)
// ========================
function SystemLogs() {
  const logs = [
    {
      time: "14:32:15",
      type: "info",
      message: "Airflow DAG simulation_pipeline 실행 완료",
    },
    {
      time: "14:30:00",
      type: "info",
      message: "ML Service 예측 배치 처리 완료 (47명)",
    },
    {
      time: "14:28:45",
      type: "warning",
      message: "P-3421 센서 데이터 결측 감지",
    },
    { time: "14:25:12", type: "info", message: "Oracle DB 연결 갱신" },
    {
      time: "14:20:00",
      type: "critical",
      message: "P-1024 Critical Alert 발생 - 승압제 위험 96%",
    },
  ];

  return (
    <div className="system-logs">
      <h3>📜 시스템 로그</h3>
      <div className="log-list">
        {logs.map((log, idx) => (
          <div key={idx} className={`log-item ${log.type}`}>
            <span className="log-time">{log.time}</span>
            <span className={`log-type ${log.type}`}>
              {log.type.toUpperCase()}
            </span>
            <span className="log-message">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ========================
// 공통 컴포넌트
// ========================
function RiskBadge({ value }) {
  let className = "risk-badge ";
  if (value >= 80) className += "critical";
  else if (value >= 60) className += "high";
  else if (value >= 40) className += "warning";
  else className += "stable";

  return <span className={className}>{value}%</span>;
}

function StatusBadge({ status }) {
  const labels = {
    critical: "Critical",
    warning: "Warning",
    stable: "Stable",
  };
  return <span className={`status-badge ${status}`}>{labels[status]}</span>;
}

function TrendChart() {
  return (
    <div className="trend-chart">
      <div className="trend-line">
        <span>MAP:</span>
        <svg viewBox="0 0 60 20">
          <polyline
            points="0,15 15,12 30,8 45,14 60,10"
            fill="none"
            stroke="#ef4444"
            strokeWidth="2"
          />
        </svg>
      </div>
      <div className="trend-line">
        <span>Lactate:</span>
        <svg viewBox="0 0 60 20">
          <polyline
            points="0,10 15,8 30,12 45,6 60,4"
            fill="none"
            stroke="#22d3ee"
            strokeWidth="2"
          />
        </svg>
      </div>
    </div>
  );
}

// ========================
// 보호자 뷰
// ========================
function PatientView({ user, onLogout }) {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="dashboard-header-left">
          <div className="dashboard-logo">
            <div className="dashboard-logo-icon">⚡</div>
            <div className="dashboard-logo-text">
              <h1>EDCC</h1>
              <p>보호자 안내 시스템</p>
            </div>
          </div>
        </div>
        <div className="dashboard-header-right">
          <span style={{ color: "#888", fontSize: "14px" }}>{user.name}</span>
          <span style={{ cursor: "pointer" }} onClick={onLogout}>
            🚪
          </span>
        </div>
      </header>
      <div className="patient-view-container">
        <div className="patient-summary-card">
          <div className="patient-icon">🏥</div>
          <h2>환자 상태 안내</h2>
          <p className="patient-summary-text">
            현재 환자분의 상태가 변화하고 있어
            <br />
            의료진이 주의 깊게 모니터링하고 있습니다.
          </p>
          <p className="patient-summary-sub">
            변화가 있으면 바로 알려드리겠습니다.
          </p>
          <div className="patient-contact">
            <p>담당 의료진 문의</p>
            <button className="contact-btn">📞 간호사 호출</button>
          </div>
        </div>
        <p className="patient-note">
          ※ 자세한 수치는 담당 의료진에게 문의해주세요.
        </p>
      </div>
    </div>
  );
}

// ========================
// 헬퍼 함수
// ========================
function getRoleInitial(role) {
  const initials = {
    patient: "PT",
    resident: "RS",
    doctor: "DR",
    admin: "AD",
  };
  return initials[role] || role.toUpperCase().slice(0, 2);
}

export default Dashboard;
