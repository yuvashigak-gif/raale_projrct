import React, { useState, useEffect } from "react";
import { ShieldCheck, CheckCircle2, XCircle, AlertCircle, X, Terminal } from "lucide-react";
import { api } from "../api";

export default function DecisionDetailModal({ requestId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!requestId) return;
    setLoading(true);
    api.getDecisionDetail(requestId)
      .then(res => setDetail(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [requestId]);

  if (!requestId) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="glass-panel max-w-3xl w-full p-6 rounded-2xl space-y-6 border border-cyan-500/30 my-8">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div>
            <h3 className="text-lg font-bold text-gray-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              Decision Inspection: <span className="font-mono text-cyan-300">{requestId}</span>
            </h3>
            <p className="text-xs text-gray-400">Complete multi-model consensus and audit inspection</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg bg-gray-800 text-gray-400 hover:text-white cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading decision inspection...</div>
        ) : !detail ? (
          <div className="p-8 text-center text-gray-400">Decision request not found.</div>
        ) : (
          <div className="space-y-6 text-xs text-gray-300">
            {/* Request Summary */}
            <div className="bg-gray-900/60 p-4 rounded-xl border border-gray-800 grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>Type: <b className="text-gray-100 block mt-0.5">{detail.request.request_type}</b></div>
              <div>Applicant: <b className="text-gray-300 block mt-0.5">{detail.request.applicant_id}</b></div>
              <div>Priority: <b className="text-cyan-400 block mt-0.5">{detail.request.priority}</b></div>
              <div>Risk Level: <b className="text-amber-400 block mt-0.5">{detail.request.risk_level}</b></div>
              <div className="col-span-full pt-2 border-t border-gray-800/60">
                <b>Description:</b> {detail.request.description}
              </div>
            </div>

            {/* Model Responses Table */}
            <div className="space-y-2">
              <h4 className="font-bold text-cyan-400 uppercase tracking-wider">Collected AI Model Responses</h4>
              <div className="space-y-2">
                {detail.responses.map((resp, i) => (
                  <div key={i} className="p-3 bg-gray-900/80 rounded-xl border border-gray-800 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-gray-100">{resp.model_name} ({resp.vendor_name})</span>
                      <div className="flex items-center space-x-3">
                        <span className="text-emerald-400 font-mono font-bold">${(resp.cost_per_request || 0.010).toFixed(3)}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          resp.decision === "APPROVE" ? "badge-approve" : resp.decision === "REJECT" ? "badge-reject" : "badge-review"
                        }`}>
                          {resp.decision} ({resp.confidence}%)
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-400 text-[11px]">"{resp.reasoning_summary}"</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Final Decision Callout */}
            {detail.final_decision && (
              <div className="p-5 rounded-2xl bg-cyan-950/30 border border-cyan-500/40 space-y-3">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-[10px] font-bold text-gray-400 uppercase">Final Decision Outcome</span>
                    <div className="text-xl font-black text-emerald-400 mt-0.5">{detail.final_decision.final_decision}</div>
                  </div>
                  <div className="text-right text-xs space-y-1">
                    <div>Highest Score Winner: <b className="text-cyan-300">{detail.final_decision.weighted_score_winner || detail.final_decision.winning_model || "None"}</b></div>
                    <div>Policy Selected Winner: <b className="text-purple-300">{detail.final_decision.policy_selected_winner || detail.final_decision.winning_model || "None"}</b></div>
                    <div>Total Cost: <b className="text-emerald-400">${(detail.final_decision.total_cost || 0.043).toFixed(4)}</b></div>
                  </div>
                </div>

                {detail.final_decision.policy_override && (
                  <div className="p-3 bg-purple-950/60 border border-purple-800/80 rounded-lg text-purple-200 space-y-1">
                    <div className="font-bold text-xs">POLICY OVERRIDE APPLIED</div>
                    <p className="text-[11px] text-purple-300/90">{detail.final_decision.override_reason}</p>
                  </div>
                )}

                <div className="pt-2 border-t border-gray-800 text-gray-300">
                  <b>Audit Rationale:</b> {detail.final_decision.explanation}
                </div>
              </div>
            )}

            {/* Audit Log Reference */}
            {detail.audit && (
              <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 space-y-1">
                <div className="flex justify-between items-center text-gray-400 font-mono text-[11px]">
                  <span>Audit ID: <b className="text-cyan-300">{detail.audit.audit_id}</b></span>
                  <span>Policy: {detail.audit.policy_used}</span>
                  <span>Selection: {detail.audit.selection_method || "Weighted Scoring"}</span>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="pt-2 text-right border-t border-gray-800">
          <button onClick={onClose} className="px-4 py-2 bg-gray-800 text-gray-300 text-xs rounded-lg hover:bg-gray-700 cursor-pointer">
            Close Inspection
          </button>
        </div>
      </div>
    </div>
  );
}
