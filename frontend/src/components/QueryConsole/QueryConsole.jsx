import { useEffect, useMemo, useState } from "react";
import styles from "./QueryConsole.module.css";

const COLUMNS = ["stay_id", "charttime", "hr", "map", "lactate", "spo2", "temp", "risk_score"];

const EXAMPLE_QUERIES = [
  "HR이 100 이상인 환자는 몇명이야?",
  "HR이 100 이상인 환자의 모든 정보 보여줘",
  "Lactate 수치가 4.0 이상인 환자 찾아줘",
  "MICU에 있는 환자 명단 보여줘",
  "최근 24시간 동안 열이 38도 이상인 기록 보여줘",
  "위험도(risk_score)가 0.8 이상인 고위험 환자 리스트",
  "Sepsis 의심 환자(Lactate > 4, MAP < 65) 조회해줘"
];

const STATUS_LABELS = {
  success: "success",
  warn: "warning",
  error: "error",
  info: "info",
};

const STATUS_CLASS = {
  success: styles.statusSuccess,
  warn: styles.statusWarn,
  error: styles.statusError,
  info: styles.statusInfo,
};

const createErrorResponse = (question) => ({
  request_id: `err_${Date.now()}`,
  question,
  sql: "",
  columns: [],
  rows: [],
  row_count: 0,
  warnings: [],
  error: "Network error. Please try again.",
  logs: [],
});

