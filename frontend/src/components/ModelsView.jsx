import React, { useState, useEffect } from "react";
import { Cpu, Plus, Edit2, CheckCircle, XCircle } from "lucide-react";
import { api } from "../api";

export default function ModelsView() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await api.getModels();
      setModels(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  const toggleStatus = async (model) => {
    const newStatus = model.status === "Active" ? "Disabled" : "Active";
    try {
      await api.updateModel(model.model_id, { status: newStatus });
      await loadModels();
    } catch (err) {
      alert("Failed to update status: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-cyan-400" />
            AI Models Registry & Performance Metrics
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Manage registered AI models from external vendors. Configure status, accuracy, and reliability benchmarks.
          </p>
        </div>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-900/90 text-gray-400 font-bold uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="p-3.5">Model ID</th>
                <th className="p-3.5">Model Name</th>
                <th className="p-3.5">Vendor</th>
                <th className="p-3.5">Version</th>
                <th className="p-3.5">Accuracy</th>
                <th className="p-3.5">Reliability</th>
                <th className="p-3.5">Confidence</th>
                <th className="p-3.5">Cost / Req</th>
                <th className="p-3.5">Avg Latency</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {loading ? (
                <tr><td colSpan={11} className="p-8 text-center text-gray-400">Loading AI models...</td></tr>
              ) : models.map((m) => (
                <tr key={m.id} className="hover:bg-gray-800/40">
                  <td className="p-3.5 font-mono font-bold text-cyan-400">{m.model_id}</td>
                  <td className="p-3.5 font-semibold text-gray-100">{m.model_name}</td>
                  <td className="p-3.5 text-gray-300">{m.vendor_id}</td>
                  <td className="p-3.5 text-gray-400 font-mono">{m.version}</td>
                  <td className="p-3.5 font-bold text-emerald-400">{(m.accuracy_score * 100).toFixed(0)}%</td>
                  <td className="p-3.5 font-bold text-cyan-400">{(m.reliability_score * 100).toFixed(0)}%</td>
                  <td className="p-3.5 text-purple-300">{(m.confidence_score * 100).toFixed(0)}%</td>
                  <td className="p-3.5 font-mono text-emerald-300 font-bold">${(m.cost_per_request || 0.01).toFixed(3)}</td>
                  <td className="p-3.5 font-mono text-amber-400">{m.latency_ms} ms</td>
                  <td className="p-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      m.status === "Active" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-gray-800 text-gray-500"
                    }`}>
                      {m.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => toggleStatus(m)}
                      className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                        m.status === "Active"
                          ? "bg-rose-950/60 border border-rose-800 text-rose-300 hover:bg-rose-900"
                          : "bg-emerald-950/60 border border-emerald-800 text-emerald-300 hover:bg-emerald-900"
                      }`}
                    >
                      {m.status === "Active" ? "Disable" : "Enable"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
