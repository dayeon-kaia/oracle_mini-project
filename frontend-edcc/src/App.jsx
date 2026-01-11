import React, { useState } from 'react';
import './styles/globals.css';
import './styles/glass.css';
import './styles/neon.css';
import TopCommandBar from './components/TopCommandBar/TopCommandBar';
import MacroStatusPanel from './components/MacroStatusPanel/MacroStatusPanel';
import PatientMonitor from './components/PatientMonitor/PatientMonitor';
import AISupportHub from './components/AISupportHub/AISupportHub';
import styles from './App.module.css';

function App() {
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState(null);

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
  };

  const handleClosePanel = () => {
    setSelectedPatient(null);
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    // TODO: Implement natural language query processing
    console.log('Search query:', query);
  };

  const handleMacroClick = (filterType) => {
    setFilterStatus(filterType);
  };

  return (
    <div className={styles.app}>
      {/* Top Command Bar */}
      <TopCommandBar onSearch={handleSearch} />

      {/* Main Dashboard Layout */}
      <div className={styles.dashboard}>
        {/* Left Side: Macro Status Panel */}
        <aside className={styles.sidebar}>
          <MacroStatusPanel onFilterClick={handleMacroClick} />
        </aside>

        {/* Center: Patient Monitor */}
        <main className={styles.main}>
          <PatientMonitor
            searchQuery={searchQuery}
            filterStatus={filterStatus}
            onPatientSelect={handlePatientSelect}
            selectedPatientId={selectedPatient?.patient_id}
          />
        </main>

        {/* Right: AI Support Hub (Sliding Panel) */}
        {selectedPatient && (
          <AISupportHub
            patient={selectedPatient}
            onClose={handleClosePanel}
          />
        )}
      </div>
    </div>
  );
}

export default App;
