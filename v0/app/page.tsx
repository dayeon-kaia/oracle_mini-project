"use client"

import { useState } from "react"
import { QueryPanel } from "@/components/query-panel"
import { ResultPanel } from "@/components/result-panel"
import { ThemeToggle } from "@/components/theme-toggle"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { NLQResponse, HistoryItem } from "@/lib/types"

export default function Home() {
  const [question, setQuestion] = useState("")
  const [response, setResponse] = useState<NLQResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [environment, setEnvironment] = useState<"dev" | "prod">("dev")
  const [timeRange, setTimeRange] = useState("24h")
  const [limit, setLimit] = useState(50)

  const handleRun = async () => {
    if (!question.trim() || isLoading) return

    setIsLoading(true)
    setResponse(null)

    try {
      const res = await fetch("/api/nlq", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          timeRange: { preset: timeRange },
          limit,
        }),
      })

      const data: NLQResponse = await res.json()
      setResponse(data)

      // Add to history
      const historyItem: HistoryItem = {
        id: data.request_id,
        question,
        timestamp: new Date().toISOString(),
        status: data.error ? "error" : "success",
        response: data,
      }
      setHistory((prev) => [historyItem, ...prev.slice(0, 9)])
    } catch (error) {
      console.error("[v0] Query execution error:", error)
      setResponse({
        request_id: `err_${Date.now()}`,
        question,
        sql: "",
        columns: [],
        rows: [],
        row_count: 0,
        warnings: [],
        error: "Network error. Please try again.",
        logs: [],
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setQuestion("")
    setResponse(null)
  }

  const handleHistorySelect = (item: HistoryItem) => {
    setQuestion(item.question)
    if (item.response) {
      setResponse(item.response)
    }
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold">ICU NLQ Console</h1>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Badge variant="outline" className="font-mono">
              Backend: Mock
            </Badge>
            <Select value={environment} onValueChange={(v) => setEnvironment(v as "dev" | "prod")}>
              <SelectTrigger className="w-28">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dev">Dev</SelectItem>
                <SelectItem value="prod">Prod</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6 h-[calc(100vh-73px)]">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 h-full">
          {/* Query Panel - 40% */}
          <div className="lg:col-span-2 h-full overflow-auto">
            <QueryPanel
              question={question}
              setQuestion={setQuestion}
              onRun={handleRun}
              onClear={handleClear}
              isLoading={isLoading}
              history={history}
              onHistorySelect={handleHistorySelect}
              timeRange={timeRange}
              setTimeRange={setTimeRange}
              limit={limit}
              setLimit={setLimit}
            />
          </div>

          {/* Result Panel - 60% */}
          <div className="lg:col-span-3 h-full overflow-hidden">
            <ResultPanel response={response} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </main>
  )
}
