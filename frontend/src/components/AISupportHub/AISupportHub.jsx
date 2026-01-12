import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import styles from './AISupportHub.module.css';

const AISupportHub = ({ patient, onClose, isFullScreen = false }) => {
    const [clinicalSummary, setClinicalSummary] = useState(null);
    const [protocol, setProtocol] = useState(null);
    const [guardianReport, setGuardianReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [vitalsVizType, setVitalsVizType] = useState('area'); // area, line, heatmap
    const [activeTab, setActiveTab] = useState('summary'); // summary, protocol, guardian
    const [selectedProtocol, setSelectedProtocol] = useState(null);
    const [showProtocolModal, setShowProtocolModal] = useState(false);

    // Mock SHAP values - will be replaced with real data
    const shap_features = [
        { feature: 'RR_slope', value: '+0.25', impact: 'high' },
        { feature: 'SpO2_last_value', value: '+0.18', impact: 'high' },
        { feature: 'Lactate_trend', value: '+0.12', impact: 'medium' },
        { feature: 'MAP_mean', value: '-0.08', impact: 'medium' },
        { feature: 'HR_variance', value: '+0.06', impact: 'low' }
    ];

    // Handle view protocol
    const handleViewProtocol = (rec) => {
        setSelectedProtocol(rec);
        setShowProtocolModal(true);
    };

    // Handle view source
    const handleViewSource = (source, page) => {
        // Map source to PDF path
        let pdfPath = '';
        if (source.includes('패혈증') || source.includes('질병관리청')) {
            pdfPath = '/guidelines/2024_질병관리청_성인_패혈증_초기치료지침서.pdf';
        } else if (source.includes('호흡') || source.includes('ARDS')) {
            pdfPath = '/guidelines/2016_대한중환자의학회_ARDS지침서.pdf';
        } else if (source.includes('AKI') || source.includes('신손상')) {
            pdfPath = '/guidelines/급성_신손상의_정의와_평가_임상진료지침.pdf';
        } else {
            pdfPath = '/guidelines/Clinical_Guidelines.pdf';
        }

        const url = page ? `${pdfPath}#page=${page}` : pdfPath;
        window.open(url, '_blank');
    };

    // Close modal
    const closeModal = () => {
        setShowProtocolModal(false);
        setSelectedProtocol(null);
    };

    // Fetch LLM clinical summary from ML service
    useEffect(() => {
        const fetchClinicalSummary = async () => {
            if (!patient?.raw) return;

            try {
                setLoading(true);

                // Prepare patient data for clinical summary API
                const payload = {
                    patient_id: patient.patient_id,
                    vitals: {
                        spo2: patient.raw.spo2_last,
                        rr: patient.raw.rr_last,
                        hr: patient.raw.hr_last,
                        map: patient.raw.map_last
                    },
                    labs: {
                        lactate: patient.raw.lactate_last
                    },
                    prediction_risk: {
                        mortality: patient.mortality_risk,
                        vent: patient.vent_risk,
                        pressor: patient.pressor_risk
                    },
                    risk_level: patient.raw.risk_level || 'MEDIUM',
                    shap_features: shap_features
                };

                const response = await fetch('http://localhost:5003/api/clinical-summary', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`API returned ${response.status}`);
                }

                const data = await response.json();

                setClinicalSummary({
                    patient_id: data.patient_id || patient.patient_id,
                    risk_level: data.risk_level || patient.raw.risk_level || 'MEDIUM',
                    risk_score: data.risk_score || 0,
                    summary: data.summary || 'Clinical summary not available',
                    key_features: data.key_features || [],
                    data_quality_alerts: data.data_quality_alerts || []
                });
            } catch (error) {
                console.error('Failed to fetch clinical summary from ML service:', error);
                // Fallback to basic summary
                setClinicalSummary({
                    patient_id: patient.patient_id,
                    risk_level: patient.raw?.risk_level || 'MEDIUM',
                    risk_score: patient.mortality_risk || 0,
                    summary: `현재 환자 데이터(SpO2 ${patient.raw?.spo2_last}%, RR ${patient.raw?.rr_last}bpm)를 분석 중입니다. AI 모델 예측 결과, 예후 악화 가능성이 있으며 추가적인 모니터링이 권장됩니다. (API 연결 대기 중)`,
                    key_features: [],
                    data_quality_alerts: []
                });
            } finally {
                setLoading(false);
            }
        };

        fetchClinicalSummary();
    }, [patient]);

    // Fetch RAG protocol and convert to condition-based recommendations
    useEffect(() => {
        const fetchProtocol = async () => {
            if (!patient?.raw) return;

            try {
                setLoading(true);
                setProtocol(null); // Reset previous protocol data while loading

                // Generate condition-based queries from patient vitals
                const conditions = [];
                const queries = [];

                // Check SpO2
                if (patient.raw.spo2_last < 90) {
                    conditions.push({
                        condition: `SpO2 ${patient.raw.spo2_last}% (< 90%)`,
                        severity: 'STAT',
                        query: patient.raw.spo2_last < 85 ? '기관 삽관 인공호흡기' : '산소 공급 증가'
                    });
                }

                // Check MAP
                if (patient.raw.map_last < 65) {
                    conditions.push({
                        condition: `MAP ${patient.raw.map_last} mmHg (< 65)`,
                        severity: 'STAT',
                        query: '승압제 투여 노르에피네프린'
                    });
                }

                // Check Lactate
                if (patient.raw.lactate_last > 4.0) {
                    conditions.push({
                        condition: `Lactate ${patient.raw.lactate_last} mmol/L (> 4.0)`,
                        severity: 'STAT',
                        query: '패혈증 수액 소생 crystalloid'
                    });
                } else if (patient.raw.lactate_last > 2.0) {
                    conditions.push({
                        condition: `Lactate ${patient.raw.lactate_last} mmol/L (> 2.0)`,
                        severity: 'HIGH',
                        query: '패혈증 모니터링'
                    });
                }

                // Check RR
                if (patient.raw.rr_last > 30) {
                    conditions.push({
                        condition: `RR ${patient.raw.rr_last} bpm (> 30)`,
                        severity: 'HIGH',
                        query: '호흡곤란 산소 치료'
                    });
                }

                // Fetch recommendations from RAG for each condition
                // Build vitals object for context-aware RAG
                const vitals = {
                    map: patient.raw.map_last,
                    lactate: patient.raw.lactate_last,
                    spo2: patient.raw.spo2_last,
                    rr: patient.raw.rr_last
                };

                const recommendations = await Promise.all(
                    conditions.map(async (cond) => {
                        try {
                            const response = await fetch('http://localhost:5003/protocol', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    query: cond.query,
                                    vitals: vitals  // Pass vitals for context-aware filtering
                                })
                            });

                            if (!response.ok) throw new Error('API failed');

                            const data = await response.json();

                            // Extract first action from protocol
                            const action = data.protocol?.steps?.[0]?.actions?.[0] ||
                                '가이드라인 참조 필요';

                            const source = data.evidence?.[0]?.doc_title || 'Clinical Guidelines';
                            const page = data.evidence?.[0]?.page || null;

                            return {
                                condition: cond.condition,
                                action: action,
                                source: source,
                                page: page,
                                severity: cond.severity,
                                fullProtocol: data.protocol,  // Store full protocol
                                evidence: data.evidence || []  // Store evidence list
                            };
                        } catch (error) {
                            console.error(`Failed to fetch for ${cond.condition}:`, error);
                            return {
                                condition: cond.condition,
                                action: '프로토콜 로딩 실패',
                                source: 'N/A',
                                page: null,
                                severity: cond.severity,
                                fullProtocol: null,
                                evidence: []
                            };
                        }
                    })
                );

                setProtocol({
                    title: 'Patient-Specific Recommendations',
                    recommendations: recommendations
                });

            } catch (error) {
                console.error('Failed to generate recommendations:', error);
                setProtocol({
                    title: 'Error',
                    recommendations: []
                });
            } finally {
                setLoading(false);
            }
        };

        fetchProtocol();
    }, [patient]);

    // Generate Guardian Report (triggered by approval button)
    const generateGuardianReport = async (approvedBy) => {
        if (!patient?.raw || !clinicalSummary) {
            alert('임상 요약이 먼저 로드되어야 합니다. AI Summary 탭을 먼저 확인해주세요.');
            return;
        }

        try {
            setLoading(true);

            // API requires clinical_summary object with specific structure
            const payload = {
                patient_id: patient.patient_id,
                clinical_summary: {
                    patient_id: patient.patient_id,
                    risk_level: clinicalSummary.risk_level || 'MEDIUM',
                    risk_score: clinicalSummary.risk_score || 0,
                    summary: clinicalSummary.summary || 'Clinical summary unavailable',
                    key_features: clinicalSummary.key_features || [],
                    data_quality_alerts: clinicalSummary.data_quality_alerts || []
                },
                approved_by: approvedBy  // Doctor who approved this report
            };

            const response = await fetch('http://localhost:5003/api/gentle-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('API error:', errorData);
                throw new Error(errorData.error || `API returned ${response.status}`);
            }

            const data = await response.json();
            setGuardianReport(data);
            alert('보호자 리포트가 성공적으로 생성되었습니다!');
        } catch (error) {
            console.error('Failed to generate guardian report:', error);
            alert(`리포트 생성 실패: ${error.message}`);
            setGuardianReport({
                patient_id: patient.patient_id,
                status: '오류',
                simple_explanation: '환자의 상태 리포트를 생성하는 중 오류가 발생했습니다.',
                what_to_expect: '담당 의료진께 직접 문의해주세요.',
                family_guidance: '간호사실 또는 주치의와 상담을 요청하시기 바랍니다.',
                approved: false,
                error: error.message
            });
        } finally {
            setLoading(false);
        }
    };

    if (!patient) return null;

    // Prepare chart data for risk timeline
    const riskChartData = patient.raw?.risk_timeline_24h?.map(point => ({
        time: point.t,
        Mortality: (point.mortality * 100).toFixed(0),
        Vent_start: (point.vent * 100).toFixed(0),
        Pressor_start: (point.pressor * 100).toFixed(0)
    })) || [];

    // Prepare chart data for vitals
    const vitalsData = patient.raw?.vitals_trends ?
        patient.raw.vitals_trends.spo2.map((_, idx) => ({
            time: patient.raw.vitals_trends.spo2[idx].t,
            SpO2: patient.raw.vitals_trends.spo2[idx].v,
            RR: patient.raw.vitals_trends.rr[idx].v,
            MAP: patient.raw.vitals_trends.map[idx].v,
            Lactate: patient.raw.vitals_trends.lactate[idx].v
        })) : [];

    return (
        <>
            {/* Overlay - only show in modal mode */}
            {!isFullScreen && <div className={styles.overlay} onClick={onClose}></div>}

            {/* Sliding Panel or Full Screen Container */}
            <aside className={isFullScreen ? styles.fullScreenContainer : styles.panel}>
                {/* Header */}
                <div className={styles.header}>
                    <div className={styles.headerContent}>
                        <div>
                            <h2 className={styles.patientTitle}>
                                Patient {patient.patient_id} / {patient.raw?.bed_id || patient.location}
                            </h2>
                            <p className={styles.subtitle}>ICU Unit: {patient.raw?.icu_unit || 'N/A'}</p>
                        </div>
                        <button
                            className={isFullScreen ? styles.backButton : `glass-btn ${styles.closeBtn}`}
                            onClick={onClose}
                        >
                            {isFullScreen ? (
                                <>
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ marginRight: '0.5rem' }}>
                                        <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Back to Dashboard
                                </>
                            ) : (
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className={styles.content}>
                    {/* Tab Navigation */}
                    <div className={styles.tabsContainer}>
                        <button
                            className={`${styles.tabBtn} glass-btn ${activeTab === 'summary' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('summary')}
                        >
                            <span>✨</span>
                            AI Summary & SHAP Insights
                        </button>
                        <button
                            className={`${styles.tabBtn} glass-btn ${activeTab === 'protocol' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('protocol')}
                        >
                            <span>📋</span>
                            Protocol Guide
                        </button>
                        <button
                            className={`${styles.tabBtn} glass-btn ${activeTab === 'guardian' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('guardian')}
                        >
                            <span>👨‍👩‍👧</span>
                            Guardian Report
                        </button>
                    </div>

                    {/* Ethical Disclaimer Notice */}
                    <div className={styles.disclaimer}>
                        ⚠️ 본 예측 결과는 임상 의사결정을 보조하기 위한 참고 정보이며, 단독으로 치료 결정에 사용되어서는 안 됩니다.
                    </div>

                    {/* Tab 1: AI Summary & SHAP Insights */}
                    {activeTab === 'summary' && (
                        <>
                            <section className={styles.section}>
                                <h3 className={styles.sectionTitle}>24시간 위험 수준 추이 (참고용)</h3>
                                <div className={styles.chartContainer}>
                                    <ResponsiveContainer width="100%" height={200}>
                                        <LineChart data={riskChartData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                            <XAxis dataKey="time" stroke="#888" />
                                            <YAxis stroke="#888" label={{ value: '%', angle: -90, position: 'insideLeft' }} />
                                            <Tooltip
                                                contentStyle={{ background: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }}
                                            />
                                            <Legend />
                                            <Line type="monotone" dataKey="Mortality" name="예후" stroke="#ff6b6b" strokeWidth={2} />
                                            <Line type="monotone" dataKey="Vent_start" name="인공호흡기" stroke="#4ecdc4" strokeWidth={2} />
                                            <Line type="monotone" dataKey="Pressor_start" name="승압제" stroke="#ffd93d" strokeWidth={2} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </section>

                            {/* Section 2: Vitals Trend */}
                            <section className={styles.section}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                    <h3 className={styles.sectionTitle} style={{ margin: 0, paddingBottom: 0, border: 'none' }}>Vitals Trend (24h)</h3>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        <button
                                            className={`glass- btn ${vitalsVizType === 'area' ? styles.activeVizBtn : ''}`}
                                            onClick={() => setVitalsVizType('area')}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                fontSize: '0.875rem',
                                                background: vitalsVizType === 'area' ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                                                border: `1px solid ${vitalsVizType === 'area' ? '#06b6d4' : 'rgba(255,255,255,0.2)'}`
                                            }}
                                        >
                                            Area
                                        </button>
                                        <button
                                            className={`glass-btn ${vitalsVizType === 'line' ? styles.activeVizBtn : ''}`}
                                            onClick={() => setVitalsVizType('line')}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                fontSize: '0.875rem',
                                                background: vitalsVizType === 'line' ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                                                border: `1px solid ${vitalsVizType === 'line' ? '#06b6d4' : 'rgba(255,255,255,0.2)'}`
                                            }}
                                        >
                                            Line
                                        </button>
                                        <button
                                            className={`glass-btn ${vitalsVizType === 'heatmap' ? styles.activeVizBtn : ''}`}
                                            onClick={() => setVitalsVizType('heatmap')}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                fontSize: '0.875rem',
                                                background: vitalsVizType === 'heatmap' ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                                                border: `1px solid ${vitalsVizType === 'heatmap' ? '#06b6d4' : 'rgba(255,255,255,0.2)'}`
                                            }}
                                        >
                                            Heatmap
                                        </button>
                                    </div>
                                </div>

                                {vitalsVizType === 'area' && (
                                    <div className={styles.vitalsGrid}>
                                        <div className={styles.vitalChart}>
                                            <h4>SpO2 Trend</h4>
                                            <p className={styles.vitalValue}>
                                                {patient.raw?.spo2_last}%
                                                {patient.raw?.vitals_trends && patient.raw.vitals_trends.spo2[0].v > patient.raw.spo2_last &&
                                                    <span className={styles.decreasing}> (Decreasing)</span>
                                                }
                                            </p>
                                            <ResponsiveContainer width="100%" height={80}>
                                                <AreaChart data={vitalsData.map(d => ({ value: d.SpO2 }))}>
                                                    <defs>
                                                        <linearGradient id="spo2Gradient" x1="0" y1="0" x2="0" y2="1">
                                                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                                                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                                        </linearGradient>
                                                    </defs>
                                                    <Area type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} fill="url(#spo2Gradient)" />
                                                </AreaChart>
                                            </ResponsiveContainer>
                                        </div>
                                        <div className={styles.vitalChart}>
                                            <h4>RR (Resp. Rate) Trend</h4>
                                            <p className={styles.vitalValue}>
                                                {patient.raw?.rr_last} bpm
                                                {patient.raw?.vitals_trends && patient.raw.vitals_trends.rr[0].v < patient.raw.rr_last &&
                                                    <span className={styles.increasing}> (Increasing)</span>
                                                }
                                            </p>
                                            <ResponsiveContainer width="100%" height={80}>
                                                <AreaChart data={vitalsData.map(d => ({ value: d.RR }))}>
                                                    <defs>
                                                        <linearGradient id="rrGradient" x1="0" y1="0" x2="0" y2="1">
                                                            <stop offset="5%" stopColor="#eab308" stopOpacity={0.8} />
                                                            <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                                                        </linearGradient>
                                                    </defs>
                                                    <Area type="monotone" dataKey="value" stroke="#eab308" strokeWidth={2} fill="url(#rrGradient)" />
                                                </AreaChart>
                                            </ResponsiveContainer>
                                        </div>
                                    </div>
                                )}

                                {vitalsVizType === 'line' && (
                                    <div className={styles.chartContainer}>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <LineChart data={vitalsData}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                                <XAxis dataKey="time" stroke="rgba(255,255,255,0.5)" style={{ fontSize: '12px' }} />
                                                <YAxis stroke="rgba(255,255,255,0.5)" style={{ fontSize: '12px' }} />
                                                <Tooltip
                                                    contentStyle={{
                                                        backgroundColor: 'rgba(0,0,0,0.9)',
                                                        border: '1px solid rgba(255,255,255,0.2)',
                                                        borderRadius: '8px',
                                                    }}
                                                    labelStyle={{ color: '#fff' }}
                                                />
                                                <Legend wrapperStyle={{ fontSize: '14px' }} />
                                                <Line type="monotone" dataKey="SpO2" stroke="#ef4444" strokeWidth={2} name="SpO2 (%)" />
                                                <Line type="monotone" dataKey="RR" stroke="#eab308" strokeWidth={2} name="RR (bpm)" />
                                                <Line type="monotone" dataKey="MAP" stroke="#a855f7" strokeWidth={2} name="MAP (mmHg)" />
                                                <Line type="monotone" dataKey="Lactate" stroke="#06b6d4" strokeWidth={2} name="Lactate (mmol/L)" />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                )}

                                {vitalsVizType === 'heatmap' && patient.raw?.vitals_trends && (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                        {['spo2', 'rr', 'map', 'lactate'].map((vitalKey) => {
                                            const vitalName = vitalKey === 'spo2' ? 'SpO2' : vitalKey === 'rr' ? 'RR' : vitalKey.toUpperCase();
                                            const vitalData = patient.raw.vitals_trends[vitalKey] || [];

                                            const getHeatColor = (vital, value) => {
                                                if (vital === 'SpO2') {
                                                    if (value >= 95) return '#10b981';
                                                    if (value >= 90) return '#eab308';
                                                    return '#ef4444';
                                                }
                                                if (vital === 'RR') {
                                                    if (value <= 20) return '#10b981';
                                                    if (value <= 25) return '#eab308';
                                                    return '#ef4444';
                                                }
                                                if (vital === 'MAP') {
                                                    if (value >= 80) return '#10b981';
                                                    if (value >= 70) return '#eab308';
                                                    return '#ef4444';
                                                }
                                                if (vital === 'Lactate') {
                                                    if (value < 2) return '#10b981';
                                                    if (value < 4) return '#eab308';
                                                    return '#ef4444';
                                                }
                                                return '#6b7280';
                                            };

                                            return (
                                                <div key={vitalKey} className={styles.vitalChart}>
                                                    <h4 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', fontWeight: 600 }}>{vitalName}</h4>
                                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '0.5rem' }}>
                                                        {vitalData.map((point, idx) => (
                                                            <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
                                                                <div
                                                                    style={{
                                                                        width: '100%',
                                                                        height: '60px',
                                                                        borderRadius: '0.5rem',
                                                                        backgroundColor: getHeatColor(vitalName, point.v),
                                                                        display: 'flex',
                                                                        alignItems: 'center',
                                                                        justifyContent: 'center',
                                                                        fontWeight: 700,
                                                                        color: 'white',
                                                                        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                                                                        transition: 'transform 0.2s',
                                                                        cursor: 'pointer'
                                                                    }}
                                                                    onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                                                    onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                                                >
                                                                    {point.v}
                                                                </div>
                                                                <span style={{ fontSize: '0.7rem', color: 'rgba(156, 163, 175, 1)' }}>{point.t}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                        <p style={{ textAlign: 'center', fontSize: '0.875rem', color: 'rgba(156, 163, 175, 1)', margin: '0.5rem 0 0 0' }}>
                                            🟢 Green = Normal | 🟡 Yellow = Warning | 🔴 Red = Critical
                                        </p>
                                    </div>
                                )}
                            </section>

                            {/* Section 3: LLM Clinical Summary */}
                            <section className={styles.section}>
                                <h3 className={styles.sectionTitle}>
                                    <span className="neon-text-ai">✨</span> LLM 기반 임상 요약 (AI-Generated Clinical Summary)
                                </h3>
                                <div className={`${styles.summaryBox} glass-card`}>
                                    {clinicalSummary ? (
                                        <p className={styles.summaryText}>{clinicalSummary.summary}</p>
                                    ) : (
                                        <p className={styles.loading}>Loading clinical summary...</p>
                                    )}
                                </div>
                            </section>

                            {/* Section 4: Key Risk Factors (SHAP) */}
                            <section className={styles.section}>
                                <h3 className={styles.sectionTitle}>Key Risk Factors (SHAP)</h3>
                                <div className={styles.shapContainer}>
                                    {shap_features.map((feature, idx) => (
                                        <div key={idx} className={styles.shapFeature}>
                                            <div className={styles.shapLabel}>{feature.feature}</div>
                                            <div className={styles.shapBar}>
                                                <div
                                                    className={`${styles.shapFill} ${styles[feature.impact]}`}
                                                    style={{ width: `${Math.abs(parseFloat(feature.value)) * 300}px` }}
                                                >
                                                    <span className={styles.shapValue}>{feature.value}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        </>
                    )}

                    {/* Tab 2: Protocol Guide */}
                    {activeTab === 'protocol' && (
                        <section className={styles.section}>
                            <div>
                                <h3 className={styles.sectionTitle}>📋 Patient-Specific Actions</h3>
                                <p className={styles.sectionSubtitle}>Based on Current Vitals & Clinical Guidelines (RAG)</p>
                            </div>
                            {protocol && protocol.recommendations && protocol.recommendations.length > 0 ? (
                                <div className={styles.checklistContainer}>
                                    {protocol.recommendations.map((rec, idx) => {
                                        const priorityClass = rec.severity?.toLowerCase() || 'medium';
                                        return (
                                            <div key={idx} className={`${styles.checklistItem} ${styles[priorityClass]}`}>
                                                <div className={styles.checklistHeader}>
                                                    <input type="checkbox" className={styles.checkbox} />
                                                    <span className={`${styles.priorityBadge} ${styles[priorityClass]}`}>
                                                        {rec.severity || 'MEDIUM'}
                                                    </span>
                                                    <div className={styles.checklistContent}>
                                                        <p className={styles.conditionLabel}>{rec.condition}</p>
                                                        <p className={styles.actionText}>→ {rec.action}</p>
                                                        <p className={styles.source}>📚 {rec.source}</p>

                                                        {/* Action Buttons */}
                                                        <div className={styles.actionButtons}>
                                                            {rec.fullProtocol && (
                                                                <button
                                                                    className={`glass-btn ${styles.protocolViewBtn}`}
                                                                    onClick={() => handleViewProtocol(rec)}
                                                                >
                                                                    📋 프로토콜 보기
                                                                </button>
                                                            )}
                                                            <button
                                                                className={`glass-btn ${styles.sourceViewBtn}`}
                                                                onClick={() => handleViewSource(rec.source, rec.page)}
                                                            >
                                                                📄 원문 보기
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <button className={styles.actionButton}>실행</button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : !protocol || loading ? (
                                <div className={`${styles.protocolBox} glass-card`}>
                                    <p className={styles.loading}>환자 바이탈 분석 중 및 임상 가이드라인 검색 중...</p>
                                </div>
                            ) : protocol.recommendations && protocol.recommendations.length === 0 ? (
                                <div className={`${styles.protocolBox} glass-card`}>
                                    <p className={styles.summaryText}>✅ 현재 주요 이상 소견 없음. 표준 모니터링 지속.</p>
                                </div>
                            ) : null}
                        </section>
                    )}

                    {/* Tab 3: Guardian Report */}
                    {activeTab === 'guardian' && (
                        <section className={styles.section}>
                            <div>
                                <h3 className={styles.sectionTitle}>👨‍👩‍👧 Guardian Report</h3>
                                <p className={styles.sectionSubtitle}>보호자를 위한 의료진 승인 필요</p>
                            </div>

                            {!guardianReport ? (
                                <div className={`${styles.contentBox} glass-card ${styles.guardianPlaceholder}`}>
                                    <div style={{ marginBottom: '1.5rem' }}>
                                        <span className={styles.guardianPlaceholderIcon}>👨‍⚕️</span>
                                        <h4 className={styles.guardianPlaceholderTitle}>의료진 승인 필요</h4>
                                        <p className={styles.guardianText}>
                                            보호자용 리포트는 의료진의 승인 후 생성됩니다.<br />
                                            승인시 AI 보조 기능에 제공 가능한 안내문이 생성됩니다.
                                        </p>
                                    </div>
                                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                                        <button
                                            className={styles.actionButton}
                                            style={{ background: loading ? 'linear-gradient(135deg, #6b7280, #4b5563)' : 'linear-gradient(135deg, #22c55e, #16a34a)' }}
                                            onClick={() => {
                                                const doctorName = prompt('승인 의료진 이름을 입력하세요:', 'Dr. ' + (patient.patient_id || 'Unknown'));
                                                if (doctorName) {
                                                    generateGuardianReport(doctorName);
                                                }
                                            }}
                                            disabled={loading}
                                        >
                                            {loading ? '⏳ 생성 중...' : '✅ 승인 및 생성'}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className={`${styles.contentBox} glass-card`} style={{ padding: '1.5rem' }}>
                                    {guardianReport.approved ? (
                                        <>
                                            <div className={styles.guardianApproved}>
                                                <span>✅ 승인됨: {guardianReport.approved_by}</span>
                                            </div>
                                            <div className={`${styles.guardianSection} ${styles.guardianStatus}`}>
                                                <h4 className={styles.guardianTitle}>환자 상태</h4>
                                                <p className={styles.guardianText}>{guardianReport.simple_explanation}</p>
                                            </div>
                                            <div className={`${styles.guardianSection} ${styles.guardianExpected}`}>
                                                <h4 className={styles.guardianTitle}>예상되는 상황</h4>
                                                <p className={styles.guardianText}>{guardianReport.what_to_expect}</p>
                                            </div>
                                            <div className={`${styles.guardianSection} ${styles.guardianGuidance}`}>
                                                <h4 className={styles.guardianTitle}>보호자 안내</h4>
                                                <p className={styles.guardianText}>{guardianReport.family_guidance}</p>
                                            </div>
                                            <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                                                <button
                                                    className={styles.actionButton}
                                                    style={{ background: 'linear-gradient(135deg, #6b7280, #4b5563)' }}
                                                    onClick={() => {
                                                        if (confirm('리포트를 다시 생성하시겠습니까?')) {
                                                            setGuardianReport(null);
                                                        }
                                                    }}
                                                >
                                                    🔄 재생성
                                                </button>
                                                <button className={styles.actionButton} style={{ background: 'linear-gradient(135deg, #3b82f6, #2563eb)' }}>
                                                    📄 이메일 전송
                                                </button>
                                            </div>
                                        </>
                                    ) : (
                                        <div style={{ padding: '2rem', textAlign: 'center' }}>
                                            <p style={{ color: '#ef4444', marginBottom: '1rem' }}>⚠️ {guardianReport.error || '리포트 생성 실패'}</p>
                                            <p style={{ color: 'rgba(156, 163, 175, 1)' }}>{guardianReport.simple_explanation}</p>
                                            <button
                                                className={styles.actionButton}
                                                style={{ marginTop: '1rem', background: 'linear-gradient(135deg, #22c55e, #16a34a)' }}
                                                onClick={() => setGuardianReport(null)}
                                            >
                                                다시 시도
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </section>
                    )}
                </div>
            </aside>

            {/* Protocol Modal */}
            {showProtocolModal && selectedProtocol && selectedProtocol.fullProtocol && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
                        <div className={styles.modalHeader}>
                            <h2>{selectedProtocol.fullProtocol.title || '프로토콜 상세'}</h2>
                            <button className={styles.closeBtn} onClick={closeModal}>✕</button>
                        </div>

                        <div className={styles.modalBody}>
                            {selectedProtocol.fullProtocol.steps && selectedProtocol.fullProtocol.steps.length > 0 ? (
                                <div className={styles.protocolSteps}>
                                    {selectedProtocol.fullProtocol.steps.map((step, idx) => (
                                        <div key={idx} className={styles.protocolStep}>
                                            <div className={styles.stepHeader}>
                                                <span className={styles.stepNumber}>{step.order || idx + 1}</span>
                                                <h3>{step.title || `Step ${idx + 1}`}</h3>
                                            </div>
                                            {step.actions && step.actions.length > 0 && (
                                                <ul className={styles.stepActions}>
                                                    {step.actions.map((action, actionIdx) => (
                                                        <li key={actionIdx}>{action}</li>
                                                    ))}
                                                </ul>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
                                    프로토콜 상세 정보를 로드할 수 없습니다.
                                </p>
                            )}

                            {selectedProtocol.fullProtocol.disclaimer && (
                                <div className={styles.protocolFooter}>
                                    <p className={styles.disclaimer}>
                                        ⚠️ {selectedProtocol.fullProtocol.disclaimer}
                                    </p>
                                </div>
                            )}

                            {selectedProtocol.source && (
                                <div className={styles.protocolFooter}>
                                    <p className={styles.modalSource}>
                                        출처: {selectedProtocol.source}
                                        {selectedProtocol.page && ` (p.${selectedProtocol.page})`}
                                    </p>
                                </div>
                            )}
                        </div>

                        <div className={styles.modalActions}>
                            <button
                                className={`glass-btn ${styles.sourceViewBtn}`}
                                onClick={() => handleViewSource(selectedProtocol.source, selectedProtocol.page)}
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
        </>
    );
};

export default AISupportHub;
