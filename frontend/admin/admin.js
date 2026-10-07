const hostname = window.location.hostname;
const isLocal = !hostname || hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.');
const API_URL = isLocal ? `http://${hostname || 'localhost'}:8000` : "";

let accessToken = localStorage.getItem("ecotrack_token");
let allReports = [];
let allCollectors = [];
let currentReportId = null;
let chartInstance = null;

const byId = (id) => document.getElementById(id);
const authHeaders = () => ({ Authorization: `Bearer ${accessToken}` });

document.addEventListener("DOMContentLoaded", async () => {
  if (!accessToken) {
    window.location.href = "../index.html";
    return;
  }

  // 1. Authenticate user
  try {
    const res = await fetch(`${API_URL}/auth/me`, { headers: authHeaders() });
    if (!res.ok) throw new Error("Unauthorized");
    const user = await res.json();
    
    if (user.role !== "administrator") {
      alert("Access Denied: You must be an administrator to view this page.");
      window.location.href = "../index.html";
      return;
    }
    
    byId("admin-name").textContent = user.name;
    const initials = user.name.substring(0, 2).toUpperCase();
    document.querySelector(".avatar").textContent = initials;
    
    byId("loader").style.opacity = '0';
    setTimeout(() => {
      byId("loader").style.display = 'none';
      byId("dashboard-layout").style.display = 'flex';
      initDashboard();
    }, 500);
    
  } catch (err) {
    localStorage.removeItem("ecotrack_token");
    window.location.href = "../index.html";
  }

  // 2. Setup Listeners
  setupNavigation();
  
  byId("logout-btn").onclick = () => {
    localStorage.removeItem("ecotrack_token");
    window.location.href = "../index.html";
  };
  
  byId("report-search").addEventListener("input", filterReports);
  byId("status-filter").addEventListener("change", filterReports);
});

function setupNavigation() {
  document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
      
      item.classList.add("active");
      const tabId = `tab-${item.dataset.tab}`;
      byId(tabId).classList.add("active");
      
      const text = item.textContent.trim();
      byId("page-title").textContent = text;
    });
  });
}

async function initDashboard() {
  await fetchAnalytics();
  await fetchReports();
  await fetchCollectors();
}

async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_URL}/analytics`, { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    
    byId("stat-total").textContent = data.total_reports || 0;
    byId("stat-pending").textContent = data.pending_reports || 0;
    byId("stat-collected").textContent = data.collected_reports || 0;
    
    const catCounts = data.category_counts || {};
    let aiTotal = 0;
    Object.values(catCounts).forEach(v => aiTotal += v);
    byId("stat-ai").textContent = aiTotal;
    
    renderChart(catCounts);
  } catch (e) {
    console.error("Failed to load analytics", e);
  }
}

function renderChart(catCounts) {
  const ctx = document.getElementById('categoryChart').getContext('2d');
  
  if (chartInstance) chartInstance.destroy();
  
  const labels = Object.keys(catCounts);
  const data = Object.values(catCounts);
  
  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        data: data.length ? data : [1],
        backgroundColor: [
          '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: '#6b7280' } }
      }
    }
  });
}

async function fetchReports() {
  try {
    const res = await fetch(`${API_URL}/reports`, { headers: authHeaders() });
    if (!res.ok) return;
    allReports = await res.json();
    
    allReports.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    populateRecentList();
    renderReportsTable(allReports);
  } catch (e) {
    console.error("Failed to load reports", e);
  }
}

async function fetchCollectors() {
  try {
    const res = await fetch(`${API_URL}/collectors`, { headers: authHeaders() });
    if (!res.ok) return;
    allCollectors = await res.json();
    
    const tbody = byId("collectors-tbody");
    tbody.innerHTML = "";
    
    const select = byId("collector-select");
    select.innerHTML = "";
    
    allCollectors.forEach(col => {
      // Table
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${col.name}</strong></td>
        <td>${col.email || "No Email"}</td>
        <td><span class="status-badge status-verified">Active</span></td>
      `;
      tbody.appendChild(tr);
      
      // Select option
      const opt = document.createElement("option");
      opt.value = col.user_id;
      opt.textContent = `${col.name} (${col.user_id})`;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error("Failed to load collectors", e);
  }
}

function populateRecentList() {
  const list = byId("recent-list");
  list.innerHTML = "";
  
  allReports.slice(0, 5).forEach(r => {
    const el = document.createElement("div");
    el.className = "recent-item";
    el.innerHTML = `
      <div>
        <div class="r-id">${r.report_id}</div>
        <div class="r-cat">${r.category || 'Unknown'}</div>
      </div>
      <div class="status-badge status-${r.status}">${r.status}</div>
    `;
    list.appendChild(el);
  });
}

