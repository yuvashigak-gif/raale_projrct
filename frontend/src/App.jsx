import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import DashboardView from "./components/DashboardView";
import CreateDecisionView from "./components/CreateDecisionView";
import DecisionHistoryView from "./components/DecisionHistoryView";
import HumanReviewView from "./components/HumanReviewView";
import ModelsView from "./components/ModelsView";
import VendorsView from "./components/VendorsView";
import PoliciesView from "./components/PoliciesView";
import AuditLogsView from "./components/AuditLogsView";
import AnalyticsView from "./components/AnalyticsView";
import DemoScenariosView from "./components/DemoScenariosView";
import VivaGuideView from "./components/VivaGuideView";
import DecisionDetailModal from "./components/DecisionDetailModal";
import { api } from "./api";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [analytics, setAnalytics] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [inspectRequestId, setInspectRequestId] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadGlobalData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [anData, polData, hrData] = await Promise.all([
        api.getAnalytics(),
        api.getPolicies(),
        api.getHumanReviews()
      ]);
      setAnalytics(anData);
      setPolicies(polData);
      setPendingCount(hrData.filter(r => r.status === "PENDING").length);
    } catch (err) {
      console.error("Global Data Load Error:", err);
      setErrorMsg(err.message || "Failed to connect to backend server at http://127.0.0.1:8000/api");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGlobalData();
  }, [activeTab]);

  const activePolicy = policies.find(p => p.is_active) || policies[0];

  return (
    <div className="min-h-screen bg-[#090d16] text-gray-100 flex flex-col font-sans">
      {/* Top Header Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activePolicyName={activePolicy?.policy_name}
        pendingReviewsCount={pendingCount}
      />

      {/* Main Body Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {errorMsg && (
          <div className="mb-6 p-4 bg-rose-950/80 border border-rose-800 rounded-xl text-rose-200 text-xs flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
              <span>{errorMsg}</span>
            </div>
            <button
              onClick={loadGlobalData}
              className="px-3 py-1.5 bg-rose-900 hover:bg-rose-800 text-white rounded-lg font-semibold flex items-center gap-1 cursor-pointer shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Connection</span>
            </button>
          </div>
        )}

        {activeTab === "dashboard" && (
          <DashboardView analytics={analytics} onNavigate={setActiveTab} />
        )}

        {activeTab === "create" && (
          <CreateDecisionView
            activePolicy={activePolicy}
            onArbitrationDone={loadGlobalData}
          />
        )}

        {activeTab === "history" && (
          <DecisionHistoryView onSelectDecision={setInspectRequestId} />
        )}

        {activeTab === "human-review" && (
          <HumanReviewView onReviewProcessed={loadGlobalData} />
        )}

        {activeTab === "models" && <ModelsView />}

        {activeTab === "vendors" && <VendorsView />}

        {activeTab === "policies" && (
          <PoliciesView onPolicyChange={loadGlobalData} />
        )}

        {activeTab === "audit" && <AuditLogsView />}

        {activeTab === "analytics" && <AnalyticsView analytics={analytics} />}

        {activeTab === "scenarios" && (
          <DemoScenariosView onScenarioExecuted={loadGlobalData} />
        )}

        {activeTab === "viva" && <VivaGuideView />}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-900 bg-gray-950 py-4 text-center text-xs text-gray-500">
        AI Model Arbitration Layer & Governance System for Public Agency Decision Making &bull; Simulated AI Mode
      </footer>

      {/* Inspection Modal */}
      {inspectRequestId && (
        <DecisionDetailModal
          requestId={inspectRequestId}
          onClose={() => setInspectRequestId(null)}
        />
      )}
    </div>
  );
}
