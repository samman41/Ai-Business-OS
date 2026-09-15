// Main Application Orchestrator for AI Business OS

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initDashboardTab();
  initCustomersTab();
  initInventoryTab();
  initSalesTab();
  initDocumentsTab();
  initAssistantTab();
  initReportsTab();
  initSettingsTab();
  initModals();
});

// Navigation Handling
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const tabViews = document.querySelectorAll(".tab-view");
  const pageHeading = document.getElementById("current-tab-title");

  const tabTitles = {
    dashboard: "Executive Dashboard",
    customers: "Customer Relationship Management (CRM)",
    inventory: "Inventory & Stock Intelligence",
    sales: "Sales Ledger & Invoicing",
    documents: "AI Document Vault & RAG Index",
    assistant: "AI Business Assistant",
    reports: "Reports & Data Export Hub",
    settings: "System Settings & API Config"
  };

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetTab = item.getAttribute("data-tab");
      if (!targetTab) return;

      navItems.forEach(n => n.classList.remove("active"));
      tabViews.forEach(v => v.classList.remove("active"));

      item.classList.add("active");
      const targetView = document.getElementById(`view-${targetTab}`);
      if (targetView) targetView.classList.add("active");

      if (pageHeading && tabTitles[targetTab]) {
        pageHeading.innerText = tabTitles[targetTab];
      }

      // Refresh data on tab activation
      if (targetTab === "dashboard") loadDashboardData();
      if (targetTab === "customers") loadCustomersData();
      if (targetTab === "inventory") loadInventoryData();
      if (targetTab === "sales") loadSalesData();
      if (targetTab === "documents") loadDocumentsData();
    });
  });

  const quickAssistBtn = document.getElementById("quick-assistant-btn");
  if (quickAssistBtn) {
    quickAssistBtn.addEventListener("click", () => {
      document.querySelector('.nav-item[data-tab="assistant"]').click();
    });
  }
}

// -------------------------------------------------------------
// 1. DASHBOARD
// -------------------------------------------------------------
async function initDashboardTab() {
  loadDashboardData();
}

async function loadDashboardData() {
  try {
    const stats = await API.getDashboardStats();
    renderKPIs(stats);

    const chartData = await API.getDashboardChart();
    renderRevenueChart(chartData);

    const insights = await API.getDashboardInsights();
    renderDashboardInsights(insights);
  } catch (err) {
    console.error("Error loading dashboard:", err);
  }
}

function renderKPIs(stats) {
  const container = document.getElementById("dashboard-kpi-grid");
  if (!container) return;

  container.innerHTML = `
    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Gross Revenue</span>
        <div class="kpi-icon"><i class="fa-solid fa-wallet"></i></div>
      </div>
      <div class="kpi-value">$${stats.total_revenue.toLocaleString()}</div>
      <div class="kpi-trend positive">
        <i class="fa-solid fa-arrow-trend-up"></i> +${stats.revenue_growth_pct}% vs last month
      </div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Net Operating Profit</span>
        <div class="kpi-icon"><i class="fa-solid fa-coins"></i></div>
      </div>
      <div class="kpi-value">$${stats.net_profit.toLocaleString()}</div>
      <div class="kpi-trend positive">
        <i class="fa-solid fa-percent"></i> ${stats.profit_margin}% Operating Margin
      </div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Active Customers</span>
        <div class="kpi-icon"><i class="fa-solid fa-users"></i></div>
      </div>
      <div class="kpi-value">${stats.active_customers}</div>
      <div class="kpi-trend neutral">
        <i class="fa-solid fa-check"></i> High account retention
      </div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Low Stock Alerts</span>
        <div class="kpi-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
      </div>
      <div class="kpi-value" style="color: ${stats.low_stock_count > 0 ? '#DC2626' : '#141414'}">${stats.low_stock_count}</div>
      <div class="kpi-trend ${stats.low_stock_count > 0 ? 'negative' : 'positive'}">
        <i class="fa-solid fa-boxes-stacked"></i> ${stats.low_stock_count > 0 ? 'Action required' : 'Stock healthy'}
      </div>
    </div>
  `;
}

