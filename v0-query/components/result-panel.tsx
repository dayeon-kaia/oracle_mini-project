"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Download, Copy, CheckCircle, XCircle, AlertCircle, Info } from "lucide-react"
import type { NLQResponse } from "@/lib/types"
import { DataTable } from "./data-table"
import { Badge } from "@/components/ui/badge"

interface ResultPanelProps {
  response: NLQResponse | null
  isLoading: boolean
}

export function ResultPanel({ response, isLoading }: ResultPanelProps) {
  const [copiedSql, setCopiedSql] = useState(false)

  const handleCopySQL = () => {
    if (response?.sql) {
      navigator.clipboard.writeText(response.sql)
      setCopiedSql(true)
      setTimeout(() => setCopiedSql(false), 2000)
    }
  }

  const handleDownloadCSV = () => {
    if (!response || !response.rows.length) return

    const csv = [
      response.columns.join(","),
      ...response.rows.map((row) =>
        response.columns
          .map((col) => {
            const value = row[col]
            return typeof value === "string" && value.includes(",") ? `"${value}"` : value
          })
          .join(","),
      ),
    ].join("\n")

    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `nlq_result_${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case "error":
        return <XCircle className="w-4 h-4 text-red-500" />
      case "warn":
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      default:
        return <Info className="w-4 h-4 text-blue-500" />
    }
  }

  if (isLoading) {
    return (
      <Card className="h-full flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-muted-foreground">Processing query...</p>
        </div>
      </Card>
    )
  }

  if (!response) {
    return (
      <Card className="h-full flex items-center justify-center">
        <div className="text-center space-y-2 text-muted-foreground">
          <Info className="w-12 h-12 mx-auto opacity-50" />
          <p className="text-sm">Enter a natural language query to get started</p>
        </div>
      </Card>
    )
  }

  if (response.error) {
    return (
      <Card className="h-full flex items-center justify-center">
        <div className="text-center space-y-3 max-w-md">
          <XCircle className="w-12 h-12 mx-auto text-destructive" />
          <h3 className="font-semibold">Query Failed</h3>
          <p className="text-sm text-muted-foreground">{response.error}</p>
          <Button variant="outline" size="sm" onClick={() => navigator.clipboard.writeText(response.error || "")}>
            <Copy className="w-4 h-4 mr-2" />
            Copy Error
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <Card className="h-full flex flex-col">
      <Tabs defaultValue="result" className="flex-1 flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <TabsList>
            <TabsTrigger value="result">Result</TabsTrigger>
            <TabsTrigger value="sql">SQL</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
          </TabsList>
          <Button variant="outline" size="sm" onClick={handleDownloadCSV}>
            <Download className="w-4 h-4 mr-2" />
            Download CSV
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden flex flex-col">
          <TabsContent value="result" className="flex-1 mt-0 overflow-hidden flex flex-col space-y-3">
            {response.warnings.length > 0 && (
              <div className="flex items-start gap-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
                <AlertCircle className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />
                <div className="flex-1 text-xs text-yellow-600 dark:text-yellow-400">
                  {response.warnings.map((warning, i) => (
                    <p key={i}>{warning}</p>
                  ))}
                </div>
              </div>
            )}
            <div className="flex-1 overflow-hidden">
              <DataTable columns={response.columns} rows={response.rows} />
            </div>
            <div className="text-xs text-muted-foreground">Showing {response.row_count} rows</div>
          </TabsContent>

          <TabsContent value="sql" className="flex-1 mt-0 overflow-auto">
            {response.sql ? (
              <div className="space-y-3">
                <div className="flex justify-end">
                  <Button variant="outline" size="sm" onClick={handleCopySQL}>
                    {copiedSql ? <CheckCircle className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                    {copiedSql ? "Copied!" : "Copy SQL"}
                  </Button>
                </div>
                <pre className="p-4 bg-muted rounded-md text-xs font-mono overflow-x-auto">{response.sql}</pre>
              </div>
            ) : (
              <div className="text-center py-8 text-sm text-muted-foreground">No SQL query available</div>
            )}
          </TabsContent>

          <TabsContent value="logs" className="flex-1 mt-0 overflow-auto">
            <div className="space-y-3">
              {response.logs.map((log, i) => (
                <div key={i} className="flex gap-3 p-3 border rounded-md">
                  <div className="shrink-0 mt-0.5">{getStatusIcon(log.status)}</div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="font-mono text-xs">
                        {log.step}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(log.ts).toLocaleTimeString("ko-KR")}
                      </span>
                    </div>
                    <p className="text-sm">{log.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </CardContent>
      </Tabs>
    </Card>
  )
}
