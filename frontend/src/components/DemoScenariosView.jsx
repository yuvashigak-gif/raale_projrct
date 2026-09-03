import React, { useState, useEffect, useRef } from "react";
import { PlayCircle, Sparkles, CheckCircle2, XCircle, AlertCircle, AlertTriangle, ShieldCheck, Loader2, Cpu } from "lucide-react";
import { api } from "../api";

export default function DemoScenariosView({ onScenarioExecuted }) {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningKey, setRunningKey] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const resultRef = useRef(null);

  const loadScenarios = async () => {
    setLoading(true);
    try {
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to fetch scenarios from backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  const handleRunScenario = async (key) => {
    setRunningKey(key);
    setResult(null);
    setErrorMsg(null);

    try {
      const res = await api.runScenario(key);
      setResult(res);
      if (onScenarioExecuted) onScenarioExecuted();

      // Smooth scroll to result
      setTimeout(() => {
        if (resultRef.current) {
          resultRef.current.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);

    } catch (err) {
      setErrorMsg(err.message || "Failed to execute scenario");
    } finally {
      setRunningKey(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <PlayCircle className="w-6 h-6 text-cyan-400" />
            Preset Demo Scenarios Launcher (8 Scenarios)
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Execute pre-configured multi-vendor AI evaluation scenarios to demonstrate edge-case consensus resolution.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-950/80 border border-rose-800 rounded-xl text-rose-200 text-xs flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Scenario Buttons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          <div className="col-span-full p-8 text-center text-gray-400 glass-panel rounded-2xl">Loading Scenarios...</div>
        ) : (
          scenarios.map((sc, i) => (
            <div key={sc.key} className="glass-panel p-5 rounded-2xl space-y-3 border border-gray-800 hover:border-cyan-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start gap-2">
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                    Scenario #{i+1}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded risk-${sc.risk_level.toLowerCase()}`}>
                    {sc.risk_level}
                  </span>
                </div>
                <h3 className="font-bold text-gray-100 text-xs mt-2.5">{sc.name}</h3>
                <p className="text-[11px] text-gray-400 mt-1 line-clamp-3 leading-relaxed">{sc.description}</p>
              </div>

              <button
                onClick={() => handleRunScenario(sc.key)}
                disabled={runningKey === sc.key}
                className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md flex items-center justify-center space-x-1.5 cursor-pointer transition-all mt-2"
              >
                {runningKey === sc.key ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-white" />
                    <span>Running Arbitration...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-cyan-200" />
                    <span>Run Demo Scenario</span>
                  </>
                )}
              </button>
            </div>
          ))
        )}
      </div>

      {/* Scenario Execution Result Display */}
      {result && (
        <div ref={resultRef} className="glass-panel p-6 rounded-2xl space-y-6 border border-cyan-500/50 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <h3 className="text-base font-bold text-cyan-300 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              Scenario Execution Output: {result.scenario}
            </h3>
            <span className="font-mono text-xs text-gray-400">Request ID: <b className="text-cyan-400 font-bold">{result.request_id}</b></span>
          </div>

          {/* Model Responses Breakdown */}
          {result.arbitration_result.scores_breakdown && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider">Participating AI Model Responses</h4>
              <div className="space-y-2">
                {result.arbitration_result.scores_breakdown.map((item, idx) => (
                  <div key={idx} className="p-3 bg-gray-900/80 rounded-xl border border-gray-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div className="flex items-center space-x-3">
                      <Cpu className="w-4 h-4 text-cyan-400" />
                      <span className="font-bold text-gray-100">{item.model_name}</span>
                      <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                        item.decision === "APPROVE" ? "badge-approve" : item.decision === "REJECT" ? "badge-reject" : "badge-review"
                      }`}>
                        {item.decision}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-gray-400">
                      <span>Model Confidence: <b className="text-cyan-300">{item.confidence}%</b></span>
                      <span>Score: <b className="text-purple-300">{item.normalized_score} / 100</b></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Final Result Banner */}
          <div className={`p-5 rounded-2xl border ${
            result.arbitration_result.human_review_required
              ? "bg-amber-950/40 border-amber-500/50 text-amber-200"
              : result.arbitration_result.final_decision === "APPROVE"
              ? "bg-emerald-950/40 border-emerald-500/50 text-emerald-200"
              : "bg-rose-950/40 border-rose-500/50 text-rose-200"
          }`}>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Arbitration Result</span>
                <div className="text-2xl font-black mt-1 flex items-center gap-3">
                  <span>{result.arbitration_result.final_decision}</span>
                  {result.arbitration_result.human_review_required && (
                    <span className="text-xs font-bold px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" /> PENDING HUMAN REVIEW
                    </span>
                  )}
                </div>
              </div>

              <div className="text-right text-xs space-y-1">
                <div>Winning Model: <b className="text-cyan-300">{result.arbitration_result.winning_model || "None (Review)"}</b></div>
                <div>Arbitration Score: <b className="text-cyan-400">{result.arbitration_result.arbitration_score} / 100</b></div>
                <div>Agreement Level: <b className="text-gray-200">{result.arbitration_result.agreement_level}</b></div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-white/10 text-xs leading-relaxed opacity-95">
              <b>Engine Explanation:</b> {result.arbitration_result.explanation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