const formatHistoryTime = (timestamp) =>
  new Date(timestamp).toLocaleString("ko-KR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

function DataTable({ columns, rows }) {
  if (!columns.length) {
    return <div className={styles.emptyState}>No rows returned.</div>;
  }

  return (
    <div className={`${styles.tableWrap} glass-panel`}>
      <table className={`glass-table ${styles.table}`}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((col) => (
                <td key={`${rowIndex}-${col}`}>{row[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function QueryConsole({ initialQuery, onClose }) {
  const [question, setQuestion] = useState(initialQuery || "");
  const [response, setResponse] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [environment, setEnvironment] = useState("dev");
  const [limit, setLimit] = useState(50);
  const [activeTab, setActiveTab] = useState("result");
  const [copiedSql, setCopiedSql] = useState(false);
  const [showExampleModal, setShowExampleModal] = useState(false);

  const handleRun = async (overrideQuestion = null) => {
    const queryTerm = typeof overrideQuestion === 'string' ? overrideQuestion : question;
    // Allow empty check to be bypassed if override provided, otherwise check state
    if (!queryTerm.trim() || (isLoading && !overrideQuestion)) return;

    setIsLoading(true);
    setResponse(null);
    setActiveTab("result");

    try {
      const res = await fetch("http://localhost:3000/api/nlq", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: queryTerm,
          limit,
        }),
      });

      let data;
      try {
        data = await res.json();
      } catch (parseError) {
        console.error("[QueryConsole] Failed to parse response:", parseError);
        data = createErrorResponse(queryTerm);
      }

      setResponse(data);
      setHistory((prev) => [
        {
          id: data.request_id || `req_${Date.now()}`,
          question: queryTerm,
          timestamp: new Date().toISOString(),
          status: data.error ? "error" : "success",
          response: data,
        },
        ...prev.slice(0, 9),
      ]);
    } catch (error) {
      console.error("[QueryConsole] Query execution error:", error);
      const fallback = createErrorResponse(queryTerm);
      setResponse(fallback);
      setHistory((prev) => [
        {
          id: fallback.request_id,
          question: queryTerm,
          timestamp: new Date().toISOString(),
          status: "error",
          response: fallback,
        },
        ...prev.slice(0, 9),
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      setQuestion(initialQuery);
      handleRun(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuery]);

  const handleClear = () => {
    setQuestion("");
    setResponse(null);
  };

  const handleUseExample = () => {
    setShowExampleModal(true);
  };

  const handleSelectExample = (ex) => {
    setQuestion(ex);
    setShowExampleModal(false);
    handleRun(ex);
  };

  const handleHistorySelect = (item) => {
    setQuestion(item.question);
    if (item.response) {
      setResponse(item.response);
    }
  };

  const handleDownloadCSV = () => {
    if (!response || !response.rows.length) return;

    const csv = [
      response.columns.join(","),
      ...response.rows.map((row) =>
        response.columns
          .map((col) => {
            const value = row[col];
            return typeof value === "string" && value.includes(",") ? `"${value}"` : value;
          })
          .join(","),
      ),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `nlq_result_${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleCopySQL = async () => {
    if (!response?.sql) return;
    try {
      await navigator.clipboard.writeText(response.sql);
      setCopiedSql(true);
      setTimeout(() => setCopiedSql(false), 2000);
    } catch (error) {
      console.warn("Clipboard unavailable:", error);
    }
  };

  const statusSummary = useMemo(() => {
    if (isLoading) return "processing";
    if (!response) return "awaiting query";
    if (response.error) return "query failed";
    return "ready";
  }, [isLoading, response]);

  return (
    <section className={`${styles.console} glass-card`}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Natural Language Query</p>
          <h2 className={styles.title}>ICU NLQ Console</h2>
        </div>
        <div className={styles.headerControls}>
          <span className={styles.statusPill}>{statusSummary}</span>
          <span className={styles.backendPill}>Backend: Mock</span>
          <select
            className={`${styles.select} glass-input`}
            value={environment}
            onChange={(event) => setEnvironment(event.target.value)}
          >
            <option value="dev">Dev</option>
            <option value="prod">Prod</option>
          </select>
          {onClose && (
            <button className="glass-btn" onClick={onClose} style={{ marginLeft: '1rem' }}>
              ✕ Close
            </button>
          )}
        </div>
      </header>

      <div className={styles.body}>
        <div className={styles.panelColumn}>
          <div className={`${styles.panel} glass-panel`}>
            <div className={styles.panelHeader}>
              <h3>Query Input</h3>
              <span className={styles.panelHint}>Run ENTER or click</span>
            </div>
            <textarea
              className={`${styles.textarea} glass-input`}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleRun();
                }
              }}
              placeholder="질문을 입력하세요. (예: HR이 100 이상인 환자 보여줘)"
              disabled={isLoading}
            />
            <div className={styles.buttonRow}>
              <button className="glass-btn" onClick={handleRun} disabled={isLoading || !question.trim()}>
                Run
              </button>
              <button className="glass-btn" onClick={handleClear} disabled={isLoading}>
                Clear
              </button>
              <button className="glass-btn" onClick={handleUseExample} disabled={isLoading}>
                Use Example
              </button>

              <div className={styles.limitControl}>
                <span className={styles.limitLabel}>Limit:</span>
                <select
                  className={`${styles.select} glass-input ${styles.limitSelect}`}
                  value={limit}
                  onChange={(event) => setLimit(Number(event.target.value))}
                  disabled={isLoading}
                >
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
              </div>
            </div>
          </div>

          <div className={`${styles.panel} ${styles.historyPanel} glass-panel`}>
            <div className={styles.panelHeader}>
              <h3>Query History</h3>
              <span className={styles.panelHint}>Last 10</span>
            </div>
            {history.length === 0 ? (
              <div className={styles.emptyState}>No query history yet.</div>
            ) : (
              <div className={styles.historyList}>
                {history.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={styles.historyItem}
                    onClick={() => handleHistorySelect(item)}
                    disabled={isLoading}
                  >
                    <div>
                      <p className={styles.historyQuestion}>{item.question}</p>
                      <span className={styles.historyTime}>{formatHistoryTime(item.timestamp)}</span>
                    </div>
                    <span className={`${styles.historyStatus} ${STATUS_CLASS[item.status]}`}>
                      {STATUS_LABELS[item.status]}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className={styles.panelColumn}>
          <div className={`${styles.panel} ${styles.resultPanel} glass-panel`}>
            <div className={styles.panelHeader}>
              <h3>Result Panel</h3>
              <div className={styles.tabRow}>
                {["result", "sql", "logs"].map((tab) => (
                  <button
                    key={tab}
                    type="button"
                    className={`${styles.tabButton} ${activeTab === tab ? styles.tabActive : ""}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab.toUpperCase()}
                  </button>
                ))}
                <button className="glass-btn" onClick={handleDownloadCSV} disabled={!response?.rows?.length}>
                  Download CSV
                </button>
              </div>
            </div>

            <div className={styles.resultBody}>
              {isLoading && (
                <div className={styles.loadingState}>
                  <div className={styles.spinner} />
                  <p>Processing query...</p>
                </div>
              )}

              {!isLoading && !response && (
                <div className={styles.emptyState}>
                  <p>Enter a natural language query to get started.</p>
                </div>
              )}

              {!isLoading && response?.error && (
                <div className={styles.errorState}>
                  <p className={styles.errorTitle}>Query Failed</p>
                  <p className={styles.errorMessage}>{response.error}</p>
                  <button className="glass-btn" onClick={() => navigator.clipboard.writeText(response.error || "")}>
                    Copy Error
                  </button>
                </div>
              )}

              {!isLoading && response && !response.error && activeTab === "result" && (
                <div className={styles.resultStack}>
                  {/* Prioritize Table: If data exists, show table only (hide text summary to avoid duplication) */}
                  {response.rows && response.rows.length > 0 ? (
                    <div className={styles.resultStack}>
                      <DataTable columns={response.columns} rows={response.rows} />
                      <div className={styles.footerNote}>Showing {response.row_count} rows</div>
                    </div>
                  ) : (
                    /* Fallback to text answer if no table data */
                    response.answer && (
                      <div className={styles.answerBox}>
                        <h4 className={styles.answerTitle}>🤖 AI Answer</h4>
                        <p className={styles.answerText}>{response.answer}</p>
                      </div>
                    )
                  )}
                </div>
              )}

              {!isLoading && response && activeTab === "sql" && (
                <div className={styles.sqlPanel}>
                  {response.sql ? (
                    <>
                      <div className={styles.sqlActions}>
                        <button className="glass-btn" onClick={handleCopySQL}>
                          {copiedSql ? "Copied!" : "Copy SQL"}
                        </button>
                      </div>
                      <pre className={styles.sqlCode}>{response.sql}</pre>
                    </>
                  ) : (
                    <div className={styles.emptyState}>No SQL query available.</div>
                  )}
                </div>
              )}

              {!isLoading && response && activeTab === "logs" && (
                <div className={styles.logList}>
                  {response.logs.map((log, index) => (
                    <div key={`${log.step}-${index}`} className={styles.logItem}>
                      <div className={`${styles.logStatus} ${STATUS_CLASS[log.status]}`} />
                      <div>
                        <div className={styles.logHeader}>
                          <span className={styles.logStep}>{log.step}</span>
                          <span className={styles.logTime}>
                            {new Date(log.ts).toLocaleTimeString("ko-KR")}
                          </span>
                        </div>
                        <p className={styles.logMessage}>{log.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      {showExampleModal && (
        <div className={styles.modalOverlay}>
          <div className={`${styles.modalContent} glass-card`}>
            <div className={styles.modalHeader}>
              <h3>💡 Query Examples</h3>
              <button className="glass-btn" onClick={() => setShowExampleModal(false)}>
                Close
              </button>
            </div>
            <div className={styles.exampleList}>
              {EXAMPLE_QUERIES.map((ex, idx) => (
                <div key={idx} className={styles.exampleItem}>
                  <p className={styles.exampleText}>{ex}</p>
                  <button
                    className={`${styles.searchBtn} glass-btn`}
                    onClick={() => handleSelectExample(ex)}
                  >
                    Search
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default QueryConsole;
