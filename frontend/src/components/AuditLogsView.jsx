import React, { useState, useEffect } from "react";
import { FileText, Search, ShieldCheck, Eye, Terminal } from "lucide-react";
import { api } from "../api";

export default function AuditLogsView() {
  const [logs, setLogs] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedAudit, setSelectedAudit] = useState(null);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs({ search });
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <FileText className="w-6 h-6 text-cyan-400" />
            Immutable Audit Log & Governance Trail
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Complete audit trail capturing model outputs, policy formulas, winning decisions, and human override actions.
          </p>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl">
        <div className="relative">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search audit records by Audit ID, Request ID, Policy, or Reason..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg pl-9 pr-4 py-2.5 focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-900/90 text-gray-400 font-bold uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="p-3.5">Audit ID</th>
                <th className="p-3.5">Request ID</th>
                <th className="p-3.5">Models Used</th>
                <th className="p-3.5">Policy Applied</th>
                <th className="p-3.5">Final Decision</th>
                <th className="p-3.5">Winning Model</th>
                <th className="p-3.5">Reviewer</th>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {loading ? (
                <tr><td colSpan={9} className="p-8 text-center text-gray-400">Loading audit records...</td></tr>
              ) : logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-800/40">
                  <td className="p-3.5 font-mono font-bold text-cyan-400">{log.audit_id}</td>
                  <td className="p-3.5 font-mono text-gray-300">{log.request_id}</td>
                  <td className="p-3.5 text-gray-400 font-mono text-[11px]">{log.models_used}</td>
                  <td className="p-3.5 font-medium text-gray-200">{log.policy_used}</td>
                  <td className="p-3.5 font-bold">{log.final_decision}</td>
                  <td className="p-3.5 text-gray-300">{log.winning_model || "Human Review"}</td>
                  <td className="p-3.5 text-gray-400">{log.reviewer || "System Engine"}</td>
                  <td className="p-3.5 text-gray-500 text-[11px]">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => setSelectedAudit(log)}
                      className="px-3 py-1 bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 rounded text-[11px] font-semibold cursor-pointer"
                    >
                      View Record
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Detail Modal */}
      {selectedAudit && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel max-w-2xl w-full p-6 rounded-2xl space-y-4 border border-cyan-500/30">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
                <Terminal className="w-5 h-5 text-cyan-400" />
                Audit Record Details: <span className="font-mono text-cyan-300">{selectedAudit.audit_id}</span>
              </h3>
              <button onClick={() => setSelectedAudit(null)} className="text-gray-400 hover:text-white font-bold text-sm">✕</button>
            </div>

            <div className="space-y-3 text-xs text-gray-300">
              <div><b>Request ID:</b> <span className="font-mono text-cyan-300">{selectedAudit.request_id}</span></div>
              <div><b>Policy Used:</b> {selectedAudit.policy_used}</div>
              <div><b>Final Decision:</b> <b className="text-emerald-400">{selectedAudit.final_decision}</b></div>
              <div><b>Winning Model:</b> {selectedAudit.winning_model || "None"}</div>
              <div><b>Explanation:</b> "{selectedAudit.reason}"</div>

              <div>
                <b className="block mb-1 text-gray-400">Raw Model Outputs JSON:</b>
                <pre className="bg-gray-950 p-3 rounded-xl border border-gray-800 text-[11px] font-mono text-cyan-300 overflow-x-auto">
                  {JSON.stringify(JSON.parse(selectedAudit.model_outputs || "[]"), null, 2)}
                </pre>
              </div>

              {selectedAudit.scores && (
                <div>
                  <b className="block mb-1 text-gray-400">Arbitration Scores Breakdown JSON:</b>
                  <pre className="bg-gray-950 p-3 rounded-xl border border-gray-800 text-[11px] font-mono text-purple-300 overflow-x-auto">
                    {JSON.stringify(JSON.parse(selectedAudit.scores || "[]"), null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="pt-2 text-right">
              <button onClick={() => setSelectedAudit(null)} className="px-4 py-2 bg-gray-800 text-gray-300 text-xs rounded-lg hover:bg-gray-700">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
