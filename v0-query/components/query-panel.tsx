"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Clock, Play, X, FileText, Info } from "lucide-react"
import type { HistoryItem } from "@/lib/types"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

interface QueryPanelProps {
  question: string
  setQuestion: (q: string) => void
  onRun: () => void
  onClear: () => void
  isLoading: boolean
  history: HistoryItem[]
  onHistorySelect: (item: HistoryItem) => void
  timeRange: string
  setTimeRange: (t: string) => void
  limit: number
  setLimit: (l: number) => void
}

const EXAMPLE_QUERIES = [
  "stay_id 3456의 최근 24시간 HR, MAP, lactate 보여줘",
  "지난 24시간 lactate가 4 이상이 한 번이라도 있었던 환자 10명",
  "현재 활성 ICU 환자 중 사망 위험도 높은 순으로 20명",
]

export function QueryPanel({
  question,
  setQuestion,
  onRun,
  onClear,
  isLoading,
  history,
  onHistorySelect,
  timeRange,
  setTimeRange,
  limit,
  setLimit,
}: QueryPanelProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      onRun()
    }
  }

  const handleUseExample = () => {
    const randomExample = EXAMPLE_QUERIES[Math.floor(Math.random() * EXAMPLE_QUERIES.length)]
    setQuestion(randomExample)
  }

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Natural Language Input */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Natural Language Query</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="예시:&#10;• stay_id 3456의 최근 24시간 HR, MAP, lactate 보여줘&#10;• 지난 24시간 lactate가 4 이상이 한 번이라도 있었던 환자 10명"
            className="min-h-32 resize-none font-mono text-sm"
            disabled={isLoading}
          />
          <div className="flex gap-2">
            <Button onClick={onRun} disabled={isLoading || !question.trim()} size="sm">
              <Play className="w-4 h-4 mr-2" />
              Run
            </Button>
            <Button onClick={onClear} variant="outline" size="sm" disabled={isLoading}>
              <X className="w-4 h-4 mr-2" />
              Clear
            </Button>
            <Button onClick={handleUseExample} variant="secondary" size="sm" disabled={isLoading}>
              <FileText className="w-4 h-4 mr-2" />
              Use Example
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Query Options */}
      <Accordion type="single" collapsible defaultValue="options">
        <AccordionItem value="options">
          <Card>
            <AccordionTrigger className="px-6 py-4 hover:no-underline">
              <CardTitle className="text-sm font-medium">Query Options</CardTitle>
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="space-y-4 pt-0">
                <div className="space-y-2">
                  <label className="text-xs text-muted-foreground">Time Range</label>
                  <Select value={timeRange} onValueChange={setTimeRange} disabled={isLoading}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="6h">Last 6 hours</SelectItem>
                      <SelectItem value="12h">Last 12 hours</SelectItem>
                      <SelectItem value="24h">Last 24 hours</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-muted-foreground">Row Limit</label>
                  <Select
                    value={limit.toString()}
                    onValueChange={(v) => setLimit(Number.parseInt(v))}
                    disabled={isLoading}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="50">50 rows</SelectItem>
                      <SelectItem value="100">100 rows</SelectItem>
                      <SelectItem value="200">200 rows</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="font-mono text-xs">
                    Read-only / SELECT only
                  </Badge>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="w-3.5 h-3.5 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="text-xs max-w-xs">
                          All queries are restricted to SELECT operations only. Data modification queries (INSERT,
                          UPDATE, DELETE) are not allowed.
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>

      {/* History */}
      <Card className="flex-1 overflow-hidden flex flex-col">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Query History</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto">
          {history.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">No query history yet</p>
          ) : (
            <div className="space-y-2">
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onHistorySelect(item)}
                  disabled={isLoading}
                  className="w-full text-left p-3 rounded-md border hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs font-mono line-clamp-2 flex-1">{item.question}</p>
                    <Badge variant={item.status === "success" ? "default" : "destructive"} className="text-xs shrink-0">
                      {item.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1 mt-1.5 text-xs text-muted-foreground">
                    <Clock className="w-3 h-3" />
                    {new Date(item.timestamp).toLocaleString("ko-KR", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
