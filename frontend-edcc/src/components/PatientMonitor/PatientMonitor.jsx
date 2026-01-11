import React, { useState, useEffect } from 'react';
import PatientRow from './PatientRow';
import styles from './PatientMonitor.module.css';

// Mock patient data
const mockPatients = [
    {
        patient_id: 'P-1024',
        location: 'ICU-A-12',
        composite_risk: 0.92,
        mortality_risk: 0.89,
        vent_risk: 0.78,
        pressor_risk: 0.92,
        map_trend: [65, 62, 58, 55, 52, 58],
        lactate_trend: [2.1, 2.8, 3.5, 4.2, 4.5, 4.2],
        data_quality_issues: ['MAP 센서 간헐적 결측'],
        status: 'critical'
    },
    {
        patient_id: 'P-0847',
        location: 'ICU-B-05',
        composite_risk: 0.78,
        mortality_risk: 0.72,
        vent_risk: 0.82,
        pressor_risk: 0.68,
        map_trend: [72, 70, 68, 65, 67, 70],
        lactate_trend: [1.8, 2.2, 2.5, 2.8, 2.6, 2.4],
        data_quality_issues: [],
        status: 'warning'
    },
    {
        patient_id: 'P-1532',
        location: 'ICU-A-08',
        composite_risk: 0.65,
        mortality_risk: 0.58,
        vent_risk: 0.71,
        pressor_risk: 0.52,
        map_trend: [75, 74, 73, 72, 74, 75],
        lactate_trend: [1.5, 1.6, 1.8, 1.7, 1.6, 1.5],
        data_quality_issues: [],
        status: 'warning'
    },
    {
        patient_id: 'P-0923',
        location: 'ICU-C-14',
        composite_risk: 0.42,
        mortality_risk: 0.38,
        vent_risk: 0.45,
        pressor_risk: 0.41,
        map_trend: [82, 80, 81, 83, 82, 84],
        lactate_trend: [1.2, 1.3, 1.2, 1.1, 1.2, 1.1],
        data_quality_issues: [],
        status: 'stable'
    },
];

const PatientMonitor = ({ searchQuery, filterStatus, onPatientSelect, selectedPatientId }) => {
    const [patients, setPatients] = useState(mockPatients);
    const [sortBy, setSortBy] = useState('composite_risk');
    const [sortOrder, setSortOrder] = useState('desc');

    // Filter patients based on status
    const filteredPatients = patients.filter(patient => {
        if (!filterStatus) return true;
        if (filterStatus === 'critical') return patient.status === 'critical';
        if (filterStatus === 'warning') return patient.status === 'warning';
        if (filterStatus === 'data-issues') return patient.data_quality_issues.length > 0;
        return true;
    });

    // Sort patients
    const sortedPatients = [...filteredPatients].sort((a, b) => {
        const multiplier = sortOrder === 'desc' ? -1 : 1;
        return (a[sortBy] - b[sortBy]) * multiplier;
    });

    return (
        <div className={styles.monitor}>
            <div className={styles.header}>
                <div>
                    <h2 className={styles.title}>Active Patient Monitor</h2>
                    <p className={styles.subtitle}>
                        Showing {sortedPatients.length} of {patients.length} patients • Sorted by Risk Score
                    </p>
                </div>

                <div className={styles.controls}>
                    <button className="glass-btn">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M2 5h12M2 8h8M2 11h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                        Filter
                    </button>
                    <button className="glass-btn">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M14 2L8 14L6 8L2 6L14 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
                        </svg>
                        Refresh
                    </button>
                </div>
            </div>

            <div className={styles.tableContainer}>
                <table className={`glass-table ${styles.table}`}>
                    <thead>
                        <tr>
                            <th>Patient Info</th>
                            <th>Composite Risk</th>
                            <th>Mortality (24h)</th>
                            <th>Vent Start (12h)</th>
                            <th>Pressor Start (12h)</th>
                            <th>MAP Trend</th>
                            <th>Lactate Trend</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedPatients.map((patient) => (
                            <PatientRow
                                key={patient.patient_id}
                                patient={patient}
                                isSelected={patient.patient_id === selectedPatientId}
                                onClick={() => onPatientSelect(patient)}
                            />
                        ))}
                    </tbody>
                </table>

                {sortedPatients.length === 0 && (
                    <div className={styles.empty}>
                        <span className={styles.emptyIcon}>🔍</span>
                        <p className={styles.emptyText}>No patients match the current filter</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PatientMonitor;
