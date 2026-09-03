import React from "react";
import { CheckCircle2, XCircle, AlertCircle, Clock, Percent, ShieldCheck, ArrowUpRight, Zap, Award } from "lucide-react";

export default function DashboardView({ analytics, onNavigate }) {
  if (!analytics) return <div className="p-8 text-center text-gray-400">Loading Dashboard Metrics...</div>;

  const kpis = [
    { label: "TOTAL DECISIONS", value: analytics.total_decisions, icon: ShieldCheck, color: "text-cyan-400", bg: "bg-cyan-950/40 border-cyan-800/40" },
    { label: "APPROVED", value: analytics.approved_count, icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-950/40 border-emerald-800/40" },
    { label: "REJECTED", value: analytics.rejected_count, icon: XCircle, color: "text-rose-400", bg: "bg-rose-950/40 border-rose-800/40" },
    { label: "PENDING HUMAN REVIEW", value: analytics.pending_review_count, icon: AlertCircle, color: "text-amber-400", bg: "bg-amber-950/40 border-amber-800/40" },
    { label: "MODEL AGREEMENT RATE", value: `${analytics.model_agreement_rate}%`, icon: Percent, color: "text-indigo-400", bg: "bg-indigo-950/40 border-indigo-800/40" },
    { label: "AVG CONFIDENCE", value: `${analytics.average_confidence}%`, icon: Award, color: "text-purple-400", bg: "bg-purple-950/40 border-purple-800/40" },
    { label: "AVG RESPONSE TIME", value: `${analytics.average_response_time} ms`, icon: Zap, color: "text-blue-400", bg: "bg-blue-950/40 border-blue-800/40" },
    { label: "HUMAN REVIEW RATE", value: `${analytics.human_review_rate}%`, icon: Clock, color: "text-rose-400", bg: "bg-rose-950/40 border-rose-800/40" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner / Call to Action */}
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            Public Agency AI Model Arbitration Control Center
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Real-time automated evaluation, weighted voting arbitration, and governance audit trail across 5 AI models.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate("create")}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-sm font-semibold rounded-lg shadow-lg shadow-cyan-900/40 flex items-center gap-2 cursor-pointer transition-all"
          >
            <span>Run New Arbitration</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onNavigate("scenarios")}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm font-medium rounded-lg border border-gray-700 cursor-pointer"
          >
            Demo Scenarios
          </button>
        </div>
      </div>

      {/* KPI Grid (8 metrics) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className={`p-4 rounded-xl border ${kpi.bg} transition-all hover:scale-[1.02]`}>
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-gray-400 tracking-wider">{kpi.label}</span>
                <Icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
              <div className={`text-2xl font-black mt-2 ${kpi.color}`}>{kpi.value}</div>
            </div>
          );
        })}
      </div>

      {/* Analytical Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Chart 1: Decisions by Status */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center justify-between">
            <span>1. Decisions by Status</span>
            <span className="text-xs text-gray-500 font-normal">Distribution</span>
          </h3>
          <div className="space-y-3">
            {[
              { label: "Approved", count: analytics.approved_count, total: analytics.total_decisions, color: "bg-emerald-500" },
              { label: "Rejected", count: analytics.rejected_count, total: analytics.total_decisions, color: "bg-rose-500" },
              { label: "Pending Review", count: analytics.pending_review_count, total: analytics.total_decisions, color: "bg-amber-500" },
            ].map((item, i) => {
              const pct = analytics.total_decisions ? round((item.count / analytics.total_decisions) * 100, 1) : 0;
              return (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-xs text-gray-300">
                    <span>{item.label}</span>
                    <span className="font-semibold">{item.count} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                    <div className={`h-full ${item.color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Chart 2: Model Accuracy Comparison */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center justify-between">
            <span>2. Model Accuracy Scores</span>
            <span className="text-xs text-gray-500 font-normal">Historical Benchmark</span>
          </h3>
          <div className="space-y-2.5">
            {analytics.model_stats.map((m, i) => (
              <div key={i} className="space-y-1 text-xs">
                <div className="flex justify-between text-gray-300">
                  <span className="font-medium">{m.model_name} ({m.vendor_name})</span>
                  <span className="text-cyan-400 font-semibold">{m.accuracy}%</span>
                </div>
                <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full" style={{ width: `${m.accuracy}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 3: Model Reliability Index */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center justify-between">
            <span>3. Model Reliability Scores</span>
            <span className="text-xs text-gray-500 font-normal">Vendor Governance</span>
          </h3>
          <div className="space-y-2.5">
            {analytics.model_stats.map((m, i) => (
              <div key={i} className="space-y-1 text-xs">
                <div className="flex justify-between text-gray-300">
                  <span className="font-medium">{m.model_name}</span>
                  <span className="text-emerald-400 font-semibold">{m.reliability}%</span>
                </div>
                <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full" style={{ width: `${m.reliability}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 4: Confidence Distribution */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center justify-between">
            <span>4. Confidence Distribution</span>
            <span className="text-xs text-gray-500 font-normal">Histogram</span>
          </h3>
          <div className="grid grid-cols-4 gap-2 text-center pt-2">
            {analytics.confidence_distribution.map((item, i) => (
              <div key={i} className="bg-gray-900/60 p-3 rounded-lg border border-gray-800">
                <div className="text-xs text-gray-400 font-medium">{item.range}</div>
                <div className="text-lg font-bold text-cyan-400 mt-1">{item.count}</div>
                <div className="text-[10px] text-gray-500 mt-0.5">cases</div>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 5: Model Response Times (Latency) */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center justify-between">
            <span>5. Latency Comparison (ms)</span>
            <span className="text-xs text-gray-500 font-normal">Processing Time</span>
          </h3>
          <div className="space-y-2.5">
            {analytics.model_stats.map((m, i) => (
              <div key={i} className="space-y-1 text-xs">
                <div className="flex justify-between text-gray-300">
                  <span>{m.model_name}</span>
                  <span className="text-amber-400 font-mono font-semibold">{m.latency} ms</span>
                </div>
                <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                    style={{ width: `${Math.min((m.latency / 1000) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 6: Human Review & Oversight Rate */}
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center justify-between">
            <span>6. Arbitration Governance Rate</span>
            <span className="text-xs text-gray-500 font-normal">Human-in-the-loop</span>
          </h3>
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Automated Resolution Rate:</span>
              <span className="text-emerald-400 font-bold">{round(100 - analytics.human_review_rate, 1)}%</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Human Escalation Rate:</span>
              <span className="text-rose-400 font-bold">{analytics.human_review_rate}%</span>
            </div>
            <div className="h-3 w-full bg-gray-800 rounded-full overflow-hidden flex">
              <div className="bg-emerald-500 h-full" style={{ width: `${100 - analytics.human_review_rate}%` }}></div>
              <div className="bg-rose-500 h-full" style={{ width: `${analytics.human_review_rate}%` }}></div>
            </div>
            <p className="text-[11px] text-gray-400">
              High risk or split model decisions are automatically routed to the Human Review Queue for final sign-off.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function round(val, dec) {
  return Number(Math.round(val + "e" + dec) + "e-" + dec);
}