function renderReportsTable(reportsToRender) {
  const tbody = byId("reports-tbody");
  tbody.innerHTML = "";
  
  reportsToRender.forEach(r => {
    const tr = document.createElement("tr");
    const dateStr = new Date(r.timestamp).toLocaleDateString();
    let actionHtml = `<button class="action-btn" onclick="viewDetails('${r.report_id}')">View</button>`;
    if (r.status === "ai_analyzed" || r.status === "reported") {
      actionHtml = `<button class="action-btn" onclick="openReviewModal('${r.report_id}')">Review</button>`;
    } else if (r.status === "reviewed") {
      actionHtml = `<button class="action-btn" onclick="openAssignModal('${r.report_id}')">Assign Task</button>`;
    } else if (r.status === "collected") {
      actionHtml = `<button class="action-btn" style="background:rgba(59,130,246,0.2); color:#3b82f6;" onclick="openVerifyModal('${r.report_id}')">Verify Proof</button>`;
    }
    
    tr.innerHTML = `
      <td><strong>${r.report_id.substring(0,8)}...</strong></td>
      <td>${r.category || '-'}</td>
      <td>${dateStr}</td>
      <td>${r.ai_result || '-'}</td>
      <td><span class="status-badge status-${r.status}">${r.status}</span></td>
      <td>${actionHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

function filterReports() {
  const term = byId("report-search").value.toLowerCase();
  const statusFilter = byId("status-filter").value;
  
  const filtered = allReports.filter(r => {
    const matchesTerm = r.report_id.toLowerCase().includes(term) || (r.category && r.category.toLowerCase().includes(term));
    const matchesStatus = statusFilter === "all" || r.status === statusFilter;
    return matchesTerm && matchesStatus;
  });
  
  renderReportsTable(filtered);
}

// Modals Logic
function openModal(id) {
  byId(id).classList.add('active');
}
function closeModal(id) {
  byId(id).classList.remove('active');
  currentReportId = null;
}

window.openReviewModal = (reportId) => {
  currentReportId = reportId;
  const report = allReports.find(r => r.report_id === reportId);
  
  byId("review-image").style.backgroundImage = `url('${API_URL}/reports/${reportId}/image')`;
  byId("review-cat").textContent = report.category || "N/A";
  byId("review-conf").textContent = report.ai_result || "N/A";
  byId("review-desc").textContent = report.description || "No description provided.";
  
  openModal('modal-review');
};

byId("btn-approve-report").onclick = async () => {
  if (!currentReportId) return;
  await updateReportStatus(currentReportId, "reviewed");
  closeModal('modal-review');
};
byId("btn-reject-report").onclick = async () => {
  if (!currentReportId) return;
  await updateReportStatus(currentReportId, "rejected");
  closeModal('modal-review');
};

window.openAssignModal = async (reportId) => {
  currentReportId = reportId;
  
  const report = allReports.find(r => r.report_id === reportId);
  if (report) {
    byId("assign-rep-desc").textContent = report.description || "N/A";
    byId("assign-rep-name").textContent = "Loading...";
    byId("assign-rep-email").textContent = "Loading...";
    
    fetch(`${API_URL}/users/${report.user_id}`, { headers: authHeaders() })
      .then(res => res.ok ? res.json() : null)
      .then(user => {
        if (user) {
          byId("assign-rep-name").textContent = user.name || "N/A";
          byId("assign-rep-email").textContent = user.email || "N/A";
        } else {
          byId("assign-rep-name").textContent = "Unknown";
          byId("assign-rep-email").textContent = "Unknown";
        }
      }).catch(() => {
        byId("assign-rep-name").textContent = "Error loading";
        byId("assign-rep-email").textContent = "Error loading";
      });
  }
  
  openModal('modal-assign');
};

byId("btn-confirm-assign").onclick = async () => {
  if (!currentReportId) return;
  const collectorId = byId("collector-select").value;
  if (!collectorId) return alert("Select a collector first");
  
  try {
    const res = await fetch(`${API_URL}/reports/${currentReportId}/assignment`, {
      method: "POST",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ collector_id: collectorId })
    });
    if (res.ok) {
      closeModal('modal-assign');
      initDashboard();
    }
  } catch (e) {
    console.error(e);
  }
};

window.openVerifyModal = async (reportId) => {
  currentReportId = reportId;
  byId("verify-before").style.backgroundImage = `url('${API_URL}/reports/${reportId}/image')`;
  byId("verify-after").style.backgroundImage = `url('${API_URL}/reports/${reportId}/evidence-image?t=${new Date().getTime()}')`;
  
  const report = allReports.find(r => r.report_id === reportId);
  if (report) {
    byId("verify-rep-desc").textContent = report.description || "N/A";
    byId("verify-rep-name").textContent = "Loading...";
    byId("verify-rep-email").textContent = "Loading...";
    
    fetch(`${API_URL}/users/${report.user_id}`, { headers: authHeaders() })
      .then(res => res.ok ? res.json() : null)
      .then(user => {
        if (user) {
          byId("verify-rep-name").textContent = user.name || "N/A";
          byId("verify-rep-email").textContent = user.email || "N/A";
        } else {
          byId("verify-rep-name").textContent = "Unknown";
          byId("verify-rep-email").textContent = "Unknown";
        }
      }).catch(() => {
        byId("verify-rep-name").textContent = "Error loading";
        byId("verify-rep-email").textContent = "Error loading";
      });
  }
  
  openModal('modal-verify');
};

byId("btn-approve-evidence").onclick = async () => {
  if (!currentReportId) return;
  try {
    const res = await fetch(`${API_URL}/reports/${currentReportId}/verify?approved=true`, {
      method: "POST",
      headers: authHeaders()
    });
    if (res.ok) {
      closeModal('modal-verify');
      initDashboard();
    } else {
      const errorData = await res.json();
      alert(errorData.detail || "Failed to verify evidence");
    }
  } catch (e) {
    console.error(e);
    alert("An error occurred");
  }
};

byId("btn-reject-evidence").onclick = async () => {
  if (!currentReportId) return;
  try {
    const res = await fetch(`${API_URL}/reports/${currentReportId}/verify?approved=false`, {
      method: "POST",
      headers: authHeaders()
    });
    if (res.ok) {
      closeModal('modal-verify');
      initDashboard();
    } else {
      const errorData = await res.json();
      alert(errorData.detail || "Failed to reject evidence");
    }
  } catch (e) {
    console.error(e);
    alert("An error occurred");
  }
};

async function updateReportStatus(id, newStatus) {
  try {
    const res = await fetch(`${API_URL}/reports/${id}/status`, {
      method: "PATCH",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      initDashboard(); // Refresh all
    }
  } catch (e) {
    console.error(e);
  }
}

window.viewDetails = async (reportId) => {
  const report = allReports.find(r => r.report_id === reportId);
  if (!report) return;
  
  byId("view-desc").textContent = report.description || "No description provided.";
  byId("view-image-before").style.backgroundImage = `url('${API_URL}/reports/${reportId}/image')`;
  
  byId("view-name").textContent = "Loading...";
  byId("view-email").textContent = "Loading...";
  byId("view-role").textContent = "Loading...";
  
  const collectorSection = byId("view-collector-section");
  if (report.collector_id) {
    collectorSection.style.display = "block";
    byId("view-collector-name").textContent = "Loading...";
    byId("view-collector-email").textContent = "Loading...";
    
    // Fetch collector details
    fetch(`${API_URL}/users/${report.collector_id}`, { headers: authHeaders() })
      .then(res => res.ok ? res.json() : null)
      .then(col => {
        if (col) {
          byId("view-collector-name").textContent = col.name || "N/A";
          byId("view-collector-email").textContent = col.email || "N/A";
        } else {
          byId("view-collector-name").textContent = "Unknown";
          byId("view-collector-email").textContent = "Unknown";
        }
      }).catch(() => {
        byId("view-collector-name").textContent = "Error";
        byId("view-collector-email").textContent = "Error";
      });
  } else {
    collectorSection.style.display = "none";
  }
  
  openModal('modal-view-details');
  
  try {
    const res = await fetch(`${API_URL}/users/${report.user_id}`, {
      headers: authHeaders()
    });
    if (res.ok) {
      const user = await res.json();
      byId("view-name").textContent = user.name || "N/A";
      byId("view-email").textContent = user.email || "N/A";
      byId("view-role").textContent = user.role || "N/A";
    } else {
      byId("view-name").textContent = "Unknown User";
      byId("view-email").textContent = "Unknown Email";
      byId("view-role").textContent = "Unknown Role";
    }
  } catch (e) {
    console.error(e);
  }
};
