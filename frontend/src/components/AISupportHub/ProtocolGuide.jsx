import React, { useState } from 'react';
import styles from './ProtocolGuide.module.css';

const ProtocolGuide = ({ patient }) => {
    const [checkedItems, setCheckedItems] = useState({});
    const [selectedProtocol, setSelectedProtocol] = useState(null);
    const [showProtocolModal, setShowProtocolModal] = useState(false);

    const protocols = [
        {
            id: 1,
            action: '저혈압 감지: 30ml/kg 정질액 투여 검토 필요',
            priority: 'STAT',
            source: '2024 성인 패혈증 초기치료지침서',
            page: 12,
            fullProtocol: {
                title: '패혈증 초기 수액 소생술',
                steps: [
                    { order: 1, title: '즉시(0-15분)', actions: ['MAP <65 mmHg 또는 lactate ≥4 mmol/L 확인', 'Blood culture 채취 (항생제 투여 전)', 'Lactate 측정'] },
                    { order: 2, title: '수액 소생', actions: ['30 ml/kg crystalloid 3시간 이내 투여', '수액 반응성 재평가'] },
                    { order: 3, title: '승압제', actions: ['MAP 65 mmHg 유지', 'Norepinephrine 우선 투여'] }
                ]
            },
            pdfPath: '/guidelines/2024_패혈증_초기치료지침서.pdf'
        },
        {
            id: 2,
            action: '혈압 유지 실패 시 노르에피네프린 투여 고려',
            priority: 'HIGH',
            source: '2024 성인 패혈증 초기치료지침서',
            page: 15,
            fullProtocol: {
                title: '패혈쇼크 승압제 투여',
                steps: [
                    { order: 1, title: '승압제 시작', actions: ['초기 수액 치료 도중 혈역학적 안정을 위해 승압제 조기 투여', 'Norepinephrine을 우선적으로 사용'] },
                    { order: 2, title: '목표 설정', actions: ['MAP ≥65 mmHg 목표', '만성 고혈압 환자는 더 높은 목표(75-85 mmHg) 고려'] },
                    { order: 3, title: '모니터링', actions: ['지속적 혈압 모니터링', 'Lactate 추적 관찰'] }
                ]
            },
            pdfPath: '/guidelines/2024_패혈증_초기치료지침서.pdf'
        },
        {
            id: 3,
            action: '젖산 수치 모니터링 (목표: <2 mmol/L)',
            priority: 'MEDIUM',
            source: 'Surviving Sepsis Campaign',
            page: 8,
            fullProtocol: {
                title: '젖산 모니터링 프로토콜',
                steps: [
                    { order: 1, title: '초기 측정', actions: ['패혈증/패혈쇼크 의심 시 즉시 lactate 측정', '≥4 mmol/L인 경우 저관류로 판단'] },
                    { order: 2, title: '추적 관찰', actions: ['초기 lactate 상승 시 2-4시간마다 재측정', 'Lactate clearance 지표로 사용'] },
                    { order: 3, title: '목표', actions: ['정상화(<2 mmol/L) 또는 지속적 감소 확인', '반응 없으면 치료 조정'] }
                ]
            },
            pdfPath: '/guidelines/Surviving_Sepsis_Campaign.pdf'
        }
    ];

    const handleCheck = (id) => {
        setCheckedItems(prev => ({
            ...prev,
            [id]: !prev[id]
        }));
    };

    const handleViewProtocol = (protocol) => {
        setSelectedProtocol(protocol);
        setShowProtocolModal(true);
    };

    const handleViewSource = (pdfPath, page) => {
        // Open PDF in new window/tab with page number
        const url = `${pdfPath}#page=${page}`;
        window.open(url, '_blank');
    };

    const closeModal = () => {
        setShowProtocolModal(false);
        setSelectedProtocol(null);
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

                            <div className={styles.actionButtons}>
                                <button
                                    className={`glass-btn ${styles.protocolBtn}`}
                                    onClick={() => handleViewProtocol(protocol)}
                                >
                                    📋 프로토콜 보기
                                </button>
                                <button
                                    className={`glass-btn ${styles.sourceBtn}`}
                                    onClick={() => handleViewSource(protocol.pdfPath, protocol.page)}
                                >
                                    📄 원문 보기
                                </button>
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

            {/* Protocol Modal */}
            {showProtocolModal && selectedProtocol && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
                        <div className={styles.modalHeader}>
                            <h2>{selectedProtocol.fullProtocol.title}</h2>
                            <button className={styles.closeBtn} onClick={closeModal}>✕</button>
                        </div>

                        <div className={styles.modalBody}>
                            <div className={styles.protocolSteps}>
                                {selectedProtocol.fullProtocol.steps.map((step) => (
                                    <div key={step.order} className={styles.protocolStep}>
                                        <div className={styles.stepHeader}>
                                            <span className={styles.stepNumber}>{step.order}</span>
                                            <h3>{step.title}</h3>
                                        </div>
                                        <ul className={styles.stepActions}>
                                            {step.actions.map((action, idx) => (
                                                <li key={idx}>{action}</li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>

                            <div className={styles.protocolFooter}>
                                <p className={styles.disclaimer}>
                                    ⚠️ 환자 상태에 따라 조정 필요
                                </p>
                                <p className={styles.source}>
                                    출처: {selectedProtocol.source}, p.{selectedProtocol.page}
                                </p>
                            </div>
                        </div>

                        <div className={styles.modalActions}>
                            <button
                                className={`glass-btn ${styles.sourceBtn}`}
                                onClick={() => handleViewSource(selectedProtocol.pdfPath, selectedProtocol.page)}
                            >
                                📄 원문 보기
                            </button>
                            <button className="glass-btn" onClick={closeModal}>
                                닫기
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProtocolGuide;
