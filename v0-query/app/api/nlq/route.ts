import { type NextRequest, NextResponse } from "next/server"
import type { NLQRequest, NLQResponse } from "@/lib/types"

// Mock data generators
function generateMockLactateData(limit: number) {
  const columns = ["stay_id", "charttime", "hr", "map", "lactate"]
  const rows = []
  const now = new Date()

  for (let i = 0; i < limit; i++) {
    const hoursAgo = Math.floor(Math.random() * 24)
    const charttime = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000)
    rows.push({
      stay_id: Math.floor(Math.random() * 9000) + 1000,
      charttime: charttime.toISOString(),
      hr: Math.floor(Math.random() * 40) + 60,
      map: Math.floor(Math.random() * 30) + 65,
      lactate: (Math.random() * 5 + 1).toFixed(1),
    })
  }

  return { columns, rows }
}

function generateMockStayData(stayId: string, limit: number) {
  const columns = ["stay_id", "charttime", "hr", "map", "spo2", "temp"]
  const rows = []
  const now = new Date()

  for (let i = 0; i < limit; i++) {
    const hoursAgo = i
    const charttime = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000)
    rows.push({
      stay_id: stayId,
      charttime: charttime.toISOString(),
      hr: Math.floor(Math.random() * 30) + 70,
      map: Math.floor(Math.random() * 25) + 70,
      spo2: Math.floor(Math.random() * 5) + 95,
      temp: (Math.random() * 2 + 36.5).toFixed(1),
    })
  }

  return { columns, rows }
}

function generateMockPatientList(limit: number) {
  const columns = ["stay_id", "icu_unit", "bed_id", "asof", "risk_mortality_24h"]
  const rows = []
  const units = ["MICU", "SICU", "CSRU", "CCU"]
  const now = new Date()

  for (let i = 0; i < limit; i++) {
    rows.push({
      stay_id: Math.floor(Math.random() * 9000) + 1000,
      icu_unit: units[Math.floor(Math.random() * units.length)],
      bed_id: `B${Math.floor(Math.random() * 20) + 1}`,
      asof: now.toISOString(),
      risk_mortality_24h: (Math.random() * 0.4 + 0.05).toFixed(3),
    })
  }

  return { columns, rows }
}

export async function POST(request: NextRequest) {
  try {
    const body: NLQRequest = await request.json()
    const { question, limit } = body

    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700))

    // 10% chance of error for testing
    if (Math.random() < 0.1) {
      const errorResponse: NLQResponse = {
        request_id: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        question,
        sql: "",
        columns: [],
        rows: [],
        row_count: 0,
        warnings: [],
        error: "Failed to parse natural language query. Please rephrase your question.",
        logs: [
          {
            step: "received_question",
            status: "success",
            message: `Received query: "${question}"`,
            ts: new Date().toISOString(),
          },
          {
            step: "generated_sql",
            status: "error",
            message: "NLU model failed to generate valid SQL",
            ts: new Date().toISOString(),
          },
        ],
      }
      return NextResponse.json(errorResponse, { status: 400 })
    }

    // Generate mock data based on question content
    let mockData
    let sql = ""

    if (question.toLowerCase().includes("lactate")) {
      mockData = generateMockLactateData(Math.min(limit, 30))
      sql = `SELECT stay_id, charttime, hr, map, lactate\nFROM lab_vitals\nWHERE lactate >= 4.0\n  AND charttime >= NOW() - INTERVAL '24 hours'\nORDER BY charttime DESC\nLIMIT ${limit};`
    } else if (question.toLowerCase().includes("stay_id")) {
      const stayIdMatch = question.match(/\d{4}/)
      const stayId = stayIdMatch ? stayIdMatch[0] : "3456"
      mockData = generateMockStayData(stayId, Math.min(limit, 24))
      sql = `SELECT stay_id, charttime, hr, map, spo2, temp\nFROM vitals\nWHERE stay_id = ${stayId}\n  AND charttime >= NOW() - INTERVAL '24 hours'\nORDER BY charttime DESC\nLIMIT ${limit};`
    } else {
      mockData = generateMockPatientList(Math.min(limit, 50))
      sql = `SELECT stay_id, icu_unit, bed_id, asof, risk_mortality_24h\nFROM icu_patients\nWHERE status = 'active'\nORDER BY risk_mortality_24h DESC\nLIMIT ${limit};`
    }

    const response: NLQResponse = {
      request_id: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      question,
      sql,
      columns: mockData.columns,
      rows: mockData.rows,
      row_count: mockData.rows.length,
      warnings: mockData.rows.length >= limit ? [`Result set truncated to ${limit} rows`] : [],
      logs: [
        {
          step: "received_question",
          status: "success",
          message: `Received query: "${question}"`,
          ts: new Date().toISOString(),
        },
        {
          step: "generated_sql",
          status: "success",
          message: "NLU model generated SQL query",
          ts: new Date(Date.now() + 200).toISOString(),
        },
        {
          step: "validated_sql",
          status: "success",
          message: "SQL validation passed (SELECT only, no mutations)",
          ts: new Date(Date.now() + 400).toISOString(),
        },
        {
          step: "executed_query",
          status: "success",
          message: `Query executed in ${(Math.random() * 300 + 100).toFixed(0)}ms`,
          ts: new Date(Date.now() + 600).toISOString(),
        },
        {
          step: "returned_rows",
          status: "success",
          message: `Returned ${mockData.rows.length} rows`,
          ts: new Date(Date.now() + 800).toISOString(),
        },
      ],
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error("[v0] NLQ API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
