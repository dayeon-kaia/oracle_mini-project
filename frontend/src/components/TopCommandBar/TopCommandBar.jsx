import React, { useState } from 'react';
import { ThemeToggle } from '../ThemeToggle/ThemeToggle';
import AISearchBar from './AISearchBar';
import styles from './TopCommandBar.module.css';

const TopCommandBar = ({ user, onLogout, onSearch, onToggleNLQ, onHome, showSearch = true }) => {
    return (
        <header className={styles.commandBar}>
            <div className={styles.container}>
                {/* Logo / Title */}
                <div className={styles.logo} onClick={onHome} style={{ cursor: 'pointer' }}>
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

                {/* AI Search Bar (Center) - Only for doctor role */}
                {showSearch && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <button className="glass-btn" style={{ padding: '0.5rem', display: 'flex' }}>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
                            </svg>
                        </button>
                        <AISearchBar onSearch={onSearch} />
                    </div>
                )}

                {/* User Profile / Settings */}
                <div className={styles.userSection}>
                    {/* NLQ Toggle Button */}
                    <button
                        className="glass-btn"
                        onClick={onToggleNLQ}
                        style={{ marginRight: '1rem', padding: '0.5rem 1rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                        title="Open Query Console"
                    >
                        <span>💬</span> Query Console
                    </button>

                    <div className={`${styles.statusIndicator} scan-line`}>
                        <span className={styles.statusDot}></span>
                        <span className={styles.statusText}>System Active</span>
                    </div>

                    {/* Theme Toggle */}
                    <ThemeToggle />

                    {user && (
                        <>
                            <span className={styles.userName}>{user.name}</span>
                            <button className={`glass-btn ${styles.userBtn}`} onClick={onLogout} title="Logout">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <circle cx="10" cy="6" r="3" stroke="currentColor" strokeWidth="1.5" />
                                    <path d="M15 14C15 11.7909 12.7614 10 10 10C7.23858 10 5 11.7909 5 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                                </svg>
                            </button>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
};

export default TopCommandBar;
