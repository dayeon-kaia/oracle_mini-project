import React from 'react';
import styles from './ClinicalExplain.module.css';

const ClinicalExplain = ({ patient }) => {
    // Mock SHAP data
    const shapFeatures = [
        { feature: 'MAP (평균동맥압)', value: patient.map_trend[patient.map_trend.length - 1], contribution: -0.35 },
        { feature: 'Lactate (젖산)', value: patient.lactate_trend[patient.lactate_trend.length - 1], contribution: 0.28 },
        { feature: 'Heart Rate', value: 120, contribution: 0.15 },
        { feature: 'Urine Output', value: 0.3, contribution: -0.12 },
        { feature: 'WBC', value: 18, contribution: 0.08 },
    ];

    const maxContribution = Math.max(...shapFeatures.map(f => Math.abs(f.contribution)));

    return (
        <div className={styles.container}>
            {/* AI Summary */}
            <div className={`${styles.section} neon-border-ai`}>
                <div className={styles.sectionHeader}>
                    <span className="neon-text-ai">✨</span>
                    <h3>AI Summary & SHAP Insights</h3>
                    <span className={styles.badge}>AI-Generated</span>
                </div>

                <p className={styles.summary}>
                    지난 4시간 동안 <strong className="neon-text-critical">평균동맥압(MAP) 15% 하락</strong> 및{' '}
                    <strong className="neon-text-warning">젖산 수치 상승 (4.2 mmol/L)</strong>이 주된 원인으로,{' '}
                    승압제 투여 가능성이 <strong className="neon-text-critical">높은 수준으로 상승</strong>하여 추가 평가가 필요합니다.
                </p>
            </div>

            {/* SHAP Contribution Chart */}
            <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Top Contributing Features</h3>

                <div className={styles.shapChart}>
                    {shapFeatures.map((item, index) => (
                        <div key={index} className={styles.shapItem}>
                            <div className={styles.shapLabel}>
                                <span className={styles.featureName}>{item.feature}</span>
                                <span className={styles.featureValue}>{item.value.toFixed(1)}</span>
                            </div>

                            <div className={styles.barContainer}>
                                <div
                                    className={`${styles.bar} ${item.contribution > 0 ? styles.positive : styles.negative}`}
                                    style={{
                                        width: `${(Math.abs(item.contribution) / maxContribution) * 100}%`,
                                        [item.contribution > 0 ? 'marginLeft' : 'marginRight']: 'auto'
                                    }}
                                >
                                    <span className={styles.barValue}>
                                        {item.contribution > 0 ? '+' : ''}{item.contribution.toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recommended Actions */}
            <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Recommended Actions</h3>

                <div className={styles.actions}>
                    <div className={styles.actionItem}>
                        <span className={styles.actionIcon}>🔍</span>
                        <span>혈압 및 신체검진 재확인 필요</span>
                    </div>
                    <div className={styles.actionItem}>
                        <span className={styles.actionIcon}>💉</span>
                        <span>MAP 센서 재부착 및 측정 확인</span>
                    </div>
                    <div className={styles.actionItem}>
                        <span className={styles.actionIcon}>📊</span>
                        <span>젖산 수치 trending 모니터링</span>
                    </div>
                </div>
            </div>

            {/* Data Quality Alerts */}
            {patient.data_quality_issues.length > 0 && (
                <div className={`${styles.section} ${styles.warning}`}>
                    <h3 className={styles.sectionTitle}>⚠️ Data Quality Alerts</h3>
                    <ul className={styles.alertList}>
                        {patient.data_quality_issues.map((issue, index) => (
                            <li key={index}>{issue}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default ClinicalExplain;
