import React, { useState, useEffect } from "react";
import { Users, CheckCircle2, XCircle, HelpCircle, AlertTriangle, ShieldCheck, Loader2 } from "lucide-react";
import { api } from "../api";

export default function HumanReviewView({ onReviewProcessed }) {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState(null);
  const [reviewerName, setReviewerName] = useState("Agency Officer");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [actionType, setActionType] = useState(null); // APPROVE, REJECT, REQUEST_MORE_INFO

  const loadReviews = async () => {
    setLoading(true);
    try {
      const data = await api.getHumanReviews();
      setReviews(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, []);

  const handleActionClick = (review, action) => {
    setSelectedReview(review);
    setActionType(action);
    setNotes("");
  };

  const handleConfirmSubmit = async () => {
    if (!selectedReview || !actionType) return;
    setSubmitting(true);
    try {
      await api.processHumanReview({
        request_id: selectedReview.request_id,
        action: actionType,
        reviewer_name: reviewerName,
        notes: notes
      });
      setSelectedReview(null);
      setActionType(null);
      await loadReviews();
      if (onReviewProcessed) onReviewProcessed();
    } catch (err) {
      alert("Error processing review: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const pendingCount = reviews.filter(r => r.status === "PENDING").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-amber-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <Users className="w-6 h-6 text-amber-400" />
            Human Review & Decision Governance Queue
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Cases escalated by the arbitration engine due to model disagreement, high risk tier, or low confidence thresholds.
          </p>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-amber-950/60 border border-amber-500/40 text-amber-300 text-xs font-bold">
          <span>Pending Cases: {pendingCount}</span>
        </div>
      </div>

      {/* Review Queue Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-gray-400 glass-panel rounded-2xl">Loading review queue...</div>
        ) : reviews.length === 0 ? (
          <div className="p-12 text-center text-gray-400 glass-panel rounded-2xl">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-2" />
            <h4 className="font-bold text-gray-200">Queue is Clear</h4>
            <p className="text-xs text-gray-500 mt-1">No decision requests currently pending human intervention.</p>
          </div>
        ) : (
          reviews.map((rev) => (
            <div key={rev.id} className="glass-panel p-6 rounded-2xl space-y-4 border border-gray-800 hover:border-gray-700 transition-all">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800/80 pb-3">
                <div className="flex items-center space-x-3">
                  <span className="font-mono font-bold text-cyan-400 text-sm">{rev.request_id}</span>
                  <span className="text-xs font-semibold text-gray-200">{rev.request_type}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold risk-${rev.risk_level.toLowerCase()}`}>
                    {rev.risk_level} RISK
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  Status: <b className={rev.status === "PENDING" ? "text-amber-400 font-bold" : "text-emerald-400"}>{rev.status}</b>
                </div>
              </div>

              <div className="text-xs text-gray-300 leading-relaxed bg-gray-900/50 p-3 rounded-xl border border-gray-800">
                <b>Description:</b> {rev.description} (Applicant: {rev.applicant_id})
              </div>

              {/* Model Outputs Breakdown */}
              <div className="space-y-2">
                <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">AI Model Decision Breakdown</h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {rev.model_decisions.map((md, idx) => (
                    <div key={idx} className="p-3 bg-gray-900/80 rounded-xl border border-gray-800 text-xs flex justify-between items-center">
                      <div>
                        <div className="font-bold text-gray-200">{md.model}</div>
                        <div className="text-[10px] text-gray-500">Confidence: {md.confidence}%</div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        md.decision === "APPROVE" ? "badge-approve" : md.decision === "REJECT" ? "badge-reject" : "badge-review"
                      }`}>
                        {md.decision}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Human Decision Controls or Recorded Result */}
              {rev.status === "PENDING" ? (
                <div className="pt-2 flex flex-wrap items-center justify-end gap-3 border-t border-gray-800/80">
                  <span className="text-xs text-gray-400 mr-auto">Human Override Actions:</span>
                  <button
                    onClick={() => handleActionClick(rev, "APPROVE")}
                    className="px-4 py-2 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 font-semibold text-xs rounded-xl flex items-center gap-1.5 cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>APPROVE</span>
                  </button>
                  <button
                    onClick={() => handleActionClick(rev, "REJECT")}
                    className="px-4 py-2 bg-rose-950 hover:bg-rose-900 border border-rose-700 text-rose-300 font-semibold text-xs rounded-xl flex items-center gap-1.5 cursor-pointer"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>REJECT</span>
                  </button>
                  <button
                    onClick={() => handleActionClick(rev, "REQUEST_MORE_INFO")}
                    className="px-4 py-2 bg-amber-950 hover:bg-amber-900 border border-amber-700 text-amber-300 font-semibold text-xs rounded-xl flex items-center gap-1.5 cursor-pointer"
                  >
                    <HelpCircle className="w-4 h-4" />
                    <span>REQUEST INFO</span>
                  </button>
                </div>
              ) : (
                <div className="pt-2 text-xs bg-emerald-950/30 p-3 rounded-xl border border-emerald-800/40 text-emerald-300 flex justify-between items-center">
                  <div>Reviewer: <b>{rev.reviewer_name}</b> | Decision: <b>{rev.human_decision}</b></div>
                  <div className="text-[11px] text-gray-400">{rev.review_notes}</div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Review Confirmation Modal */}
      {selectedReview && actionType && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel max-w-md w-full p-6 rounded-2xl space-y-4 border border-cyan-500/30">
            <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              Confirm Human Review Decision
            </h3>
            <p className="text-xs text-gray-300">
              You are recording decision <b>{actionType}</b> for request <span className="font-mono font-bold text-cyan-300">{selectedReview.request_id}</span>.
            </p>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">Reviewer Name / Officer ID</label>
              <input
                type="text"
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2.5 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">Justification & Review Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                placeholder="Enter justification for overriding AI model recommendation..."
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2.5 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => setSelectedReview(null)}
                className="px-4 py-2 bg-gray-800 text-gray-300 text-xs rounded-lg hover:bg-gray-700 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmSubmit}
                disabled={submitting}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold rounded-lg flex items-center gap-1.5 cursor-pointer"
              >
                {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                <span>Submit & Record Audit Log</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
