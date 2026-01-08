import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import TopCommandBar from "../../components/TopCommandBar/TopCommandBar";
import MacroStatusPanel from "../../components/MacroStatusPanel/MacroStatusPanel";
import PatientMonitor from "../../components/PatientMonitor/PatientMonitor";
import AISupportHub from "../../components/AISupportHub/AISupportHub";
import QueryConsole from "../../components/QueryConsole/QueryConsole";
import "./Dashboard.css";
import "../../styles/globals.css";
import "../../styles/glass.css";
import "../../styles/neon.css";

function Dashboard() {
  const { role } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState(null);
  const [viewMode, setViewMode] = useState("dashboard"); // 'dashboard' | 'nlq' | 'patient_detail'

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (!savedUser) {
      navigate("/login");
      return;
    }

    const userData = JSON.parse(savedUser);

    // Redirect to correct role if mismatch
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

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
    setViewMode('patient_detail');
  };

  const handleClosePanel = () => {
    setSelectedPatient(null);
    setViewMode('dashboard');
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    setViewMode("nlq");
    console.log("Search query:", query);
  };

  const handleToggleNLQ = () => {
    setViewMode(prev => prev === 'dashboard' ? 'nlq' : 'dashboard');
  };

  const handleMacroClick = (filterType) => {
    setFilterStatus(filterType);
  };

  if (!user) return null;

  // Doctor View: Full EDCC Dashboard
  if (role === "doctor") {
    return (
      <div className="dashboard-container">
        <TopCommandBar user={user} onLogout={handleLogout} onSearch={handleSearch} onToggleNLQ={handleToggleNLQ} />

        {viewMode === 'nlq' ? (
          <div className="dashboard-main" style={{ display: 'block', height: 'calc(100vh - 60px)', overflow: 'hidden', padding: '1rem' }}>
            <QueryConsole initialQuery={searchQuery} />
          </div>
        ) : viewMode === 'patient_detail' && selectedPatient ? (
          <div className="dashboard-main" style={{ display: 'block', height: 'calc(100vh - 60px)', overflow: 'hidden' }}>
            <AISupportHub patient={selectedPatient} onClose={handleClosePanel} isFullScreen={true} />
          </div>
        ) : (
          <div className="dashboard-main">
            <aside className="dashboard-sidebar">
              <MacroStatusPanel onFilterClick={handleMacroClick} />
            </aside>

            <main className="dashboard-content">
              <PatientMonitor
                searchQuery={searchQuery}
                filterStatus={filterStatus}
                onPatientSelect={handlePatientSelect}
                selectedPatientId={selectedPatient?.patient_id}
              />
            </main>
          </div>
        )}

        <Footer />
      </div>
    );
  }

  // Nurse View: Simplified Dashboard (no AI Support Hub, simpler top bar)
  if (role === "nurse") {
    return (
      <div className="dashboard-container">
        <TopCommandBar user={user} onLogout={handleLogout} showSearch={false} />

        <div className="dashboard-main">
          <aside className="dashboard-sidebar">
            <NurseStatusPanel />
          </aside>

          <main className="dashboard-content">
            <PatientMonitor
              searchQuery=""
              filterStatus={filterStatus}
              onPatientSelect={() => { }} // Nurse can't open AI support hub
              selectedPatientId={null}
            />
            <GuidelineCards />
          </main>
        </div>

        <Footer />
      </div>
    );
  }

  // If role is not recognized, redirect to login
  navigate("/login");
  return null;
}

// Simplified Nurse Status Panel
function NurseStatusPanel() {
  const widgets = [
    { title: "Active Patients", value: "47", icon: "📊", color: "purple" },
    { title: "Critical", value: "5", icon: "⚠️", color: "red" },
    { title: "High Risk", value: "12", icon: "🔸", color: "orange" },
    { title: "Stable", value: "30", icon: "✓", color: "cyan" },
  ];

  return (
    <div className="nurse-status-panel">
      <p className="panel-title">Patient Overview</p>
      {widgets.map((widget, idx) => (
        <div key={idx} className={`status-widget ${widget.color}`}>
          <div className="widget-icon">{widget.icon}</div>
          <div className="widget-value">{widget.value}</div>
          <div className="widget-title">{widget.title}</div>
        </div>
      ))}
    </div>
  );
}

// Guideline Cards for Nurses
function GuidelineCards() {
  return (
    <div className="guideline-cards">
      <h3>📋 핵심 가이드라인</h3>

      <div className="guideline-card critical">
        <div className="guideline-header">
          <span className="guideline-tag">Critical</span>
          <span className="guideline-title">패혈증 초기 대응</span>
        </div>
        <ul className="guideline-list">
          <li>1시간 이내 광범위 항생제 투여</li>
          <li>30ml/kg 수액 소생술</li>
          <li>MAP ≥ 65mmHg 목표</li>
          <li>담당 의사에게 즉시 보고</li>
        </ul>
      </div>

      <div className="guideline-card warning">
        <div className="guideline-header">
          <span className="guideline-tag">Warning</span>
          <span className="guideline-title">호흡기 모니터링</span>
        </div>
        <ul className="guideline-list">
          <li>호흡수 &gt; 30/min 주의 관찰</li>
          <li>SpO2 &lt; 92% 산소 공급</li>
          <li>호흡 보조근 사용 시 의사 호출</li>
        </ul>
      </div>
    </div>
  );
}

// Footer Component
function Footer() {
  return (
    <footer className="dashboard-footer">
      <div className="footer-content">
        <div className="footer-disclaimer">
          <span className="disclaimer-icon">⚕️</span>
          <span>본 시스템은 의사 결정 보조 도구입니다. 최종 판단은 의사에게 있습니다.</span>
        </div>
        <div className="footer-copyright">
          © {new Date().getFullYear()} fire4birds. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default Dashboard;
