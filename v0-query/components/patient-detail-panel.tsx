"use client"

import { X } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  BarChart,
  Bar,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts"

const riskTrendData = [
  { time: "-24h", mortality: 15, vent: 10, pressor: 8 },
  { time: "-18h", mortality: 22, vent: 15, pressor: 12 },
  { time: "-12h", mortality: 35, vent: 28, pressor: 22 },
  { time: "-6h", mortality: 52, vent: 45, pressor: 38 },
  { time: "-2h", mortality: 68, vent: 62, pressor: 55 },
  { time: "now", mortality: 78, vent: 72, pressor: 68 },
]

const spo2Data = [
  { value: 98 },
  { value: 96 },
  { value: 94 },
  { value: 92 },
  { value: 90 },
  { value: 88 },
  { value: 86 },
  { value: 84 },
]

const rrData = [
  { value: 18 },
  { value: 20 },
  { value: 22 },
  { value: 24 },
  { value: 26 },
  { value: 28 },
  { value: 30 },
  { value: 32 },
]

const vitalsTimeSeriesData = [
  { time: "-24h", spo2: 98, rr: 18, hr: 75, map: 85, temp: 36.8 },
  { time: "-20h", spo2: 97, rr: 19, hr: 78, map: 83, temp: 36.9 },
  { time: "-16h", spo2: 96, rr: 20, hr: 82, map: 82, temp: 37.1 },
  { time: "-12h", spo2: 94, rr: 22, hr: 88, map: 80, temp: 37.3 },
  { time: "-8h", spo2: 92, rr: 24, hr: 95, map: 78, temp: 37.6 },
  { time: "-4h", spo2: 90, rr: 26, hr: 102, map: 76, temp: 37.8 },
  { time: "-2h", spo2: 88, rr: 28, hr: 108, map: 74, temp: 38.0 },
  { time: "now", spo2: 84, rr: 32, hr: 115, map: 72, temp: 38.2 },
]

const vitalsRadarData = [
  { vital: "SpO2", value: 84, fullMark: 100 },
  { vital: "MAP", value: 72, fullMark: 100 },
  { vital: "HR", value: 58, fullMark: 100 }, // normalized (115 / 200 * 100)
  { vital: "RR", value: 64, fullMark: 100 }, // normalized (32 / 50 * 100)
  { vital: "Temp", value: 95, fullMark: 100 }, // normalized ((38.2 - 35) / 4 * 100)
]

const vitalsHeatmapData = [
  { vital: "SpO2", "-24h": 98, "-20h": 97, "-16h": 96, "-12h": 94, "-8h": 92, "-4h": 90, "-2h": 88, now: 84 },
  { vital: "RR", "-24h": 18, "-20h": 19, "-16h": 20, "-12h": 22, "-8h": 24, "-4h": 26, "-2h": 28, now: 32 },
  { vital: "HR", "-24h": 75, "-20h": 78, "-16h": 82, "-12h": 88, "-8h": 95, "-4h": 102, "-2h": 108, now: 115 },
  { vital: "MAP", "-24h": 85, "-20h": 83, "-16h": 82, "-12h": 80, "-8h": 78, "-4h": 76, "-2h": 74, now: 72 },
]

const shapData = [
  { feature: "RR_slope", value: 0.25, impact: "high" },
  { feature: "SpO2_current", value: 0.18, impact: "high" },
  { feature: "HR_variability", value: 0.12, impact: "medium" },
  { feature: "MAP_trend", value: 0.08, impact: "medium" },
  { feature: "Lactate_level", value: 0.06, impact: "low" },
]

const actions = [
  {
    priority: "STAT",
    condition: "SpO2 84% (< 90%)",
    action: "기관 삽관 인공호흡기 시도",
    source: "📚 2024 성인 패혈증 초기치료지침서, p.12",
  },
  {
    priority: "HIGH",
    condition: "RR 32 bpm (> 30)",
    action: "산소 공급 증량 (FiO2 상향)",
    source: "📚 급성호흡부전 관리지침, p.8",
  },
  {
    priority: "MEDIUM",
    condition: "Mortality Risk > 75%",
    action: "중환자의학과 컨설트 요청",
    source: "📚 병원 내부 프로토콜, ICU-001",
  },
]

interface PatientDetailPanelProps {
  patientId?: string
  bedLocation?: string
  onClose?: () => void
}

