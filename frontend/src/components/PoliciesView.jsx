import React, { useState, useEffect } from "react";
import { Scale, CheckCircle2, ShieldCheck, Zap } from "lucide-react";
import { api } from "../api";

export default function PoliciesView({ onPolicyChange }) {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadPolicies = async () => {
    setLoading(true);
    try {
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolicies();
  }, []);

  const handleActivate = async (policyId) => {
    try {
      await api.activatePolicy(policyId);
      await loadPolicies();
      if (onPolicyChange) onPolicyChange();
    } catch (err) {
      alert("Failed to activate policy: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <Scale className="w-6 h-6 text-cyan-400" />
            Configurable Arbitration Policies Engine (10 Policies)
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Configure active policy rules and formula weights governing automated multi-model arbitration.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {loading ? (
          <div className="col-span-full p-8 text-center text-gray-400">Loading Policies...</div>
        ) : (
          policies.map((p) => (
            <div
              key={p.id}
              className={`glass-panel p-6 rounded-2xl space-y-4 border transition-all ${
                p.is_active
                  ? "border-cyan-500 bg-cyan-950/20 shadow-lg shadow-cyan-950/50"
                  : "border-gray-800 hover:border-gray-700"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-gray-100 text-sm flex items-center gap-2">
                    <span>{p.policy_name}</span>
                    <span className="font-mono text-[10px] text-cyan-400">({p.policy_id})</span>
                  </h3>
                  <p className="text-xs text-gray-400 mt-1 leading-relaxed">{p.description}</p>
                </div>
                {p.is_active && (
                  <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-[10px] font-bold shrink-0 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                    ACTIVE
                  </span>
                )}
              </div>

              {/* Formula Weights Grid */}
              <div className="grid grid-cols-4 gap-2 text-center bg-gray-900/60 p-3 rounded-xl border border-gray-800 text-xs">
                <div>
                  <span className="text-[10px] text-gray-500 block">Reliability</span>
                  <span className="font-bold text-cyan-400">{(p.weight_reliability * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 block">Confidence</span>
                  <span className="font-bold text-purple-400">{(p.weight_confidence * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 block">Accuracy</span>
                  <span className="font-bold text-emerald-400">{(p.weight_accuracy * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 block">Consensus</span>
                  <span className="font-bold text-amber-400">{(p.weight_consensus * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-1 border-t border-gray-800/80">
                <span className="text-gray-400">
                  Min Threshold: <b className="text-gray-200">{(p.min_confidence_threshold * 100).toFixed(0)}%</b>
                </span>
                {!p.is_active && (
                  <button
                    onClick={() => handleActivate(p.policy_id)}
                    className="px-4 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-lg text-xs cursor-pointer transition-all shadow"
                  >
                    Activate Policy
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
