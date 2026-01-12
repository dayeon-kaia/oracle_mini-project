export interface NLQRequest {
  question: string
  timeRange: {
    preset?: "6h" | "12h" | "24h"
    start?: string
    end?: string
  }
  limit: number
}

export interface NLQLog {
  step: string
  status: "success" | "warn" | "error"
  message: string
  ts: string
}

export interface NLQResponse {
  request_id: string
  question: string
  sql: string
  columns: string[]
  rows: Array<Record<string, any>>
  row_count: number
  warnings: string[]
  logs: NLQLog[]
  error?: string
}

export interface HistoryItem {
  id: string
  question: string
  timestamp: string
  status: "success" | "error"
  response?: NLQResponse
}
