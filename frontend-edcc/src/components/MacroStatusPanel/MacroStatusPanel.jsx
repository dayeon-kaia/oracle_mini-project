import React, { useState, useEffect } from 'react';
import StatusWidget from './StatusWidget';
import styles from './MacroStatusPanel.module.css';

const MacroStatusPanel = ({ onFilterClick }) => {
    // Mock data - will be replaced with real API
    const [stats, setStats] = useState({
        totalMonitored: 42,
        criticalAlerts: 5,
        upcomingInterventions: 12,
        dataIssues: 3,
    });

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
                    sublabel="24h Mortality High"
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
                    <span className={styles.metricValue}>0.42</span>
                </div>
                <div className={styles.metric}>
                    <span className={styles.metricLabel}>Last Update</span>
                    <span className={styles.metricValue}>30s ago</span>
                </div>
            </div>
        </div>
    );
};

export default MacroStatusPanel;
