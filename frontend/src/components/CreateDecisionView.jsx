import React, { useState } from "react";
import { PlayCircle, ShieldCheck, CheckCircle2, XCircle, AlertCircle, Cpu, Loader2, Sparkles, AlertTriangle } from "lucide-react";
import { api } from "../api";

export default function CreateDecisionView({ activePolicy, onArbitrationDone }) {
  const [requestType, setRequestType] = useState("Permit Approval");
  const [applicantId, setApplicantId] = useState("APP-2045");
  const [description, setDescription] = useState("Construction permit application for municipal solar facility.");
  const [priority, setPriority] = useState("Medium");
  const [riskLevel, setRiskLevel] = useState("MEDIUM");
  const [selectedModels, setSelectedModels] = useState(["M001", "M002", "M003"]);

  const [isProcessing, setIsProcessing] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const requestTypes = [
    "Permit Approval",
    "Benefits Eligibility",
    "License Renewal",
    "Environmental Approval",
    "Infrastructure Funding",
    "Zoning Exception",
    "Hazardous Materials Permit",
    "Public Contracting Eligibility"
  ];

  const modelOptions = [
    { id: "M001", name: "GPT-5.6 (OpenAI)" },
    { id: "M002", name: "Claude Sonnet (Anthropic)" },
    { id: "M003", name: "Gemini (Google)" },
    { id: "M004", name: "Azure AI Model (Microsoft)" },
    { id: "M005", name: "Command R+ (Cohere)" },
  ];

  const handleModelToggle = (id) => {
    if (selectedModels.includes(id)) {
      if (selectedModels.length > 2) {
        setSelectedModels(selectedModels.filter(m => m !== id));
      }
    } else {
      setSelectedModels([...selectedModels, id]);
    }
  };

  const handleRunArbitration = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setErrorMsg(null);
    setResult(null);
    setStepIndex(1);

    try {
      // Step animation sequence
      setTimeout(() => setStepIndex(2), 600);
      setTimeout(() => setStepIndex(3), 1200);

      const res = await api.createDecision({
        request_type: requestType,
        applicant_id: applicantId,
        description: description,
        priority: priority,
        risk_level: riskLevel,
        selected_models: selectedModels
      });

      setTimeout(() => {
        setStepIndex(4);
        setResult(res);
        setIsProcessing(false);
        if (onArbitrationDone) onArbitrationDone();
      }, 1800);

    } catch (err) {
      setIsProcessing(false);
      setErrorMsg(err.message || "Failed to execute arbitration");
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-cyan-500">
        <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
          <PlayCircle className="w-6 h-6 text-cyan-400" />
          Create Decision Request & Run Arbitration
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Submit a public agency decision request. The system will query selected AI models, evaluate responses under the active arbitration policy, and generate a final decision with full audit trail.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Panel */}
        <form onSubmit={handleRunArbitration} className="glass-panel p-6 rounded-2xl space-y-4 lg:col-span-1">
          <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-wider">Decision Parameters</h3>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Request Type</label>
            <select
              value={requestType}
              onChange={(e) => setRequestType(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2.5 focus:border-cyan-500 focus:outline-none"
            >
              {requestTypes.map((t, idx) => (
                <option key={idx} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Applicant ID</label>
            <input
              type="text"
              value={applicantId}
              onChange={(e) => setApplicantId(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2.5 focus:border-cyan-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Description / Summary</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2.5 focus:border-cyan-500 focus:outline-none"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2 focus:border-cyan-500 focus:outline-none"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">Risk Level</label>
              <select
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2 focus:border-cyan-500 focus:outline-none font-bold"
              >
                <option value="LOW" className="text-emerald-400">LOW</option>
                <option value="MEDIUM" className="text-blue-400">MEDIUM</option>
                <option value="HIGH" className="text-amber-400">HIGH</option>
                <option value="CRITICAL" className="text-rose-400">CRITICAL</option>
              </select>
            </div>
          </div>

          {/* Model Selector */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Participating Models (Min 2)</label>
            <div className="space-y-1.5 pt-1">
              {modelOptions.map((m) => (
                <label key={m.id} className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer bg-gray-900/60 p-2 rounded-lg border border-gray-800 hover:border-gray-700">
                  <input
                    type="checkbox"
                    checked={selectedModels.includes(m.id)}
                    onChange={() => handleModelToggle(m.id)}
                    className="accent-cyan-500 rounded"
                  />
                  <span>{m.name}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-lg shadow-cyan-900/40 flex items-center justify-center space-x-2 cursor-pointer transition-all mt-4"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Running Arbitration Engine...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Run Arbitration</span>
              </>
            )}
          </button>
        </form>

        {/* Results & Animation Area */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-2 space-y-6">
          {/* Active Policy Header Box */}
          <div className="bg-gray-900/80 p-4 rounded-xl border border-gray-800 flex items-center justify-between">
            <div className="text-xs text-gray-400">Active Policy Engine:</div>
            <div className="text-xs font-bold text-cyan-300 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>{activePolicy?.policy_name || "Weighted Reliability + Confidence"}</span>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-4 bg-rose-950/60 border border-rose-800/80 text-rose-200 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Processing Animation */}
          {isProcessing && (
            <div className="py-12 space-y-6 text-center">
              <div className="inline-flex p-4 rounded-full bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 animate-bounce">
                <Cpu className="w-8 h-8" />
              </div>
              <div className="space-y-2 max-w-sm mx-auto">
                <div className="text-sm font-semibold text-gray-200">
                  {stepIndex === 1 && "1. Requesting outputs from AI models..."}
                  {stepIndex === 2 && "2. Normalizing model confidence & reliability scores..."}
                  {stepIndex === 3 && "3. Applying arbitration policy algorithm & risk checks..."}
                  {stepIndex === 4 && "4. Decision finalized!"}
                </div>
                <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 transition-all duration-500"
                    style={{ width: `${(stepIndex / 4) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          {/* Initial State Prompt */}
          {!isProcessing && !result && !errorMsg && (
            <div className="py-16 text-center space-y-3">
              <Sparkles className="w-12 h-12 text-gray-600 mx-auto" />
              <h4 className="text-sm font-medium text-gray-400">Ready to execute AI Arbitration</h4>
              <p className="text-xs text-gray-500 max-w-md mx-auto">
                Fill out the decision parameters on the left and click "Run Arbitration" to simulate multi-model consensus evaluation.
              </p>
            </div>
          )}

          {/* Arbitration Result View */}
          {!isProcessing && result && (
            <div className="space-y-6 animate-fadeIn">
              {/* 1. Model Responses Table */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider">1. Model Responses Collected</h4>
                <div className="space-y-2">
                  {result.model_responses.map((resp, i) => (
                    <div key={i} className="p-3 bg-gray-900/60 rounded-xl border border-gray-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                      <div className="flex items-center space-x-3">
                        <span className="font-bold text-gray-200">{resp.model_name}</span>
                        <DecisionBadge decision={resp.decision} />
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="text-gray-400">Confidence: <b className="text-cyan-400">{resp.confidence}%</b></span>
                        <span className="text-gray-500 font-mono">{resp.processing_time} ms</span>
                      </div>
                      <p className="w-full text-gray-400 text-[11px] bg-gray-950/40 p-2 rounded border border-gray-800/60 mt-1">
                        "{resp.reasoning_summary}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 2. Arbitration Analysis */}
              <div className="p-4 bg-gray-900/80 rounded-xl border border-gray-800 space-y-3 text-xs">
                <h4 className="font-bold text-cyan-400 uppercase tracking-wider">2. Arbitration Analysis Breakdown</h4>
                
                {/* Winner Breakdown Box */}
                <div className="p-3 bg-gray-950/60 rounded-lg border border-gray-800 grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wider font-semibold">Weighted Score Winner (Highest Raw Score)</span>
                    <div className="font-bold text-cyan-300 text-sm">{result.arbitration_result.weighted_score_winner || result.arbitration_result.winning_model || "None"}</div>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wider font-semibold">Policy Selected Winner (Governance Outcome)</span>
                    <div className="font-bold text-purple-300 text-sm">{result.arbitration_result.policy_selected_winner || result.arbitration_result.winning_model || "None"}</div>
                  </div>
                </div>

                {/* Policy Override Banner if applicable */}
                {result.arbitration_result.policy_override && (
                  <div className="p-3 bg-purple-950/60 border border-purple-800/80 rounded-lg text-purple-200 space-y-1">
                    <div className="font-bold flex items-center gap-1.5 text-xs">
                      <ShieldCheck className="w-4 h-4 text-purple-400" />
                      <span>POLICY OVERRIDE DETECTED</span>
                    </div>
                    <p className="text-[11px] text-purple-300/90 leading-relaxed">
                      {result.arbitration_result.override_reason}
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-gray-300">
                  <div>Agreement: <b className="text-gray-100">{result.arbitration_result.agreement_level}</b></div>
                  <div>Arbitration Score: <b className="text-cyan-400">{result.arbitration_result.arbitration_score} / 100</b></div>
                  <div>Total Cost: <b className="text-emerald-400">${(result.arbitration_result.total_cost || 0.043).toFixed(4)}</b></div>
                  <div>Selection: <b className="text-purple-300">{result.arbitration_result.selection_method || "Weighted Scoring"}</b></div>
                </div>
              </div>

              {/* 3. FINAL DECISION BANNER */}
              <div className={`p-6 rounded-2xl border ${
                result.arbitration_result.human_review_required
                  ? "bg-amber-950/40 border-amber-500/50 text-amber-200"
                  : result.arbitration_result.final_decision === "APPROVE"
                  ? "bg-emerald-950/40 border-emerald-500/50 text-emerald-200"
                  : "bg-rose-950/40 border-rose-500/50 text-rose-200"
              }`}>
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-widest text-gray-400">Final Decision Outcome</div>
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
                    {result.arbitration_result.policy_selected_winner && (
                      <div>Final Winner: <b className="text-cyan-300">{result.arbitration_result.policy_selected_winner}</b></div>
                    )}
                    <div>Overall Confidence: <b className="text-gray-100">{result.arbitration_result.confidence}%</b></div>
                    <div>Request ID: <b className="font-mono text-gray-300">{result.request_id}</b></div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/10 text-xs leading-relaxed opacity-90">
                  <b>Audit Rationale:</b> {result.arbitration_result.explanation}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DecisionBadge({ decision }) {
  if (decision === "APPROVE") {
    return <span className="px-2.5 py-0.5 rounded text-[11px] font-bold badge-approve flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> APPROVE</span>;
  }
  if (decision === "REJECT") {
    return <span className="px-2.5 py-0.5 rounded text-[11px] font-bold badge-reject flex items-center gap-1"><XCircle className="w-3 h-3" /> REJECT</span>;
  }
  return <span className="px-2.5 py-0.5 rounded text-[11px] font-bold badge-review flex items-center gap-1"><AlertCircle className="w-3 h-3" /> REVIEW</span>;
}
