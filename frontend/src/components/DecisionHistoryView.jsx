import React, { useState, useEffect } from "react";
import { Search, Filter, Eye, CheckCircle2, XCircle, AlertCircle, ShieldCheck } from "lucide-react";
import { api } from "../api";

export default function DecisionHistoryView({ onSelectDecision }) {
  const [decisions, setDecisions] = useState([]);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [decisionFilter, setDecisionFilter] = useState("");
  const [loading, setLoading] = useState(true);

  const loadDecisions = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (riskFilter) params.risk = riskFilter;
      if (decisionFilter) params.decision = decisionFilter;

      const data = await api.getDecisions(params);
      setDecisions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDecisions();
  }, [search, riskFilter, decisionFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-cyan-400" />
            Decision Request History & Audit Records
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Complete historical log of public agency decision requests processed by the AI arbitration engine.
          </p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by Request ID, Applicant, or Type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg pl-9 pr-4 py-2.5 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        {/* Risk Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2 focus:border-cyan-500 focus:outline-none"
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">LOW Risk</option>
            <option value="MEDIUM">MEDIUM Risk</option>
            <option value="HIGH">HIGH Risk</option>
            <option value="CRITICAL">CRITICAL Risk</option>
          </select>
        </div>

        {/* Decision Filter */}
        <div>
          <select
            value={decisionFilter}
            onChange={(e) => setDecisionFilter(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2 focus:border-cyan-500 focus:outline-none"
          >
            <option value="">All Decisions</option>
            <option value="APPROVE">APPROVE</option>
            <option value="REJECT">REJECT</option>
            <option value="PENDING HUMAN REVIEW">PENDING HUMAN REVIEW</option>
          </select>
        </div>
      </div>

      {/* Decisions Table */}
      <div className="glass-panel rounded-xl overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-900/90 text-gray-400 font-bold uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="p-3.5">Request ID</th>
                <th className="p-3.5">Request Type</th>
                <th className="p-3.5">Applicant</th>
                <th className="p-3.5">Risk Tier</th>
                <th className="p-3.5">Final Decision</th>
                <th className="p-3.5">Selected Winner</th>
                <th className="p-3.5">Total Cost</th>
                <th className="p-3.5">Policy Override</th>
                <th className="p-3.5">Submitted</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {loading ? (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-gray-400">Loading history records...</td>
                </tr>
              ) : decisions.length === 0 ? (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-gray-500">No decision records found matching filters.</td>
                </tr>
              ) : (
                decisions.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="p-3.5 font-mono font-bold text-cyan-400">{item.request_id}</td>
                    <td className="p-3.5 font-medium text-gray-200">{item.request_type}</td>
                    <td className="p-3.5 text-gray-400">{item.applicant_id}</td>
                    <td className="p-3.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold risk-${item.risk_level.toLowerCase()}`}>
                        {item.risk_level}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <DecisionStatusBadge decision={item.final_decision} />
                    </td>
                    <td className="p-3.5 text-gray-300 font-medium">{item.policy_selected_winner || item.winning_model || "N/A (Review)"}</td>
                    <td className="p-3.5 font-mono text-emerald-400 font-bold">${(item.total_cost || 0.043).toFixed(4)}</td>
                    <td className="p-3.5">
                      {item.policy_override ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-950 text-purple-300 border border-purple-800">
                          YES (OVERRIDE)
                        </span>
                      ) : (
                        <span className="text-gray-500 text-[10px]">No</span>
                      )}
                    </td>
                    <td className="p-3.5 text-gray-500 text-[11px]">
                      {new Date(item.submitted_date).toLocaleDateString()}
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => onSelectDecision(item.request_id)}
                        className="px-3 py-1 bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 rounded-lg text-[11px] font-medium inline-flex items-center gap-1 cursor-pointer transition-all"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DecisionStatusBadge({ decision }) {
  if (decision === "APPROVE") {
    return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold badge-approve inline-flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> APPROVE</span>;
  }
  if (decision === "REJECT") {
    return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold badge-reject inline-flex items-center gap-1"><XCircle className="w-3 h-3" /> REJECT</span>;
  }
  return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold badge-pending inline-flex items-center gap-1"><AlertCircle className="w-3 h-3" /> PENDING REVIEW</span>;
}
