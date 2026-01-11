import React, { useState } from 'react';
import styles from './AISearchBar.module.css';

const AISearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const [isFocused, setIsFocused] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <form
            className={`${styles.searchForm} ${isFocused ? styles.focused : ''}`}
            onSubmit={handleSubmit}
        >
            <div className={styles.searchIcon}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="8" cy="8" r="5" stroke="currentColor" strokeWidth="1.5" />
                    <path d="M12 12L17 17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
            </div>

            <input
                type="text"
                className={styles.searchInput}
                placeholder="AI에게 명령을 내려주세요 (예: '최근 2시간 내 Pressor 위험 급상승 환자 필터링')"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
            />

            {query && (
                <button
                    type="button"
                    className={styles.clearBtn}
                    onClick={() => setQuery('')}
                >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                </button>
            )}

            <div className={styles.aiIndicator}>
                <span className={styles.aiIcon}>✨</span>
                <span className={styles.aiText}>AI</span>
            </div>
        </form>
    );
};

export default AISearchBar;
