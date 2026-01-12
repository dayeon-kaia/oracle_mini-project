import React from 'react';
import RiskIndicator from './RiskIndicator';
import Sparkline from './Sparkline';
import styles from './PatientRow.module.css';

const PatientRow = ({ patient, isSelected, onClick }) => {
    const getStatusClass = () => {
        switch (patient.status) {
            case 'critical':
                return styles.critical;
            case 'warning':
                return styles.warning;
            case 'stable':
                return styles.stable;
            default:
                return '';
        }
    };

    return (
        <tr
            className={`${styles.row} ${getStatusClass()} ${isSelected ? styles.selected : ''}`}
            onClick={onClick}
        >
            {/* Patient Info */}
            <td className={styles.patientInfo}>
                <div className={styles.patientId}>{patient.patient_id}</div>
                <div className={styles.location}>{patient.location}</div>
                {patient.data_quality_issues.length > 0 && (
                    <div className={styles.dataWarning} title={patient.data_quality_issues.join(', ')}>
                        ⚠️ Sensor Check
                    </div>
                )}
            </td>

            {/* Composite Risk */}
            <td>
                <div className={styles.compositeRisk}>
                    <RiskIndicator value={patient.composite_risk} size="large" />
                    <span className={styles.riskText}>
                        {(patient.composite_risk * 100).toFixed(0)}%
                    </span>
                </div>
            </td>

            {/* Mortality Risk */}
            <td>
                <RiskIndicator value={patient.mortality_risk} label="Mortality" />
            </td>

            {/* Vent Risk */}
            <td>
                <RiskIndicator value={patient.vent_risk} label="Vent" />
            </td>

            {/* Pressure Risk */}
            <td>
                <RiskIndicator value={patient.pressor_risk} label="Pressor" />
            </td>

            {/* MAP Trend */}
            <td>
                <Sparkline
                    data={patient.map_trend}
                    color="cyan"
                    label="MAP"
                />
            </td>

            {/* Lactate Trend */}
            <td>
                <Sparkline
                    data={patient.lactate_trend}
                    color="amber"
                    label="Lactate"
                />
            </td>

            {/* Status */}
            <td>
                <div className={`${styles.statusBadge} ${styles[patient.status]}`}>
                    {patient.status}
                </div>
            </td>
        </tr>
    );
};

export default PatientRow;
