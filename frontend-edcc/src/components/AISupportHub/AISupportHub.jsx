import React, { useState } from 'react';
import ClinicalExplain from './ClinicalExplain';
import ProtocolGuide from './ProtocolGuide';
import GuardianReport from './GuardianReport';
import styles from './AISupportHub.module.css';

const AISupportHub = ({ patient, onClose }) => {
    const [activeTab, setActiveTab] = useState('clinical');

    return (
        <>
            {/* Overlay */}
            <div className={styles.overlay} onClick={onClose}></div>

            {/* Sliding Panel */}
            <aside className={styles.panel}>
                {/* Header */}
                <div className={styles.header}>
                    <div className={styles.headerContent}>
                        <div className={styles.patientBadge}>
                            <span className={styles.patientIcon}>👤</span>
                            <div>
                                <div className={styles.patientId}>{patient.patient_id}</div>
                                <div className={styles.patientLocation}>{patient.location}</div>
                            </div>
                        </div>

                        <button className={`glass-btn ${styles.closeBtn}`} onClick={onClose}>
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        </button>
                    </div>

                    {/* Alert Badge */}
                    {patient.status === 'critical' && (
                        <div className={`${styles.alert} neon-glow-critical`}>
                            🚨 High Risk: Pressor Start in 2h
                        </div>
                    )}

                    {/* Tabs */}
                    <div className={styles.tabs}>
                        <button
                            className={`${styles.tab} ${activeTab === 'clinical' ? styles.active : ''}`}
                            onClick={() => setActiveTab('clinical')}
                        >
                            <span className="neon-text-ai">✨</span>
                            Clinical Explain
                        </button>
                        <button
                            className={`${styles.tab} ${activeTab === 'protocol' ? styles.active : ''}`}
                            onClick={() => setActiveTab('protocol')}
                        >
                            📋 Protocol Guide
                        </button>
                        <button
                            className={`${styles.tab} ${activeTab === 'guardian' ? styles.active : ''}`}
                            onClick={() => setActiveTab('guardian')}
                        >
                            👨‍👩‍👧 Guardian Report
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className={styles.content}>
                    {activeTab === 'clinical' && <ClinicalExplain patient={patient} />}
                    {activeTab === 'protocol' && <ProtocolGuide patient={patient} />}
                    {activeTab === 'guardian' && <GuardianReport patient={patient} />}
                </div>
            </aside>
        </>
    );
};

export default AISupportHub;
