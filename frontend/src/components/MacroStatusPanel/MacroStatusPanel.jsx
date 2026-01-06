import React, { useState, useEffect } from 'react';
import StatusWidget from './StatusWidget';
import styles from './MacroStatusPanel.module.css';
import api from '../../services/api';

const MacroStatusPanel = ({ onFilterClick }) => {
    const [stats, setStats] = useState({
        totalMonitored: 0,
        criticalAlerts: 0,
        upcomingInterventions: 0,
        dataIssues: 0,
        avgRiskScore: 0,
        lastUpdate: 'Loading...'
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/patients');
                const patients = response.data.patients;

                // Calculate statistics from real patient data
                const totalMonitored = patients.length;

                // Critical: CRITICAL risk_level
                const criticalAlerts = patients.filter(p =>
                    p.risk_level === 'CRITICAL'
                ).length;

                // Upcoming Interventions: HIGH or MEDIUM risk levels
                const upcomingInterventions = patients.filter(p =>
                    p.risk_level === 'HIGH' || p.risk_level === 'MEDIUM'
                ).length;

                // Data Issues: placeholder (can be calculated based on data_quality_flags if available)
                const dataIssues = patients.filter(p =>
                    p.data_quality_flags && p.data_quality_flags.length > 0
                ).length;

                // Average Risk Score (using mortality as proxy)
                const avgRiskScore = patients.reduce((sum, p) =>
                    sum + p.risk_mortality_24h, 0) / patients.length;

                setStats({
                    totalMonitored,
                    criticalAlerts,
                    upcomingInterventions,
                    dataIssues,
                    avgRiskScore: avgRiskScore.toFixed(2),
                    lastUpdate: new Date().toLocaleTimeString('ko-KR', {
                        hour: '2-digit',
                        minute: '2-digit'
                    })
                });
            } catch (error) {
                console.error('Failed to fetch patient stats:', error);
            }
        };

        fetchStats();

        // Refresh every 30 seconds
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className={styles.panel}>
            <h2 className={styles.title}>Command Center Overview</h2>

            <div className={styles.widgets}>
                <StatusWidget
                    icon="👥"
                    label="Total Monitored"
                    value={stats.totalMonitored}
                    status="info"
                    onClick={() => onFilterClick(null)}
                />

                <StatusWidget
                    icon="🚨"
                    label="Critical Alerts"
                    sublabel="예후 악화 가능성 높음"
                    value={stats.criticalAlerts}
                    status="critical"
                    onClick={() => onFilterClick('critical')}
                    pulse
                />

                <StatusWidget
                    icon="⚡"
                    label="Upcoming Interventions"
                    sublabel="12h Vent/Pressor"
                    value={stats.upcomingInterventions}
                    status="warning"
                    onClick={() => onFilterClick('warning')}
                />

                <StatusWidget
                    icon="⚠️"
                    label="Data Integrity Issues"
                    sublabel="Sensor Check Needed"
                    value={stats.dataIssues}
                    status="attention"
                    onClick={() => onFilterClick('data-issues')}
                />
            </div>

            {/* Mini Metrics */}
            <div className={styles.miniMetrics}>
                <div className={styles.metric}>
                    <span className={styles.metricLabel}>Avg Risk Score</span>
                    <span className={styles.metricValue}>{stats.avgRiskScore}</span>
                </div>
                <div className={styles.metric}>
                    <span className={styles.metricLabel}>Last Update</span>
                    <span className={styles.metricValue}>{stats.lastUpdate}</span>
                </div>
            </div>
        </div>
    );
};

export default MacroStatusPanel;