function renderDashboardInsights(insights) {
  const container = document.getElementById("dashboard-insights-list");
  if (!container) return;

  container.innerHTML = insights.map(i => {
    const badgeClass = i.severity === "High" ? "badge-danger" : (i.severity === "Positive" ? "badge-success" : "badge-warning");
    return `
      <div style="padding: 12px; background: #FAF8F5; border-radius: 10px; border-left: 4px solid var(--gold-primary);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong style="font-size: 14px; color: var(--text-dark);">${i.title}</strong>
          <span class="badge ${badgeClass}">${i.severity}</span>
        </div>
        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.4;">${i.description}</p>
      </div>
    `;
  }).join("");
}

// -------------------------------------------------------------
// 2. CUSTOMERS CRM
// -------------------------------------------------------------
function initCustomersTab() {
  loadCustomersData();

  const searchInput = document.getElementById("customer-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      loadCustomersData("All", e.target.value);
    });
  }

  const formAddCust = document.getElementById("form-add-customer");
  if (formAddCust) {
    formAddCust.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById("cust-name-input").value,
        email: document.getElementById("cust-email-input").value,
        phone: document.getElementById("cust-phone-input").value,
        company: document.getElementById("cust-company-input").value,
        status: document.getElementById("cust-status-input").value,
        initial_balance: parseFloat(document.getElementById("cust-initial-balance-input").value) || 0.0,
        notes: document.getElementById("cust-notes-input").value
      };

      try {
        await API.createCustomer(payload);
        closeModal("modal-add-customer");
        loadCustomersData();
        formAddCust.reset();
      } catch (err) {
        alert("Error creating customer: " + err.message);
      }
    });
  }
}

