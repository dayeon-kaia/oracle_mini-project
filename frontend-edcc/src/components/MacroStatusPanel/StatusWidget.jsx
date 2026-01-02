import React from 'react';
import styles from './StatusWidget.module.css';

const StatusWidget = ({
    icon,
    label,
    sublabel,
    value,
    status = 'info',
    onClick,
    pulse = false
}) => {
    const getStatusClass = () => {
        switch (status) {
            case 'critical':
                return styles.critical;
            case 'warning':
                return styles.warning;
            case 'attention':
                return styles.attention;
            default:
                return styles.info;
        }
    };

    return (
        <button
            className={`${styles.widget} ${getStatusClass()} ${pulse ? styles.pulse : ''}`}
            onClick={onClick}
        >
            <div className={styles.iconContainer}>
                <span className={styles.icon}>{icon}</span>
            </div>

            <div className={styles.content}>
                <div className={styles.labelContainer}>
                    <span className={styles.label}>{label}</span>
                    {sublabel && <span className={styles.sublabel}>{sublabel}</span>}
                </div>

                <div className={styles.value}>
                    {value}
                </div>
            </div>

            {status === 'critical' && (
                <div className={styles.indicator}></div>
            )}
        </button>
    );
};

export default StatusWidget;
