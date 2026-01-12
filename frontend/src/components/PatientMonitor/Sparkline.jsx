import React from 'react';
import styles from './Sparkline.module.css';

const Sparkline = ({ data, color = 'cyan', label }) => {
    if (!data || data.length === 0) return null;

    const width = 80;
    const height = 30;
    const padding = 2;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    // Create SVG path
    const points = data.map((value, index) => {
        const x = (index / (data.length - 1)) * (width - padding * 2) + padding;
        const y = height - padding - ((value - min) / range) * (height - padding * 2);
        return `${x},${y}`;
    });

    const pathData = `M ${points.join(' L ')}`;

    // Determine color based on trend
    const getColorClass = () => {
        const trend = data[data.length - 1] - data[0];
        if (color === 'cyan') return styles.cyan;
        if (color === 'amber') return styles.amber;
        if (trend > 0 && color === 'auto') return styles.warning;
        if (trend < 0 && color === 'auto') return styles.stable;
        return styles.cyan;
    };

    return (
        <div className={styles.sparkline}>
            <svg
                width={width}
                height={height}
                viewBox={`0 0 ${width} ${height}`}
                className={styles.svg}
            >
                {/* Area fill */}
                <path
                    d={`${pathData} L ${width - padding},${height - padding} L ${padding},${height - padding} Z`}
                    fill="currentColor"
                    opacity="0.1"
                    className={getColorClass()}
                />

                {/* Line */}
                <path
                    d={pathData}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    vectorEffect="non-scaling-stroke"
                    className={`${styles.line} ${getColorClass()}`}
                />

                {/* Last point dot */}
                <circle
                    cx={points[points.length - 1].split(',')[0]}
                    cy={points[points.length - 1].split(',')[1]}
                    r="2"
                    fill="currentColor"
                    className={getColorClass()}
                />
            </svg>

            {label && (
                <span className={styles.label}>
                    {data[data.length - 1].toFixed(1)}
                </span>
            )}
        </div>
    );
};

export default Sparkline;
