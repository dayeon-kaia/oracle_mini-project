import React, { useState } from 'react';
import styles from './GuardianReport.module.css';

const GuardianReport = ({ patient }) => {
    const [approved, setApproved] = useState(false);

    const generateReport = () => {
        // This would call the /api/gentle-report endpoint
        setApproved(true);
    };

    return (
        <div className={styles.container}>
            <div className={styles.notice}>
                <span className={styles.noticeIcon}>👨‍⚕️</span>
                <div>
                    <h4 className={styles.noticeTitle}>의료진 승인 필요</h4>
                    <p className={styles.noticeText}>
                        보호자용 리포트는 의료진 검토 및 승인 후 출력 가능합니다.
                    </p>
                </div>
            </div>

            {!approved ? (
                <div className={styles.approval}>
                    <button
                        className={`glass-btn ${styles.approveBtn}`}
                        onClick={generateReport}
                    >
                        승인 및 생성
                    </button>
                    <p className={styles.approvalNote}>
                        승인 시 보호자에게 제공 가능한 안전한 언어로 변환됩니다.
                    </p>
                </div>
            ) : (
                <div className={styles.report}>
                    <div className={styles.reportHeader}>
                        <h3>환자 상태 리포트</h3>
                        <span className={styles.approvedBadge}>✓ 승인됨</span>
                    </div>

                    <div className={styles.section}>
                        <h4 className={styles.sectionTitle}>현재 상태</h4>
                        <p className={styles.text}>
                            현재 환자분은 집중 치료가 필요한 상태입니다.
                            혈압이 다소 낮아져 의료진이 면밀히 모니터링하고 있습니다.
                        </p>
                    </div>

                    <div className={styles.section}>
                        <h4 className={styles.sectionTitle}>예상되는 상황</h4>
                        <p className={styles.text}>
                            혈압을 안정시키기 위해 약물 치료를 시작할 수 있습니다.
                            의료진이 환자의 상태를 지속적으로 확인하고 있으니 안심하셔도 됩니다.
                        </p>
                    </div>

                    <div className={styles.section}>
                        <h4 className={styles.sectionTitle}>보호자 안내</h4>
                        <p className={styles.text}>
                            • 환자 곁을 지켜주시면 도움이 됩니다<br />
                            • 궁금한 사항은 언제든 담당 의료진에게 문의해주세요<br />
                            • 갑작스러운 변화 시 즉시 간호사를 호출해주세요
                        </p>
                    </div>

                    <div className={styles.actions}>
                        <button className="glass-btn">
                            📄 PDF 다운로드
                        </button>
                        <button className="glass-btn">
                            📧 이메일 전송
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GuardianReport;
