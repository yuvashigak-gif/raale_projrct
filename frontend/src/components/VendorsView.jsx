import React, { useState, useEffect } from "react";
import { Server, Building2, CheckCircle2 } from "lucide-react";
import { api } from "../api";

export default function VendorsView() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadVendors = async () => {
    setLoading(true);
    try {
      const data = await api.getVendors();
      setVendors(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVendors();
  }, []);

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-cyan-500">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <Server className="w-6 h-6 text-cyan-400" />
            AI Vendor Management & Governance
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Registered external AI vendors supplying decision service models for public agency operations.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full p-8 text-center text-gray-400">Loading Vendors...</div>
        ) : (
          vendors.map((v) => (
            <div key={v.id} className="glass-panel p-5 rounded-2xl space-y-3 border border-gray-800 hover:border-cyan-500/40 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 bg-gray-900 border border-gray-700 rounded-xl text-cyan-400">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-100 text-sm">{v.vendor_name}</h3>
                    <span className="text-[10px] font-mono text-cyan-400">{v.vendor_id}</span>
                  </div>
                </div>
                <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                  v.status === "Active" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-gray-800 text-gray-500"
                }`}>
                  {v.status}
                </span>
              </div>

              <p className="text-xs text-gray-400 line-clamp-2">{v.description}</p>

              <div className="grid grid-cols-2 gap-2 pt-2 text-xs bg-gray-900/60 p-2.5 rounded-xl border border-gray-800">
                <div>
                  <span className="text-[10px] text-gray-500 block">Reliability Score</span>
                  <span className="font-bold text-emerald-400">{(v.reliability_score * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 block">Average Latency</span>
                  <span className="font-mono font-semibold text-amber-400">{v.average_latency} ms</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