export function PatientDetailPanel({
  patientId = "P9",
  bedLocation = "MICU - Bed 1",
  onClose,
}: PatientDetailPanelProps) {
  const [vitalVizType, setVitalVizType] = useState<"area" | "line" | "bar" | "radar" | "heatmap">("area")

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "STAT":
        return "from-red-500 to-red-700"
      case "HIGH":
        return "from-orange-500 to-orange-700"
      case "MEDIUM":
        return "from-yellow-500 to-yellow-700"
      default:
        return "from-gray-500 to-gray-700"
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "high":
        return "#ef4444"
      case "medium":
        return "#f59e0b"
      case "low":
        return "#10b981"
      default:
        return "#6b7280"
    }
  }

  const getHeatmapColor = (vital: string, value: number) => {
    if (vital === "SpO2") {
      if (value >= 95) return "#10b981" // green
      if (value >= 90) return "#eab308" // yellow
      return "#ef4444" // red
    }
    if (vital === "RR") {
      if (value <= 20) return "#10b981"
      if (value <= 25) return "#eab308"
      return "#ef4444"
    }
    if (vital === "HR") {
      if (value <= 90) return "#10b981"
      if (value <= 105) return "#eab308"
      return "#ef4444"
    }
    if (vital === "MAP") {
      if (value >= 80) return "#10b981"
      if (value >= 75) return "#eab308"
      return "#ef4444"
    }
    return "#6b7280"
  }

  return (
    <div className="h-screen w-full bg-black/95 text-white overflow-y-auto">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="glass-strong rounded-xl p-6 flex items-center justify-between shadow-xl border-cyan-500/30">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Patient {patientId}
            </h1>
            <p className="text-cyan-300/80 text-sm mt-1">{bedLocation}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="hover:bg-red-500/20 hover:text-red-400 transition-colors"
          >
            <X className="h-6 w-6" />
          </Button>
        </div>

        {/* Section 1: 24-hour Risk Score Trend */}
        <Card className="glass-strong border-purple-500/30 shadow-2xl">
          <div className="p-6 space-y-4">
            <h2 className="text-xl font-semibold text-purple-300">24-hour Risk Score Trend</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={riskTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} />
                <YAxis
                  stroke="rgba(255,255,255,0.5)"
                  style={{ fontSize: "12px" }}
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0,0,0,0.9)",
                    border: "1px solid rgba(255,255,255,0.2)",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "#fff" }}
                />
                <Legend wrapperStyle={{ fontSize: "14px" }} />
                <Line
                  type="monotone"
                  dataKey="mortality"
                  stroke="#ef4444"
                  strokeWidth={3}
                  name="Mortality (24h)"
                  dot={{ fill: "#ef4444", r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="vent"
                  stroke="#06b6d4"
                  strokeWidth={3}
                  name="Vent_start (12h)"
                  dot={{ fill: "#06b6d4", r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="pressor"
                  stroke="#eab308"
                  strokeWidth={3}
                  name="Pressor_start (12h)"
                  dot={{ fill: "#eab308", r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Section 2: Vitals Trend - Multiple Visualizations */}
        <Card className="glass-strong border-cyan-500/30 shadow-2xl">
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-cyan-300">Vitals Trend (24h)</h2>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant={vitalVizType === "area" ? "default" : "outline"}
                  onClick={() => setVitalVizType("area")}
                  className={
                    vitalVizType === "area"
                      ? "bg-cyan-500 hover:bg-cyan-600"
                      : "border-cyan-500/30 hover:bg-cyan-500/20"
                  }
                >
                  Area
                </Button>
                <Button
                  size="sm"
                  variant={vitalVizType === "line" ? "default" : "outline"}
                  onClick={() => setVitalVizType("line")}
                  className={
                    vitalVizType === "line"
                      ? "bg-cyan-500 hover:bg-cyan-600"
                      : "border-cyan-500/30 hover:bg-cyan-500/20"
                  }
                >
                  Line
                </Button>
                <Button
                  size="sm"
                  variant={vitalVizType === "bar" ? "default" : "outline"}
                  onClick={() => setVitalVizType("bar")}
                  className={
                    vitalVizType === "bar" ? "bg-cyan-500 hover:bg-cyan-600" : "border-cyan-500/30 hover:bg-cyan-500/20"
                  }
                >
                  Bar
                </Button>
                <Button
                  size="sm"
                  variant={vitalVizType === "radar" ? "default" : "outline"}
                  onClick={() => setVitalVizType("radar")}
                  className={
                    vitalVizType === "radar"
                      ? "bg-cyan-500 hover:bg-cyan-600"
                      : "border-cyan-500/30 hover:bg-cyan-500/20"
                  }
                >
                  Radar
                </Button>
                <Button
                  size="sm"
                  variant={vitalVizType === "heatmap" ? "default" : "outline"}
                  onClick={() => setVitalVizType("heatmap")}
                  className={
                    vitalVizType === "heatmap"
                      ? "bg-cyan-500 hover:bg-cyan-600"
                      : "border-cyan-500/30 hover:bg-cyan-500/20"
                  }
                >
                  Heatmap
                </Button>
              </div>
            </div>

            {vitalVizType === "area" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* SpO2 Trend */}
                <div className="glass rounded-lg p-4 border-red-500/30">
                  <h3 className="text-sm text-gray-300 mb-2">SpO2 Trend</h3>
                  <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-4xl font-bold text-red-400">84%</span>
                    <span className="text-sm text-red-300">(Decreasing)</span>
                  </div>
                  <ResponsiveContainer width="100%" height={80}>
                    <AreaChart data={spo2Data}>
                      <defs>
                        <linearGradient id="spo2Gradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#ef4444"
                        strokeWidth={2}
                        fill="url(#spo2Gradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* RR Trend */}
                <div className="glass rounded-lg p-4 border-yellow-500/30">
                  <h3 className="text-sm text-gray-300 mb-2">RR (Resp. Rate) Trend</h3>
                  <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-4xl font-bold text-yellow-400">32 bpm</span>
                    <span className="text-sm text-yellow-300">(Increasing)</span>
                  </div>
                  <ResponsiveContainer width="100%" height={80}>
                    <AreaChart data={rrData}>
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

            {vitalVizType === "line" && (
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={vitalsTimeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="time" stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} />
                  <YAxis stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "rgba(0,0,0,0.9)",
                      border: "1px solid rgba(255,255,255,0.2)",
                      borderRadius: "8px",
                    }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "14px" }} />
                  <Line type="monotone" dataKey="spo2" stroke="#ef4444" strokeWidth={2} name="SpO2 (%)" />
                  <Line type="monotone" dataKey="rr" stroke="#eab308" strokeWidth={2} name="RR (bpm)" />
                  <Line type="monotone" dataKey="hr" stroke="#06b6d4" strokeWidth={2} name="HR (bpm)" />
                  <Line type="monotone" dataKey="map" stroke="#a855f7" strokeWidth={2} name="MAP (mmHg)" />
                </LineChart>
              </ResponsiveContainer>
            )}

            {vitalVizType === "bar" && (
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={[
                    {
                      vital: "SpO2",
                      "24h ago": vitalsTimeSeriesData[0].spo2,
                      Current: vitalsTimeSeriesData[vitalsTimeSeriesData.length - 1].spo2,
                    },
                    {
                      vital: "RR",
                      "24h ago": vitalsTimeSeriesData[0].rr,
                      Current: vitalsTimeSeriesData[vitalsTimeSeriesData.length - 1].rr,
                    },
                    {
                      vital: "HR",
                      "24h ago": vitalsTimeSeriesData[0].hr,
                      Current: vitalsTimeSeriesData[vitalsTimeSeriesData.length - 1].hr,
                    },
                    {
                      vital: "MAP",
                      "24h ago": vitalsTimeSeriesData[0].map,
                      Current: vitalsTimeSeriesData[vitalsTimeSeriesData.length - 1].map,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="vital" stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} />
                  <YAxis stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "rgba(0,0,0,0.9)",
                      border: "1px solid rgba(255,255,255,0.2)",
                      borderRadius: "8px",
                    }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "14px" }} />
                  <Bar dataKey="24h ago" fill="#06b6d4" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="Current" fill="#ef4444" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}

            {vitalVizType === "radar" && (
              <div className="flex flex-col items-center">
                <ResponsiveContainer width="100%" height={400}>
                  <RadarChart data={vitalsRadarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.2)" />
                    <PolarAngleAxis dataKey="vital" stroke="rgba(255,255,255,0.7)" style={{ fontSize: "14px" }} />
                    <PolarRadiusAxis stroke="rgba(255,255,255,0.3)" style={{ fontSize: "12px" }} />
                    <Radar
                      name="Current Vitals"
                      dataKey="value"
                      stroke="#06b6d4"
                      fill="#06b6d4"
                      fillOpacity={0.6}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
                <p className="text-sm text-gray-400 mt-2">
                  * Values normalized to 0-100 scale for comparison (Current snapshot)
                </p>
              </div>
            )}

            {vitalVizType === "heatmap" && (
              <div className="space-y-3">
                {vitalsHeatmapData.map((vitalRow) => (
                  <div key={vitalRow.vital} className="glass rounded-lg p-4">
                    <h3 className="text-sm text-gray-300 mb-3 font-semibold">{vitalRow.vital}</h3>
                    <div className="grid grid-cols-8 gap-2">
                      {Object.entries(vitalRow)
                        .filter(([key]) => key !== "vital")
                        .map(([timePoint, value]) => (
                          <div key={timePoint} className="flex flex-col items-center gap-1">
                            <div
                              className="w-full h-16 rounded-lg flex items-center justify-center font-bold text-white shadow-lg transition-transform hover:scale-110"
                              style={{ backgroundColor: getHeatmapColor(vitalRow.vital, value as number) }}
                            >
                              {value}
                            </div>
                            <span className="text-xs text-gray-400">{timePoint}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
                <p className="text-sm text-gray-400 text-center mt-4">
                  🟢 Green = Normal | 🟡 Yellow = Warning | 🔴 Red = Critical
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Section 3: LLM Clinical Summary */}
        <Card className="glass-strong border-blue-500/30 shadow-2xl">
          <div className="p-6 space-y-4">
            <h2 className="text-xl font-semibold text-blue-300">
              ✨ LLM 기반 임상 요약 (AI-Generated Clinical Summary)
            </h2>
            <div className="glass rounded-lg p-4 text-gray-200 leading-relaxed">
              <p>
                환자는 지난 24시간 동안 SpO2 저하(84%), 호흡수 증가(32bpm)를 보이며 급성 호흡부전 징후가 뚜렷합니다.
                Mortality risk가 78%로 매우 높은 상태이며, 인공호흡기 적용 확률(72%)과 승압제 투여 필요성(68%)이 모두
                증가 추세입니다. 현재 vitals 추세를 고려할 때 즉각적인 중환자 처치가 필요한 것으로 판단됩니다.
              </p>
            </div>
          </div>
        </Card>

        {/* Section 4: Patient-Specific Actions */}
        <Card className="glass-strong border-green-500/30 shadow-2xl">
          <div className="p-6 space-y-4">
            <div>
              <h2 className="text-xl font-semibold text-green-300">📋 Patient-Specific Actions</h2>
              <p className="text-sm text-gray-400 mt-1">Based on Current Vitals & Clinical Guidelines (RAG)</p>
            </div>
            <div className="space-y-3">
              {actions.map((action, index) => (
                <div
                  key={index}
                  className="glass rounded-lg p-4 flex items-start gap-4 hover:bg-white/10 transition-colors"
                >
                  <Checkbox className="mt-1" />
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r ${getPriorityColor(
                          action.priority,
                        )} text-white shadow-lg`}
                      >
                        {action.priority}
                      </span>
                      <span className="text-yellow-300 text-sm">{action.condition}</span>
                    </div>
                    <div className="text-white">
                      <span className="text-cyan-400 mr-2">→</span>
                      {action.action}
                    </div>
                    <div className="text-xs text-gray-400">{action.source}</div>
                  </div>
                  <Button
                    size="sm"
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white shadow-lg"
                  >
                    실행
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Section 5: Key Risk Factors (SHAP) */}
        <Card className="glass-strong border-orange-500/30 shadow-2xl">
          <div className="p-6 space-y-4">
            <h2 className="text-xl font-semibold text-orange-300">Key Risk Factors (SHAP)</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={shapData} layout="vertical" margin={{ left: 100, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis type="number" stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} domain={[0, 0.3]} />
                <YAxis type="category" dataKey="feature" stroke="rgba(255,255,255,0.5)" style={{ fontSize: "12px" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0,0,0,0.9)",
                    border: "1px solid rgba(255,255,255,0.2)",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "#fff" }}
                />
                <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                  {shapData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getImpactColor(entry.impact)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  )
}
