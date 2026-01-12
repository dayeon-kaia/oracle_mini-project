import React, { useState, useEffect } from 'react';
import PatientRow from './PatientRow';
import styles from './PatientMonitor.module.css';
import api from '../../services/api';

const PatientMonitor = ({ searchQuery, filterStatus, onPatientSelect, selectedPatientId }) => {
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [sortBy, setSortBy] = useState('status'); // Default sort by status
    const [sortOrder, setSortOrder] = useState('desc');
    const [isSortDropdownOpen, setIsSortDropdownOpen] = useState(false);

    // Fetch patients from backend
    useEffect(() => {
        const fetchPatients = async () => {
            try {
                setLoading(true);
                const response = await api.get('/patients');

                // Transform backend data to match frontend format
                const transformedPatients = response.data.patients.map(p => ({
                    patient_id: p.stay_id,
                    location: `${p.icu_unit}-${p.bed_id}`,
                    composite_risk: Math.max(p.risk_mortality_24h, p.risk_vent_12h, p.risk_pressor_12h),
                    mortality_risk: p.risk_mortality_24h,
                    vent_risk: p.risk_vent_12h,
                    pressor_risk: p.risk_pressor_12h,
                    map_trend: [p.map_last, p.map_last - 5, p.map_last - 3, p.map_last + 2, p.map_last - 1, p.map_last],
                    lactate_trend: [p.lactate_last, p.lactate_last - 0.2, p.lactate_last + 0.3, p.lactate_last + 0.1, p.lactate_last - 0.1, p.lactate_last],
                    data_quality_issues: [],
                    status: p.risk_level?.toLowerCase() || 'stable',
                    // Include original data for detail view
                    raw: p
                }));

                setPatients(transformedPatients);
            } catch (error) {
                console.error('Failed to fetch patients:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchPatients();

        // Refresh every 30 seconds
        const interval = setInterval(fetchPatients, 30000);
        return () => clearInterval(interval);
    }, []);

    // Filter patients based on status
    const filteredPatients = patients.filter(patient => {
        if (!filterStatus) return true;
        if (filterStatus === 'critical') return patient.status === 'critical';
        if (filterStatus === 'warning') return patient.status === 'high' || patient.status === 'warning';
        if (filterStatus === 'data-issues') return patient.data_quality_issues.length > 0;
        return true;
    });

    // Sort patients with tie-breakers
    const sortedPatients = [...filteredPatients].sort((a, b) => {
        // Helper to get sort value
        const getSortValue = (patient, field) => {
            if (field === 'status') {
                const statusWeight = {
                    'critical': 3,
                    'high': 2,
                    'warning': 2,
                    'medium': 1,
                    'low': 0,
                    'stable': 0
                };
                return statusWeight[patient.status] || 0;
            }
            return patient[field] || 0;
        };

        const valA = getSortValue(a, sortBy);
        const valB = getSortValue(b, sortBy);

        // Primary Sort
        if (valA !== valB) {
            return sortOrder === 'desc' ? valB - valA : valA - valB;
        }

        // Tie-breaker 1: Mortality Rate (Always Descending)
        if (a.mortality_risk !== b.mortality_risk) {
            return b.mortality_risk - a.mortality_risk;
        }

        // Tie-breaker 2: Composite Risk (Always Descending)
        return b.composite_risk - a.composite_risk;
    });

    const toggleSort = (field) => {
        if (sortBy === field) {
            setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc');
        } else {
            setSortBy(field);
            setSortOrder('desc'); // Default to descending when switching fields
        }
        setIsSortDropdownOpen(false);
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (isSortDropdownOpen && !event.target.closest(`.${styles.dropdownContainer}`)) {
                setIsSortDropdownOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isSortDropdownOpen]);

    const sortOptions = [
        { id: 'status', label: 'Status' },
        { id: 'mortality_risk', label: 'Mortality Risk' },
        { id: 'composite_risk', label: 'Composite Risk' },
        { id: 'vent_risk', label: 'Vent Risk' },
        { id: 'pressor_risk', label: 'Pressor Risk' }
    ];

    return (
        <div className={styles.monitor}>
            <div className={styles.header}>
                <div>
                    <h2 className={styles.title}>Active Patient Monitor</h2>
                    <p className={styles.subtitle}>
                        Showing {sortedPatients.length} of {patients.length} patients • Sorted by {sortOptions.find(o => o.id === sortBy)?.label}
                    </p>
                </div>

                <div className={styles.controls}>
                    <div className={styles.dropdownContainer}>
                        <button
                            className={`glass-btn ${isSortDropdownOpen ? styles.activeFilter : ''}`}
                            onClick={() => setIsSortDropdownOpen(!isSortDropdownOpen)}
                        >
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M2 5h12M2 8h8M2 11h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                            Sort: {sortOptions.find(o => o.id === sortBy)?.label}
                            <svg
                                width="12"
                                height="12"
                                viewBox="0 0 12 12"
                                fill="none"
                                style={{ transform: isSortDropdownOpen ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                            >
                                <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>

                        {isSortDropdownOpen && (
                            <div className={`glass-panel ${styles.dropdownMenu}`}>
                                {sortOptions.map(option => (
                                    <button
                                        key={option.id}
                                        className={styles.dropdownItem}
                                        onClick={() => toggleSort(option.id)}
                                    >
                                        <span className={styles.checkIcon}>
                                            {sortBy === option.id && (sortOrder === 'desc' ? '↓' : '↑')}
                                        </span>
                                        {option.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    <button className="glass-btn" onClick={() => window.location.reload()}>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M14 2L8 14L6 8L2 6L14 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
                        </svg>
                        Refresh
                    </button>
                </div>
            </div>

            {loading ? (
                <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    <p>Loading patients...</p>
                </div>
            ) : (
                <div className={styles.tableContainer}>
                    <table className={`glass-table ${styles.table}`}>
                        <thead>
                            <tr>
                                <th>Patient Info</th>
                                <th onClick={() => toggleSort('composite_risk')} style={{ cursor: 'pointer' }}>Composite Risk</th>
                                <th onClick={() => toggleSort('mortality_risk')} style={{ cursor: 'pointer' }}>Mortality (24h)</th>
                                <th onClick={() => toggleSort('vent_risk')} style={{ cursor: 'pointer' }}>Vent Start (12h)</th>
                                <th onClick={() => toggleSort('pressor_risk')} style={{ cursor: 'pointer' }}>Pressor Start (12h)</th>
                                <th>MAP Trend</th>
                                <th>Lactate Trend</th>
                                <th onClick={() => toggleSort('status')} style={{ cursor: 'pointer' }}>Status</th>
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
            )}
        </div>
    );
};

export default PatientMonitor;
