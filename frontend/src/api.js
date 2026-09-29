const PRIMARY_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
const SECONDARY_BASE = "http://localhost:8000/api";

export async function fetchAPI(endpoint, options = {}) {
  const tryFetch = async (baseUrl) => {
    const res = await fetch(`${baseUrl}${endpoint}`, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "API Request Failed");
    }
    return await res.json();
  };

  try {
    return await tryFetch(PRIMARY_BASE);
  } catch (primaryErr) {
    try {
      return await tryFetch(SECONDARY_BASE);
    } catch (secondaryErr) {
      console.error(`API Error on ${endpoint}:`, secondaryErr);
      throw secondaryErr;
    }
  }
}

export const api = {
  getVendors: () => fetchAPI("/vendors"),
  createVendor: (data) => fetchAPI("/vendors", { method: "POST", body: JSON.stringify(data) }),
  updateVendor: (id, data) => fetchAPI(`/vendors/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  getModels: () => fetchAPI("/models"),
  createModel: (data) => fetchAPI("/models", { method: "POST", body: JSON.stringify(data) }),
  updateModel: (id, data) => fetchAPI(`/models/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  getDecisions: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchAPI(`/decisions${query ? `?${query}` : ""}`);
  },
  getDecisionDetail: (requestId) => fetchAPI(`/decisions/${requestId}`),
  createDecision: (data) => fetchAPI("/decisions", { method: "POST", body: JSON.stringify(data) }),

  getPolicies: () => fetchAPI("/policies"),
  activatePolicy: (policyId) => fetchAPI(`/policies/${policyId}/activate`, { method: "PUT" }),
  updatePolicy: (policyId, data) => fetchAPI(`/policies/${policyId}`, { method: "PUT", body: JSON.stringify(data) }),

  getAuditLogs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchAPI(`/audit-logs${query ? `?${query}` : ""}`);
  },

  getHumanReviews: () => fetchAPI("/human-review"),
  processHumanReview: (data) => fetchAPI("/human-review", { method: "POST", body: JSON.stringify(data) }),

  getAnalytics: () => fetchAPI("/analytics"),

  getExperimentResults: () => fetchAPI("/experiment/results"),
  runExperiment: () => fetchAPI("/experiment/run", { method: "POST" }),

  getScenarios: () => fetchAPI("/scenarios"),
  runScenario: (scenarioKey) => fetchAPI(`/scenarios/run/${scenarioKey}`, { method: "POST" }),
};
