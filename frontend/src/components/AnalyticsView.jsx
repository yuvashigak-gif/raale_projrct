import React from "react";
import { BarChart3, TrendingUp, Cpu, Award, Zap } from "lucide-react";

export default function AnalyticsView({ analytics }) {
  if (!analytics) return <div className="p-8 text-center text-gray-400">Loading Analytics...</div>;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-cyan-400" />
            AI Model Performance & System Analytics
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Comparative performance metrics, model accuracy scatter benchmarks, latency profiles, and decision agreement ratios.
          </p>
        </div>
      </div>

      {/* Model Stats Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400" />
          Model Performance Benchmarks & Reliability Metrics
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-900/90 text-gray-400 font-bold uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="p-3">Model Name</th>
                <th className="p-3">Vendor</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Reliability Score</th>
                <th className="p-3">Average Confidence</th>
                <th className="p-3">Average Latency</th>
                <th className="p-3">Total Evaluated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {analytics.model_stats.map((m, i) => (
                <tr key={i} className="hover:bg-gray-800/40">
                  <td className="p-3 font-bold text-gray-100">{m.model_name}</td>
                  <td className="p-3 text-cyan-400">{m.vendor_name}</td>
                  <td className="p-3 font-bold text-emerald-400">{m.accuracy}%</td>
                  <td className="p-3 font-bold text-purple-400">{m.reliability}%</td>
                  <td className="p-3 font-semibold text-gray-200">{m.confidence}%</td>
                  <td className="p-3 font-mono text-amber-400">{m.latency} ms</td>
                  <td className="p-3 font-bold text-gray-300">{m.total_decisions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
