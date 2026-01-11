import React, { useState } from 'react';
import styles from './ProtocolGuide.module.css';

const ProtocolGuide = ({ patient }) => {
    const [checkedItems, setCheckedItems] = useState({});

    const protocols = [
        {
            id: 1,
            action: '저혈압 감지: 30ml/kg 정질액 투여 검토 필요',
            priority: 'STAT',
            source: '2024 성인 패혈증 초기치료지침서',
            page: 12
        },
        {
            id: 2,
            action: '혈압 유지 실패 시 노르에피네프린 투여 고려',
            priority: 'HIGH',
            source: '2024 성인 패혈증 초기치료지침서',
            page: 15
        },
        {
            id: 3,
            action: '젖산 수치 모니터링 (목표: <2 mmol/L)',
            priority: 'MEDIUM',
            source: 'Surviving Sepsis Campaign',
            page: 8
        }
    ];

    const handleCheck = (id) => {
        setCheckedItems(prev => ({
            ...prev,
            [id]: !prev[id]
        }));
    };

    return (
        <div className={styles.container}>
            <div className={`${styles.header} neon-border-ai`}>
                <span className="neon-text-ai">✨</span>
                <div>
                    <h3>Actionable Checklist</h3>
                    <p className={styles.subtitle}>Based on Clinical Guidelines (RAG)</p>
                </div>
            </div>

            <div className={styles.checklist}>
                {protocols.map((protocol) => (
                    <div key={protocol.id} className={`${styles.item} ${styles[protocol.priority.toLowerCase()]}`}>
                        <label className={styles.checkLabel}>
                            <input
                                type="checkbox"
                                checked={checkedItems[protocol.id] || false}
                                onChange={() => handleCheck(protocol.id)}
                                className={styles.checkbox}
                            />
                            <span className={styles.checkmark}></span>
                        </label>

                        <div className={styles.content}>
                            <div className={styles.itemHeader}>
                                <span className={`${styles.priority} ${styles[protocol.priority.toLowerCase()]}`}>
                                    {protocol.priority}
                                </span>
                                <span className={styles.action}>{protocol.action}</span>
                            </div>

                            <div className={styles.citation}>
                                📚 Source: {protocol.source}, p.{protocol.page}
                            </div>
                        </div>

                        <button className={`glass-btn ${styles.executeBtn}`}>
                            실행
                        </button>
                    </div>
                ))}
            </div>

            <div className={styles.footer}>
                <button className={`glass-btn ${styles.fullBtn}`}>
                    전체 가이드라인 보기
                </button>
            </div>
        </div>
    );
};

export default ProtocolGuide;
