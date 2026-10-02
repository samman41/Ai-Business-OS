const API_BASE = (window.location.protocol && window.location.protocol.startsWith("http"))
  ? "/api"
  : "http://127.0.0.1:8000/api";

const API = {
  async fetchJSON(url, options = {}) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned status ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error [${url}]:`, err);
      throw err;
    }
  },

  // Dashboard
  getDashboardStats() {
    return this.fetchJSON(`${API_BASE}/dashboard/stats`);
  },

  getDashboardChart() {
    return this.fetchJSON(`${API_BASE}/dashboard/revenue-chart`);
  },

  getDashboardInsights() {
    return this.fetchJSON(`${API_BASE}/dashboard/insights`);
  },

  // Customers CRM
  getCustomers(status = "All", search = "") {
    const params = new URLSearchParams();
    if (status && status !== "All") params.append("status", status);
    if (search) params.append("search", search);
    return this.fetchJSON(`${API_BASE}/customers?${params.toString()}`);
  },

  getCustomerDetail(id) {
    return this.fetchJSON(`${API_BASE}/customers/${id}`);
  },

  generateCustomerSummary(id) {
    return this.fetchJSON(`${API_BASE}/customers/${id}/generate-summary`, { method: "POST" });
  },

  generateCustomerEmail(id, type = null) {
    let url = `${API_BASE}/customers/${id}/generate-email`;
    if (type) url += `?email_type=${type}`;
    return this.fetchJSON(url, { method: "POST" });
  },

  createCustomer(data) {
    return this.fetchJSON(`${API_BASE}/customers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  },


  // Inventory
  getProducts(status = "All", search = "") {
    const params = new URLSearchParams();
    if (status && status !== "All") params.append("stock_status", status);
    if (search) params.append("search", search);
    return this.fetchJSON(`${API_BASE}/inventory/products?${params.toString()}`);
  },

  getCategories() {
    return this.fetchJSON(`${API_BASE}/inventory/categories`);
  },

  createProduct(data) {
    return this.fetchJSON(`${API_BASE}/inventory/products`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  },

  getReorderSuggestions() {
    return this.fetchJSON(`${API_BASE}/inventory/reorder-suggestions`);
  },

  // Sales
  getOrders() {
    return this.fetchJSON(`${API_BASE}/sales/orders`);
  },

  getOrderDetail(id) {
    return this.fetchJSON(`${API_BASE}/sales/orders/${id}`);
  },

  createOrder(data) {
    return this.fetchJSON(`${API_BASE}/sales/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  },

  // Documents
  getDocuments() {
    return this.fetchJSON(`${API_BASE}/documents`);
  },

  uploadDocument(formData) {
    return this.fetchJSON(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData
    });
  },

  searchDocuments(query) {
    return this.fetchJSON(`${API_BASE}/documents/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
  },

  // AI Assistant
  queryAIAssistant(query) {
    return this.fetchJSON(`${API_BASE}/ai-assistant/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
  },

  // Reports & Settings
  getExecutiveReportData() {
    return this.fetchJSON(`${API_BASE}/reports/business-summary`);
  },

  saveAPIKey(key) {
    return this.fetchJSON(`${API_BASE}/reports/settings/openai-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ openai_api_key: key })
    });
  },

  // Insights
  getDailyBriefing() {
    return this.fetchJSON(`${API_BASE}/insights/daily-briefing`);
  },
  getForecast() {
    return this.fetchJSON(`${API_BASE}/insights/forecast`);
  },
  getAnomalies() {
    return this.fetchJSON(`${API_BASE}/insights/anomalies`);
  }
};