async function loadCustomersData(status = "All", search = "") {
  try {
    const customers = await API.getCustomers(status, search);
    const tbody = document.getElementById("customers-table-body");
    if (!tbody) return;

    tbody.innerHTML = customers.map(c => `
      <tr>
        <td>
          <strong style="color: var(--text-dark);">${c.name}</strong><br>
          <span style="font-size: 12px; color: var(--text-muted);">${c.email}</span>
        </td>
        <td>${c.company}</td>
        <td><span class="badge ${c.status === 'VIP' ? 'badge-gold' : (c.status === 'At-Risk' ? 'badge-danger' : 'badge-success')}">${c.status}</span></td>
        <td><strong style="color: var(--gold-dark);">$${c.ltv.toLocaleString()}</strong></td>
        <td>${c.total_orders} orders</td>
        <td>${c.last_order_date}</td>
        <td>
          <button class="btn btn-outline-gold btn-sm" onclick="openCustomerDetail(${c.id})">
            <i class="fa-solid fa-eye"></i> Profile
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error loading customers:", err);
  }
}

async function openCustomerDetail(id) {
  try {
    const c = await API.getCustomerDetail(id);
    document.getElementById("cust-modal-name").innerText = `${c.name} (${c.company})`;
    
    const body = document.getElementById("cust-modal-body");
    body.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
        <div style="padding: 14px; background: var(--gold-light); border-radius: 10px; border: 1px solid var(--gold-border);">
          <span style="font-size: 12px; color: var(--text-muted);">Email:</span> <strong>${c.email}</strong><br>
          <span style="font-size: 12px; color: var(--text-muted);">Phone:</span> <strong>${c.phone || 'N/A'}</strong>
        </div>
        <div style="padding: 14px; background: var(--gold-light); border-radius: 10px; border: 1px solid var(--gold-border);">
          <span style="font-size: 12px; color: var(--text-muted);">Lifetime Spent:</span> <strong style="color: var(--gold-dark); font-size: 18px;">$${c.ltv.toLocaleString()}</strong><br>
          <span style="font-size: 12px; color: var(--text-muted);">Initial Balance:</span> <strong style="color: var(--gold-dark); font-size: 14px;">$${(c.initial_balance || 0).toLocaleString()}</strong><br>
          <span style="font-size: 12px; color: var(--text-muted);">Status Tier:</span> <span class="badge badge-gold">${c.status}</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong style="font-size: 14px; color: var(--text-dark);"><i class="fa-solid fa-brain" style="color: var(--gold-primary);"></i> AI Persona Summary</strong>
          <button class="btn btn-outline-gold btn-sm" onclick="refreshAISummary(${c.id})"><i class="fa-solid fa-rotate"></i> Refresh AI</button>
        </div>
        <div id="ai-summary-text" style="padding: 14px; background: #FAF7F0; border-left: 3px solid var(--gold-primary); font-size: 13px; color: var(--text-body); border-radius: 6px;">
          ${c.ai_summary || 'No AI summary generated.'}
        </div>
      </div>

      <strong style="font-size: 14px; color: var(--text-dark); display: block; margin-bottom: 10px;">Purchase Order History (${c.orders.length})</strong>
      <div style="max-height: 200px; overflow-y: auto;">
        ${c.orders.map(o => `
          <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid var(--border-subtle); font-size: 13px;">
            <span><strong>${o.order_number}</strong> (${o.order_date})</span>
            <span class="badge badge-gold">$${o.total_amount.toLocaleString()}</span>
          </div>
        `).join("")}
      </div>
    `;

    document.getElementById("modal-customer-detail").classList.add("active");
  } catch (err) {
    console.error("Error opening customer detail:", err);
  }
}

async function refreshAISummary(id) {
  const summaryBox = document.getElementById("ai-summary-text");
  if (summaryBox) summaryBox.innerText = "Generating AI insights...";
  try {
    const res = await API.generateCustomerSummary(id);
    if (summaryBox) summaryBox.innerText = res.ai_summary;
  } catch (err) {
    if (summaryBox) summaryBox.innerText = "Failed to update AI summary.";
  }
}

// -------------------------------------------------------------
// 3. INVENTORY & REORDER ENGINE
// -------------------------------------------------------------
function initInventoryTab() {
  loadInventoryData();

  const searchInput = document.getElementById("inventory-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      loadInventoryData("All", e.target.value);
    });
  }

  const formAddProd = document.getElementById("form-add-product");
  if (formAddProd) {
    formAddProd.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById("prod-name").value,
        sku: document.getElementById("prod-sku").value,
        category_id: parseInt(document.getElementById("prod-category").value || 1),
        stock_qty: parseInt(document.getElementById("prod-stock").value),
        min_stock_threshold: parseInt(document.getElementById("prod-threshold").value),
        cost_price: parseFloat(document.getElementById("prod-cost").value),
        selling_price: parseFloat(document.getElementById("prod-price").value)
      };

      try {
        await API.createProduct(payload);
        closeModal("modal-add-product");
        loadInventoryData();
      } catch (err) {
        alert("Error creating product: " + err.message);
      }
    });
  }
}

async function loadInventoryData(status = "All", search = "") {
  try {
    const products = await API.getProducts(status, search);
    const tbody = document.getElementById("inventory-table-body");
    if (tbody) {
      tbody.innerHTML = products.map(p => `
        <tr>
          <td><code>${p.sku}</code></td>
          <td><strong style="color: var(--text-dark);">${p.name}</strong></td>
          <td>${p.category_name}</td>
          <td>
            <span class="badge ${p.stock_status === 'Out of Stock' ? 'badge-danger' : (p.stock_status === 'Low Stock' ? 'badge-warning' : 'badge-success')}">
              ${p.stock_qty} units (${p.stock_status})
            </span>
          </td>
          <td>$${p.cost_price.toFixed(2)}</td>
          <td><strong>$${p.selling_price.toFixed(2)}</strong></td>
          <td><span style="color: var(--gold-dark); font-weight: 600;">$${p.profit_margin.toFixed(2)} (${p.margin_pct}%)</span></td>
          <td>${p.supplier}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="editStockPrompt(${p.id}, ${p.stock_qty})">
              <i class="fa-solid fa-pen-to-square"></i> Stock
            </button>
          </td>
        </tr>
      `).join("");
    }

    const suggestions = await API.getReorderSuggestions();
    renderReorderSuggestions(suggestions);

    // Render Categories in Add Product select dropdown
    const categories = await API.getCategories();
    const catSelect = document.getElementById("prod-category");
    if (catSelect) {
      catSelect.innerHTML = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    }
  } catch (err) {
    console.error("Error loading inventory:", err);
  }
}

