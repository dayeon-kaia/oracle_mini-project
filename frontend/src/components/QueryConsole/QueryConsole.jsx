import { useEffect, useMemo, useState } from "react";
import styles from "./QueryConsole.module.css";

const EXAMPLE_QUERIES = [
  "stay_id 3456의 최근 24시간 HR, MAP, lactate 보여줘",
  "지난 24시간 lactate가 4 이상이 한 번이라도 있었던 환자 10명",
  "현재 활성 ICU 환자 중 예후 악화 가능성 높은 순으로 20명",
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
            <tr key={`${rowIndex}-${row[columns[0]]}`}>
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

function QueryConsole({ initialQuery }) {
  const [question, setQuestion] = useState(initialQuery || "");
  const [response, setResponse] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [environment, setEnvironment] = useState("dev");
  const [timeRange, setTimeRange] = useState("24h");
  const [limit, setLimit] = useState(50);
  const [activeTab, setActiveTab] = useState("result");
  const [copiedSql, setCopiedSql] = useState(false);

  const handleRun = async (overrideQuestion = null) => {
    const queryTerm = typeof overrideQuestion === 'string' ? overrideQuestion : question;
    if (!queryTerm.trim() || isLoading) return;

    setIsLoading(true);
    setResponse(null);
    setActiveTab("result");

    try {
      const res = await fetch("http://localhost:3000/api/nlq", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: queryTerm,
          timeRange: { preset: timeRange },
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
    const randomExample = EXAMPLE_QUERIES[Math.floor(Math.random() * EXAMPLE_QUERIES.length)];
    setQuestion(randomExample);
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
              placeholder="예시:\n- stay_id 3456의 최근 24시간 HR, MAP, lactate 보여줘\n- 지난 24시간 lactate가 4 이상이 한 번이라도 있었던 환자 10명"
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
            </div>
          </div>

          <div className={`${styles.panel} glass-panel`}>
            <div className={styles.panelHeader}>
              <h3>Query Options</h3>
              <span className={styles.panelHint}>SELECT only</span>
            </div>
            <div className={styles.optionGrid}>
              <label>
                <span>Time Range</span>
                <select
                  className={`${styles.select} glass-input`}
                  value={timeRange}
                  onChange={(event) => setTimeRange(event.target.value)}
                  disabled={isLoading}
                >
                  <option value="6h">Last 6 hours</option>
                  <option value="12h">Last 12 hours</option>
                  <option value="24h">Last 24 hours</option>
                  <option value="custom">Custom</option>
                </select>
              </label>
              <label>
                <span>Row Limit</span>
                <select
                  className={`${styles.select} glass-input`}
                  value={limit}
                  onChange={(event) => setLimit(Number(event.target.value))}
                  disabled={isLoading}
                >
                  <option value={50}>50 rows</option>
                  <option value={100}>100 rows</option>
                  <option value={200}>200 rows</option>
                </select>
              </label>
            </div>
            <p className={styles.mutedNote}>Queries are read-only. Mutations are blocked.</p>
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
                  {response.warnings.length > 0 && (
                    <div className={styles.warningBox}>
                      {response.warnings.map((warning, index) => (
                        <p key={`${warning}-${index}`}>{warning}</p>
                      ))}
                    </div>
                  )}
                  <DataTable columns={response.columns} rows={response.rows} />
                  <div className={styles.footerNote}>Showing {response.row_count} rows</div>
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
    </section>
  );
}

export default QueryConsole;
