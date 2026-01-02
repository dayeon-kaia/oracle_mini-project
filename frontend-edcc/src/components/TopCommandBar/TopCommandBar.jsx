import React, { useState } from 'react';
import AISearchBar from './AISearchBar';
import styles from './TopCommandBar.module.css';

const TopCommandBar = ({ onSearch }) => {
    return (
        <header className={styles.commandBar}>
            <div className={styles.container}>
                {/* Logo / Title */}
                <div className={styles.logo}>
                    <div className={styles.logoIcon}>
                        <span className="neon-text-ai">🏥</span>
                    </div>
                    <div className={styles.logoText}>
                        <h1 className={styles.title}>
                            <span className="neon-text-ai">EDCC</span>
                        </h1>
                        <p className={styles.subtitle}>Early Deterioration Command Center</p>
                    </div>
                </div>

                {/* AI Search Bar (Center) */}
                <AISearchBar onSearch={onSearch} />

                {/* User Profile / Settings */}
                <div className={styles.userSection}>
                    <div className={`${styles.statusIndicator} scan-line`}>
                        <span className={styles.statusDot}></span>
                        <span className={styles.statusText}>System Active</span>
                    </div>
                    <button className={`glass-btn ${styles.userBtn}`}>
                        <span>Dr. Kim</span>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <circle cx="10" cy="6" r="3" stroke="currentColor" strokeWidth="1.5" />
                            <path d="M15 14C15 11.7909 12.7614 10 10 10C7.23858 10 5 11.7909 5 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    </button>
                </div>
            </div>
        </header>
    );
};

export default TopCommandBar;
