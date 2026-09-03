import React from "react";
import { ShieldCheck, Cpu, PlayCircle, Clock, Users, Server, Scale, FileText, BarChart3, HelpCircle, AlertTriangle } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, activePolicyName, pendingReviewsCount }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "create", label: "Run Arbitration", icon: PlayCircle },
    { id: "history", label: "Decision History", icon: Clock },
    { id: "human-review", label: "Human Review", icon: Users, badge: pendingReviewsCount },
    { id: "models", label: "AI Models", icon: Cpu },
    { id: "vendors", label: "Vendors", icon: Server },
    { id: "policies", label: "Policies Engine", icon: Scale },
    { id: "audit", label: "Audit Logs", icon: FileText },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "scenarios", label: "Demo Scenarios", icon: PlayCircle },
    { id: "viva", label: "Viva & Docs", icon: HelpCircle },
  ];

  return (
    <header className="border-b border-gray-800 bg-gray-950/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Brand Title */}
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-950/80 border border-cyan-500/30 rounded-xl text-cyan-400">
            <ShieldCheck className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-100 flex items-center gap-2">
              AI Model Arbitration Layer
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                PUBLIC AGENCY GOVERNANCE
              </span>
            </h1>
            <p className="text-xs text-gray-400">Multi-Vendor AI Model Consensus & Arbitration Engine</p>
          </div>
        </div>

        {/* System Indicators */}
        <div className="flex items-center space-x-3">
          {/* SIMULATION MODE BADGE */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-amber-950/60 border border-amber-500/40 text-amber-300 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>SIMULATION MODE</span>
          </div>

          {/* ACTIVE POLICY BADGE */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-gray-300">
            <Scale className="w-3.5 h-3.5 text-cyan-400" />
            <span>Policy:</span>
            <span className="font-semibold text-cyan-300">{activePolicyName || "Weighted Reliability + Confidence"}</span>
          </div>
        </div>
      </div>

      {/* Navigation Links Bar */}
      <div className="max-w-7xl mx-auto px-4 flex items-center space-x-1 overflow-x-auto text-sm py-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg font-medium transition-all text-xs cursor-pointer whitespace-nowrap ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-900/30"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/60"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
              {item.badge ? (
                <span className="ml-1.5 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500 text-white">
                  {item.badge}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
    </header>
  );
}