function renderReorderSuggestions(suggestions) {
  const container = document.getElementById("reorder-suggestions-container");
  const banner = document.getElementById("reorder-banner");
  if (!container) return;

  if (suggestions.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); font-size: 14px;">✅ Stock levels healthy. No urgent reorder recommendations.</p>`;
    if (banner) banner.style.display = "none";
    return;
  }

  if (banner) {
    banner.style.display = "block";
    banner.innerHTML = `
      <div style="padding: 16px; background: #FEF2F2; border: 1px solid #FECACA; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px; color: #991B1B;">
          <i class="fa-solid fa-triangle-exclamation" style="font-size: 22px;"></i>
          <div>
            <strong>AI Stock Alert: ${suggestions.length} items require reordering</strong>
            <p style="font-size: 13px; margin-top: 2px;">Replenish inventory to prevent order delays.</p>
          </div>
        </div>
      </div>
    `;
  }

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
      ${suggestions.map(s => `
        <div style="padding: 16px; background: #FAF7F0; border-radius: 12px; border: 1px solid var(--gold-border);">
          <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <strong style="color: var(--text-dark);">${s.product_name}</strong>
            <span class="badge ${s.urgency === 'Critical' ? 'badge-danger' : 'badge-warning'}">${s.urgency}</span>
          </div>
          <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">${s.reason}</p>
          <div style="display: flex; justify-content: space-between; font-size: 13px;">
            <span>Suggested Qty: <strong style="color: var(--gold-dark);">+${s.suggested_reorder_qty} units</strong></span>
            <span>Est. Cost: <strong>$${s.est_total_cost.toLocaleString()}</strong></span>
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

async function editStockPrompt(id, currentStock) {
  const newStock = prompt("Enter new stock quantity for product:", currentStock);
  if (newStock !== null && !isNaN(newStock)) {
    try {
      await API.fetchJSON(`/api/inventory/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stock_qty: parseInt(newStock) })
      });
      loadInventoryData();
    } catch (err) {
      alert("Failed to update stock: " + err.message);
    }
  }
}

// -------------------------------------------------------------
// 4. SALES & INVOICES
// -------------------------------------------------------------
function initSalesTab() {
  loadSalesData();

  const btnCreateOrder = document.getElementById("btn-create-order-modal");
  if (btnCreateOrder) {
    btnCreateOrder.addEventListener("click", async () => {
      // Fetch customers and products for selects
      try {
        const customers = await API.getCustomers();
        const products = await API.getProducts();

        const custSelect = document.getElementById("order-customer-select");
        custSelect.innerHTML = customers.map(c => `<option value="${c.id}">${c.name} (${c.company})</option>`).join("");

        const prodSelect = document.getElementById("order-product-select");
        prodSelect.innerHTML = products.map(p => `<option value="${p.id}">${p.name} (Stock: ${p.stock_qty}) - $${p.selling_price}</option>`).join("");

        document.getElementById("modal-create-order").classList.add("active");
      } catch (err) {
        alert("Failed to load data for order: " + err.message);
      }
    });
  }

  const formCreateOrder = document.getElementById("form-create-order");
  if (formCreateOrder) {
    formCreateOrder.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const customerId = parseInt(document.getElementById("order-customer-select").value);
      const productId = parseInt(document.getElementById("order-product-select").value);
      const quantity = parseInt(document.getElementById("order-quantity").value);
      const shippingAddress = document.getElementById("order-shipping").value;
      const notes = document.getElementById("order-notes").value;

      if (isNaN(customerId) || isNaN(productId) || isNaN(quantity) || quantity <= 0) {
        alert("Please ensure valid Customer, Product, and Quantity are selected.");
        return;
      }

      const payload = {
        customer_id: customerId,
        items: [
          {
            product_id: productId,
            quantity: quantity
          }
        ],
        shipping_address: shippingAddress || undefined,
        notes: notes || undefined
      };

      try {
        await API.createOrder(payload);
        closeModal("modal-create-order");
        loadSalesData();
        formCreateOrder.reset();
      } catch (err) {
        alert("Error creating order: " + err.message);
      }
    });
  }
}

