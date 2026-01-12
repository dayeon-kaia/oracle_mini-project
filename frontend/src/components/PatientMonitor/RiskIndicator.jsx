import React from 'react';
import styles from './RiskIndicator.module.css';

const RiskIndicator = ({ value, size = 'normal', label }) => {
    const percentage = value * 100;

    const getRiskLevel = () => {
        if (value >= 0.85) return 'critical';
        if (value >= 0.60) return 'warning';
        return 'stable';
    };

    const riskLevel = getRiskLevel();
    const circumference = 2 * Math.PI * 18; // radius = 18
    const dashOffset = circumference - (percentage / 100) * circumference;

    return (
        <div className={`${styles.indicator} ${styles[size]}`}>
            <svg
                width={size === 'large' ? '50' : '40'}
                height={size === 'large' ? '50' : '40'}
                viewBox="0 0 40 40"
                className={styles.svg}
            >
                {/* Background circle */}
                <circle
                    cx="20"
                    cy="20"
                    r="18"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth="3"
                />

                {/* Progress circle */}
                <circle
                    cx="20"
                    cy="20"
                    r="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={dashOffset}
                    className={`${styles.progress} ${styles[riskLevel]}`}
                    transform="rotate(-90 20 20)"
                />

                {/* Center text */}
                <text
                    x="20"
                    y="20"
                    textAnchor="middle"
                    dominantBaseline="central"
                    className={styles.text}
                    fontSize="10"
                    fontWeight="600"
                >
                    {percentage.toFixed(0)}
                </text>
            </svg>

            {label && (
                <span className={styles.label}>{label}</span>
            )}
        </div>
    );
};

export default RiskIndicator;
