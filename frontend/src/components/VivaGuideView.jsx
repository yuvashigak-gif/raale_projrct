import React from "react";
import { HelpCircle, BookOpen, Scale, ShieldCheck, CheckCircle2 } from "lucide-react";

export default function VivaGuideView() {
  const vivaQA = [
    {
      q: "What is the core problem solved by this system?",
      a: "Public agencies piloting AI models from multiple vendors (e.g. OpenAI, Anthropic, Google) receive conflicting recommendations (e.g. APPROVE vs REJECT) for the same request. This system acts as an Arbitration Layer to evaluate reliability, confidence, accuracy, and risk to determine the final decision."
    },
    {
      q: "How does the arbitration algorithm work?",
      a: "It uses a weighted mathematical formula:\nFinal Score = (Model Reliability × 0.35) + (Model Confidence × 0.30) + (Historical Accuracy × 0.20) + (Consensus Score × 0.15).\nThe candidate decision with the strongest composite evidence is selected."
    },
    {
      q: "Why do we need human-in-the-loop governance?",
      a: "AI models can hallucinate or fail on high-risk edge cases. High/Critical risk requests or cases with model disagreement and low confidence are escalated to the Human Review Queue where human officers issue final sign-off recorded in the audit log."
    },
    {
      q: "What is an Audit Log and why is it mandatory for public agency AI?",
      a: "An audit log records every step: raw model outputs, selected policy, weighted scores, winning model, and reviewer notes. In government decision-making, explainability and legal accountability require a verifiable audit trail for every automated decision."
    },
    {
      q: "How do Arbitration Policies work?",
      a: "Policies define governance rules (e.g., Majority Voting, Weighted Confidence, Highest Reliability, High Risk Human Review). The policy engine applies the administrator's active policy to govern decisions dynamically."
    }
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <HelpCircle className="w-6 h-6 text-cyan-400" />
            Viva & College Presentation Quick Reference Guide
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Simplified explanations of the arbitration algorithm, governance models, and project architecture for viva examinations.
          </p>
        </div>
      </div>

      {/* Simple Summary Box */}
      <div className="glass-panel p-6 rounded-2xl space-y-3 bg-cyan-950/20 border border-cyan-500/30">
        <h3 className="text-sm font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          The 30-Second Viva Summary
        </h3>
        <p className="text-xs text-gray-200 leading-relaxed">
          "Three AI models evaluate a public agency request. Instead of blindly trusting one model, our arbitration engine calculates a weighted score using vendor reliability, model confidence, historical accuracy, and consensus. The decision with the strongest overall evidence wins. If models disagree or the request is high risk, it automatically escalates to a human reviewer while creating an immutable audit trail."
        </p>
      </div>

      {/* Q&A List */}
      <div className="space-y-4">
        {vivaQA.map((item, idx) => (
          <div key={idx} className="glass-panel p-5 rounded-2xl space-y-2 border border-gray-800">
            <h4 className="font-bold text-cyan-300 text-xs flex items-center gap-2">
              <span className="p-1 rounded bg-cyan-950 text-cyan-400 font-mono">Q{idx+1}</span>
              <span>{item.q}</span>
            </h4>
            <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-line pl-7">
              {item.a}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