async function loadSalesData() {
  try {
    const orders = await API.getOrders();
    const tbody = document.getElementById("orders-table-body");
    if (!tbody) return;

    tbody.innerHTML = orders.map(o => `
      <tr>
        <td><strong>${o.order_number}</strong></td>
        <td>${o.customer_name} (${o.company})</td>
        <td>${o.order_date}</td>
        <td><span class="badge badge-success">${o.status}</span></td>
        <td><span class="badge badge-gold">${o.payment_status}</span></td>
        <td><strong style="color: var(--text-dark);">$${o.total_amount.toLocaleString()}</strong></td>
        <td><strong style="color: var(--gold-dark);">$${o.net_profit.toLocaleString()}</strong></td>
        <td>
          <button class="btn btn-outline-gold btn-sm" onclick="openInvoiceModal(${o.id})">
            <i class="fa-solid fa-file-invoice"></i> Invoice
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error loading sales:", err);
  }
}

async function openInvoiceModal(orderId) {
  try {
    const o = await API.getOrderDetail(orderId);
    const container = document.getElementById("invoice-printable-container");
    if (!container) return;

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid var(--gold-primary); padding-bottom: 16px; margin-bottom: 24px;">
        <div>
          <h2 style="font-family: 'Playfair Display', Georgia, serif; color: var(--gold-dark); font-size: 26px;">INVOICE</h2>
          <p style="font-size: 13px; color: #666;">AURA Business Operating System</p>
        </div>
        <div style="text-align: right;">
          <strong style="font-size: 16px;">${o.order_number}</strong>
          <p style="font-size: 12px; color: #666;">Date: ${o.order_date}</p>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; font-size: 13px;">
        <div>
          <strong style="color: var(--gold-dark); text-transform: uppercase;">Billed To:</strong><br>
          <strong>${o.customer ? o.customer.name : 'Valued Client'}</strong><br>
          ${o.customer ? o.customer.company : ''}<br>
          ${o.customer ? o.customer.email : ''}
        </div>
        <div>
          <strong style="color: var(--gold-dark); text-transform: uppercase;">Shipping Address:</strong><br>
          ${o.shipping_address}
        </div>
      </div>

      <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px;">
        <thead>
          <tr style="background: #FAF7F0; border-bottom: 1px solid var(--gold-border);">
            <th style="padding: 10px; text-align: left;">Item Description</th>
            <th style="padding: 10px; text-align: center;">Qty</th>
            <th style="padding: 10px; text-align: right;">Unit Price</th>
            <th style="padding: 10px; text-align: right;">Line Total</th>
          </tr>
        </thead>
        <tbody>
          ${o.items.map(item => `
            <tr style="border-bottom: 1px solid #EBE6DC;">
              <td style="padding: 10px;">${item.product_name} <br><small style="color: #888;">${item.sku}</small></td>
              <td style="padding: 10px; text-align: center;">${item.quantity}</td>
              <td style="padding: 10px; text-align: right;">$${item.unit_price.toFixed(2)}</td>
              <td style="padding: 10px; text-align: right;"><strong>$${item.total_price.toFixed(2)}</strong></td>
            </tr>
          `).join("")}
        </tbody>
      </table>

      <div style="display: flex; justify-content: flex-end;">
        <div style="width: 260px; font-size: 14px;">
          <div style="display: flex; justify-content: space-between; padding: 6px 0;">
            <span>Subtotal:</span> <span>$${o.total_amount.toFixed(2)}</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #CCC;">
            <span>Tax (0%):</span> <span>$0.00</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 10px 0; font-size: 18px; font-weight: 700; color: var(--gold-dark);">
            <span>Total Paid:</span> <span>$${o.total_amount.toFixed(2)}</span>
          </div>
        </div>
      </div>
    `;

    document.getElementById("modal-invoice").classList.add("active");

    const printBtn = document.getElementById("btn-print-invoice");
    if (printBtn) {
      printBtn.onclick = () => {
        html2pdf().from(container).save(`${o.order_number}_Invoice.pdf`);
      };
    }
  } catch (err) {
    console.error("Error opening invoice:", err);
  }
}

// -------------------------------------------------------------
// 5. DOCUMENTS VAULT & RAG SEARCH
// -------------------------------------------------------------
function initDocumentsTab() {
  loadDocumentsData();

  const dropzone = document.getElementById("doc-dropzone");
  const fileInput = document.getElementById("doc-file-input");
  const form = document.getElementById("upload-doc-form");

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        dropzone.querySelector("p").innerText = `Selected: ${fileInput.files[0].name}`;
      }
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!fileInput.files[0]) return alert("Please select a file to upload");

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("category", document.getElementById("doc-category-select").value);

      try {
        await API.uploadDocument(formData);
        form.reset();
        dropzone.querySelector("p").innerText = "Click or drag PDF / Docs here";
        loadDocumentsData();
      } catch (err) {
        alert("Upload error: " + err.message);
      }
    });
  }

  const searchBtn = document.getElementById("btn-doc-search");
  if (searchBtn) {
    searchBtn.addEventListener("click", async () => {
      const q = document.getElementById("doc-search-query").value;
      if (!q) return;
      try {
        const results = await API.searchDocuments(q);
        renderDocSearchResults(results);
      } catch (err) {
        console.error("Search error:", err);
      }
    });
  }
}

async function loadDocumentsData() {
  try {
    const docs = await API.getDocuments();
    const grid = document.getElementById("documents-grid");
    if (!grid) return;

    grid.innerHTML = docs.map(d => `
      <div style="padding: 16px; background: #FAF7F0; border-radius: 12px; border: 1px solid var(--gold-border);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <strong style="color: var(--text-dark); font-size: 15px;"><i class="fa-solid fa-file-pdf" style="color: var(--gold-primary);"></i> ${d.filename}</strong>
          <span class="badge badge-gold">${d.category}</span>
        </div>
        <p style="font-size: 13px; color: var(--text-body); margin-bottom: 8px; line-height: 1.4;">${d.summary}</p>
        <span style="font-size: 11px; color: var(--text-muted);">Uploaded: ${d.upload_date}</span>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error loading documents:", err);
  }
}

function renderDocSearchResults(results) {
  const container = document.getElementById("doc-search-results");
  if (!container) return;

  if (results.length === 0) {
    container.innerHTML = `<p style="font-size: 13px; color: var(--text-muted);">No matching document passages found.</p>`;
    return;
  }

  container.innerHTML = results.map(r => `
    <div style="padding: 10px; background: #FFF; border: 1px solid var(--gold-border); border-radius: 8px; margin-bottom: 8px;">
      <strong style="font-size: 13px; color: var(--gold-dark);">${r.filename}</strong>
      <p style="font-size: 12px; color: #444; margin-top: 4px;">${r.snippet}</p>
    </div>
  `).join("");
}

// -------------------------------------------------------------
// 6. AI ASSISTANT CHAT
// -------------------------------------------------------------
function initAssistantTab() {
  const sendBtn = document.getElementById("btn-send-assistant");
  const input = document.getElementById("assistant-input");

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => handleAssistantSend());
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handleAssistantSend();
    });
  }

  // Preset Pills
  document.querySelectorAll(".pill-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const q = btn.getAttribute("data-query");
      if (q) {
        document.querySelector('.nav-item[data-tab="assistant"]').click();
        if (input) input.value = q;
        handleAssistantSend();
      }
    });
  });
}

async function handleAssistantSend() {
  const input = document.getElementById("assistant-input");
  const log = document.getElementById("chat-messages-log");
  if (!input || !log) return;

  const query = input.value.trim();
  if (!query) return;

  // Append user bubble
  log.innerHTML += `
    <div class="message-bubble user">
      ${query}
    </div>
  `;
  input.value = "";
  log.scrollTop = log.scrollHeight;

  // Append thinking indicator
  const thinkingId = "thinking-" + Date.now();
  log.innerHTML += `
    <div class="message-bubble assistant" id="${thinkingId}">
      <i class="fa-solid fa-spinner fa-spin"></i> Analyzing live database...
    </div>
  `;
  log.scrollTop = log.scrollHeight;

  try {
    const res = await API.queryAIAssistant(query);
    const thinkingElem = document.getElementById(thinkingId);
    if (thinkingElem) {
      thinkingElem.innerHTML = `
        <strong style="color: var(--gold-dark);"><i class="fa-solid fa-crown"></i> AURA AI Engine (${res.mode}):</strong><br>
        ${marked.parse(res.response_markdown)}
      `;
    }
  } catch (err) {
    const thinkingElem = document.getElementById(thinkingId);
    if (thinkingElem) {
      thinkingElem.innerHTML = `<span style="color: red;">Error querying AI Assistant engine.</span>`;
    }
  }
  log.scrollTop = log.scrollHeight;
}

// -------------------------------------------------------------
// 7. REPORTS PDF & EXPORTS
// -------------------------------------------------------------
function initReportsTab() {
  const btnPDF = document.getElementById("btn-download-pdf-report");
  if (btnPDF) {
    btnPDF.addEventListener("click", async () => {
      try {
        const data = await API.getExecutiveReportData();
        const element = document.createElement("div");
        element.style.padding = "24px";
        element.style.fontFamily = "Outfit, sans-serif";
        element.innerHTML = `
          <h1 style="color: #D4AF37; font-family: Playfair Display, serif;">EXECUTIVE BUSINESS REPORT</h1>
          <p>Generated on ${data.generated_at}</p>
          <hr style="margin: 16px 0; border: 0; border-top: 1px solid #D4AF37;">
          
          <h3>Financial Performance</h3>
          <p>Gross Revenue: <strong>$${data.financials.total_revenue.toLocaleString()}</strong></p>
          <p>Net Operating Profit: <strong>$${data.financials.net_profit.toLocaleString()}</strong></p>
          <p>Profit Margin: <strong>${data.financials.profit_margin_pct}%</strong></p>
          
          <h3 style="margin-top: 20px;">Top VIP Accounts</h3>
          <ul>
            ${data.top_customers.map(c => `<li>${c.name} (${c.company}): $${c.spent.toLocaleString()}</li>`).join("")}
          </ul>

          <h3 style="margin-top: 20px;">AI Risk Highlights</h3>
          <ul>
            ${data.insights.map(i => `<li><strong>${i.title}</strong>: ${i.description}</li>`).join("")}
          </ul>
        `;

        html2pdf().from(element).save("Executive_Business_Summary_2026.pdf");
      } catch (err) {
        alert("Failed to generate PDF: " + err.message);
      }
    });
  }
}

// -------------------------------------------------------------
// 8. SETTINGS
// -------------------------------------------------------------
function initSettingsTab() {
  const saveBtn = document.getElementById("btn-save-api-key");
  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      const key = document.getElementById("setting-openai-key").value;
      try {
        await API.saveAPIKey(key);
        alert("OpenAI API Key settings updated!");
      } catch (err) {
        alert("Failed to save API Key: " + err.message);
      }
    });
  }
}

// -------------------------------------------------------------
// MODAL CONTROLS
// -------------------------------------------------------------
function initModals() {
  const btnAddProdModal = document.getElementById("btn-add-product-modal");
  if (btnAddProdModal) {
    btnAddProdModal.addEventListener("click", () => {
      document.getElementById("modal-add-product").classList.add("active");
    });
  }

  const btnAddCustModal = document.getElementById("btn-add-customer-modal");
  if (btnAddCustModal) {
    btnAddCustModal.addEventListener("click", () => {
      document.getElementById("modal-add-customer").classList.add("active");
    });
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("active");
}
