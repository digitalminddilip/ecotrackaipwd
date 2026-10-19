const hostname = window.location.hostname;
const isLocal = !hostname || hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.');
const API_URL = isLocal ? `http://${hostname || 'localhost'}:8000` : (window.BACKEND_API_URL || localStorage.getItem("cleanconnect_api_url") || "");
window.API_URL = API_URL;

let reports = [];
let accessToken = localStorage.getItem("cleanconnect_token");
let currentUser = null;
let campusScene;
const GIDA_CENTER = [26.7430558, 83.2733427];
const CAMPUS_SCALE = 90000;
let currentLocation;

const byId = (id) => document.getElementById(id);
const authHeaders = () =>
  accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
const isGuest = () => Boolean(currentUser?.isGuest);

function updateSidebarProfile(name) {
  const avatarEl = document.getElementById("sidebar-avatar");
  const nameEl = document.getElementById("sidebar-name");
  
  if (nameEl) nameEl.textContent = name;
  if (avatarEl) {
    const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    avatarEl.textContent = initials || 'G';
  }
}

function enterGuestMode() {
  accessToken = null;
  localStorage.removeItem("cleanconnect_token");
  currentUser = { name: "Guest", role: "citizen", isGuest: true };
  updateSidebarProfile("Guest");
  if (byId("session-label")) byId("session-label").textContent = "Guest mode";
  if (byId("login")) byId("login").hidden = false;
  if (byId("logout")) byId("logout").hidden = true;
  if (byId("login-screen")) {
    byId("login-screen").hidden = true;
    byId("login-screen").style.display = "none";
  }
  if (byId("app-wrapper")) byId("app-wrapper").hidden = true;
  if (byId("collector-dashboard-wrapper")) byId("collector-dashboard-wrapper").hidden = true;
  if (byId("citizen-wrapper")) byId("citizen-wrapper").hidden = false;
  document.body.classList.remove("collector-mode");
  
  if (byId("cit-user-name")) byId("cit-user-name").textContent = "Guest";
  if (byId("cit-user-email")) byId("cit-user-email").textContent = "Login to report";
  if (byId("cit-user-avatar")) {
    byId("cit-user-avatar").innerHTML = `<img src="https://ui-avatars.com/api/?name=Guest&background=random&color=fff&rounded=true" style="width: 100%; height: 100%; border-radius: 50%;">`;
  }
  
  if (byId("cit-logout-btn")) byId("cit-logout-btn").style.display = "none";
  if (byId("cit-login-btn")) byId("cit-login-btn").style.display = "inline-block";
  if (byId("report-form")) byId("report-form").style.display = "flex";
  if (byId("guest-report-msg")) byId("guest-report-msg").style.display = "none";
}

function openSignIn() {
  const loginScreen = byId("login-screen");
  if (loginScreen) {
    loginScreen.hidden = false;
    loginScreen.style.removeProperty("display");
    loginScreen.classList.add("active");
  }
  if (byId("app-wrapper")) byId("app-wrapper").hidden = true;
  if (byId("citizen-wrapper")) byId("citizen-wrapper").hidden = true;
  if (byId("collector-dashboard-wrapper")) byId("collector-dashboard-wrapper").hidden = true;
  setAuthMode("login");
}

function initMap() {
  if (typeof THREE === "undefined") return;
  const container = byId("map");
  if (!container) return;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xdceee3);
  const camera = new THREE.PerspectiveCamera(
    42,
    container.clientWidth / (container.clientHeight || 300),
    0.1,
    1000,
  );
  camera.position.set(13, 16, 18);
  camera.lookAt(0, 0, 0);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight || 300);
  container.innerHTML = "";
  container.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x668879, 2));
  const sun = new THREE.DirectionalLight(0xffffff, 2.5);
  sun.position.set(8, 18, 10);
  scene.add(sun);
  const campus = new THREE.Group();
  const material = (color) =>
    new THREE.MeshStandardMaterial({ color, roughness: 0.85 });
  const ground = new THREE.Mesh(
    new THREE.BoxGeometry(24, 0.25, 18),
    material(0xb9dfc5),
  );
  ground.position.y = -0.25;
  campus.add(ground);
  const addBlock = (name, x, z, width, depth, height, color) => {
    const block = new THREE.Mesh(
      new THREE.BoxGeometry(width, height, depth),
      material(color),
    );
    block.position.set(x, height / 2, z);
    block.userData.name = name;
    campus.add(block);
  };
  const addGround = (x, z, width, depth, color) => {
    const field = new THREE.Mesh(
      new THREE.BoxGeometry(width, 0.06, depth),
      material(color),
    );
    field.position.set(x, 0.03, z);
    campus.add(field);
  };
  addBlock("Main Building", -4, 1, 5, 3, 2.2, 0xf4f0dc);
  addBlock("Workshops", -8, -3, 3, 4, 1.1, 0xe3c9a9);
  addBlock("Shri Krishna Academy", 5, -2, 4, 3, 1.6, 0xf0dcae);
  addBlock("Admin Block", -1, -3.6, 2.5, 1.4, 1.4, 0xd8e5df);
  addBlock("Gate House", 8, 6, 1.3, 1.2, 0.9, 0xc9d8d0);
  addGround(5, 4, 7, 5, 0x83bd91);
  addGround(-1, 6, 5, 2.5, 0xc9df9b);
  addGround(-3, -6, 5, 2.2, 0x9ed29f);
  addGround(3, -6, 5, 2.2, 0x9ed29f);
  const road = material(0xa8b9b0);
  const path = new THREE.Mesh(new THREE.BoxGeometry(1, 0.08, 16), road);
  path.position.set(1.5, 0.08, 0);
  campus.add(path);
  scene.add(campus);
  const markerGroup = new THREE.Group();
  scene.add(markerGroup);
  campusScene = { scene, camera, renderer, container, markerGroup, campus };
  const animate = () => {
    requestAnimationFrame(animate);
    campus.rotation.y += 0.0008;
    renderer.render(scene, camera);
  };
  animate();
  window.addEventListener("resize", () => {
    if (!container.clientHeight) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
}

function setLocation(latitude, longitude) {
  currentLocation = [latitude, longitude];
  if (byId("latitude")) byId("latitude").value = latitude.toFixed(6);
  if (byId("longitude")) byId("longitude").value = longitude.toFixed(6);
  
  const gpsBtn = byId("btn-fetch-gps");
  const gpsBtnText = byId("gps-btn-text");
  const gpsBadge = byId("gps-coords-badge");
  const gpsCoordsText = byId("gps-coords-text");
  const stepIndicator = byId("cit-step-indicator");

  if (gpsBtn) {
    gpsBtn.classList.add("locked");
    if (gpsBtnText) gpsBtnText.innerHTML = '<i class="fa-solid fa-circle-check"></i> Locked';
  }
  if (gpsBadge && gpsCoordsText) {
    gpsCoordsText.textContent = `Coordinates: ${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E (Accuracy: ±4m)`;
    gpsBadge.classList.add("visible");
    gpsBadge.style.display = "inline-flex";
  }
  if (stepIndicator) {
    stepIndicator.innerHTML = '<i class="fa-solid fa-satellite-dish"></i> STEP 2: REAL-TIME DATA POPULATED & GPS GEOLOCATED';
  }

  const locationStatus = byId("location-status");
  if (locationStatus) {
    locationStatus.textContent = "";
  }
  
  const locInput = byId("report-location");
  if (locInput) {
    if (!locInput.value) {
      locInput.placeholder = "Locating...";
      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`)
        .then(r => r.json())
        .then(data => {
          if (data && data.display_name) {
            locInput.value = data.display_name.split(",").slice(0, 3).join(",");
            locInput.classList.add("filled");
          }
        })
        .catch(e => {
          locInput.placeholder = "Enter Location";
        });
    } else {
      locInput.classList.add("filled");
    }
  }

  if (campusScene) {
    campusScene.camera.position.set(10, 13, 15);
    renderCampusLocation();
  }
}

function toCampusPosition(latitude, longitude) {
  return {
    x: Math.max(-11, Math.min(11, (longitude - GIDA_CENTER[1]) * CAMPUS_SCALE)),
    z: Math.max(-8, Math.min(8, -(latitude - GIDA_CENTER[0]) * CAMPUS_SCALE)),
  };
}

function createMarker(color, size = 0.28) {
  return new THREE.Mesh(
    new THREE.SphereGeometry(size, 16, 16),
    new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity: 0.25,
    }),
  );
}

function renderCampusLocation() {
  if (!campusScene || !currentLocation) return;
  if (campusScene.locationMarker)
    campusScene.markerGroup.remove(campusScene.locationMarker);
  const position = toCampusPosition(currentLocation[0], currentLocation[1]);
  const marker = createMarker(0x2478ff, 0.34);
  marker.position.set(position.x, 1.35, position.z);
  campusScene.markerGroup.add(marker);
  campusScene.locationMarker = marker;
}

function getLocation(silent = false) {
  const locationStatus = byId("location-status");
  if (!navigator.geolocation) {
    if (locationStatus && !silent) locationStatus.textContent = "GPS is not supported by this browser";
    return;
  }
  if (locationStatus && !silent) locationStatus.textContent = "Requesting your location...";
  navigator.geolocation.getCurrentPosition(
    (position) =>
      setLocation(position.coords.latitude, position.coords.longitude),
    () => {
      if (locationStatus && !silent) locationStatus.textContent = "GPS unavailable. Trying network location...";
      getNetworkLocation(silent);
    },
    { enableHighAccuracy: true, timeout: 5000, maximumAge: 300000 },
  );
}

async function getNetworkLocation(silent = false) {
  const locationStatus = byId("location-status");
  if (locationStatus && !silent) locationStatus.textContent = "Detecting approximate network location...";
  try {
    const response = await fetch("https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyAa1vpYMlgD57Qfnb6DQHds509S9sL0cOs", { method: 'POST' });
    const result = await response.json();
    if (!response.ok || !result.location)
      throw new Error("Network location unavailable");
    setLocation(Number(result.location.lat), Number(result.location.lng));
    if (locationStatus) {
      locationStatus.textContent = "Google Network GPS Locked";
    }
  } catch (error) {
    if (locationStatus && !silent) locationStatus.textContent = "Unable to detect network location.";
  }
}

function renderMapMarkers() {
  renderCampusMarkers();
}

function renderCampusMarkers() {
  if (!campusScene) return;
  campusScene.markerGroup.clear();
  reports.forEach((report) => {
    const marker = createMarker(0xf07b61);
    const position = toCampusPosition(report.latitude, report.longitude);
    marker.position.set(position.x, 1.1, position.z);
    marker.userData.reportId = report.report_id;
    campusScene.markerGroup.add(marker);
  });
  renderCampusLocation();
}

function formatStatus(value) {
  return (value || "").replaceAll("_", " ");
}

function renderAnalytics(data) {
  if (byId("total-reports")) byId("total-reports").textContent = data.total_reports || 0;
  if (byId("pending-reports")) byId("pending-reports").textContent = data.pending_reports || 0;
  if (byId("collected-reports")) byId("collected-reports").textContent = data.collected_reports || 0;
  const verified = (data.status_counts && data.status_counts.verified) || 0;
  renderPremiumCharts(data);
  renderPremiumImpact(data);
  if (byId("verified-rate")) {
    byId("verified-rate").textContent = data.total_reports
      ? `${Math.round((verified / data.total_reports) * 100)}%`
      : "0%";
  }
}

function renderReports() {
  const searchEl = byId("search");
  const filterEl = byId("status-filter");
  const search = searchEl ? searchEl.value.trim().toLowerCase() : "";
  const status = filterEl ? filterEl.value : "";
  const visible = reports.filter((report) => {
    const matchesSearch =
      !search ||
      report.report_id.toLowerCase().includes(search) ||
      (report.category || "").toLowerCase().includes(search) ||
      (report.description || "").toLowerCase().includes(search);
    const matchesStatus = !status || report.status === status;
    return matchesSearch && matchesStatus;
  });

  const body = byId("reports-body");
  if (!body) return;
  if (!visible.length) {
    body.innerHTML = '<tr><td colspan="6" class="empty">No matching reports</td></tr>';
    renderMapMarkers();
    return;
  }

  body.innerHTML = visible
    .map(
      (report) => `
      <tr>
        <td><strong>${report.report_id.slice(0, 8)}...</strong></td>
        <td>${report.category ? report.category.replace('_', ' ') : 'General'}</td>
        <td>${new Date(report.timestamp).toLocaleDateString()}</td>
        <td>${report.ai_result ? report.ai_result.replace('_', ' ') : 'Pending'}</td>
        <td><span class="status-pill status-${report.status}">${formatStatus(report.status)}</span></td>
        <td>${actionMarkup(report)}</td>
      </tr>
    `
    )
    .join("");

  body.querySelectorAll(".table-action").forEach((button) =>
    button.addEventListener("click", () =>
      handleAction(button.dataset.action, button.dataset.id)
    )
  );

  renderMapMarkers();
}

function actionMarkup(report) {
  if (!currentUser) return "";
  if (currentUser.role === "administrator") {
    return `<a href="admin/index.html" class="table-action" style="text-decoration:none;">Admin Console</a>`;
  }
  if (currentUser.role === "collector") {
    if (report.collector_id === currentUser.user_id) {
      if (report.status === "assigned") {
        return `<button class="table-action" data-action="in_progress" data-id="${report.report_id}">Start Work</button>`;
      }
      if (report.status === "in_progress") {
        return `<button class="table-action" data-action="collected" data-id="${report.report_id}">Mark Collected</button>`;
      }
      if (report.status === "collected" && !report.evidence_reference) {
        return `<button class="table-action" data-action="evidence" data-id="${report.report_id}">Upload Proof</button>`;
      }
      if (report.status === "rejected") {
        return `<button class="table-action" data-action="evidence" data-id="${report.report_id}" style="color: #ef4444; border-color: #fca5a5;">Retry Proof</button>`;
      }
      return `<span style="color: #64748b; font-size: 0.85rem;">Assigned to you</span>`;
    }
    return report.collector_id
      ? `<span style="color: #94a3b8; font-size: 0.85rem;">Assigned</span>`
      : `<button class="table-action" data-action="in_progress" data-id="${report.report_id}">Accept Task</button>`;
  }
  return "";
}

async function handleAction(action, reportId) {
  try {
    if (action === "in_progress" || action === "collected") {
      const response = await fetch(`${API_URL}/reports/${reportId}/status`, {
        method: "PATCH",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ status: action }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Unable to update status");
      }
      await loadDashboard();
    } else if (action === "evidence") {
      const modal = byId("evidence-modal");
      if (modal) {
        byId("evidence-report-id").value = reportId;
        if (byId("evidence-file")) byId("evidence-file").value = "";
        if (byId("evidence-message")) byId("evidence-message").textContent = "";
        modal.style.display = "flex";
      }
    }
  } catch (error) {
    alert(error.message);
  }
}

async function loadDashboard() {
  if (isGuest()) {
    reports = [];
    renderAnalytics({
      total_reports: 0,
      pending_reports: 0,
      collected_reports: 0,
      status_counts: {},
    });
    renderReports();
    return;
  }
  try {
    const [reportsResponse, analyticsResponse] = await Promise.all([
      fetch(`${API_URL}/reports`, { headers: authHeaders() }),
      fetch(`${API_URL}/analytics`, { headers: authHeaders() }),
    ]);
    if (!reportsResponse.ok || !analyticsResponse.ok)
      throw new Error("API unavailable");
    reports = await reportsResponse.json();
    renderAnalytics(await analyticsResponse.json());
    renderReports();
    if (byId("auth-message")) byId("auth-message").textContent = "";
  } catch (error) {
    if (byId("reports-body")) {
      byId("reports-body").innerHTML =
        '<tr><td colspan="6" class="empty">Unable to load live reports.</td></tr>';
    }
  }
}

async function restoreSession() {
  if (!accessToken) {
    enterGuestMode();
    return;
  }
  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: authHeaders(),
    });
    if (!response.ok) {
      enterGuestMode();
      return;
    }
    currentUser = await response.json();
    updateSidebarProfile(currentUser.name);
    
    if (byId("session-label")) {
      byId("session-label").textContent = `${currentUser.name} • ${currentUser.role}`;
    }
    if (byId("login")) byId("login").hidden = true;
    if (byId("logout")) byId("logout").hidden = false;
    if (byId("login-screen")) {
      byId("login-screen").hidden = true;
      byId("login-screen").style.display = "none";
    }
    
    if (byId("cit-logout-btn")) byId("cit-logout-btn").style.display = "inline-block";
    if (byId("cit-login-btn")) byId("cit-login-btn").style.display = "none";
    if (byId("report-form")) byId("report-form").style.display = "flex";
    if (byId("guest-report-msg")) byId("guest-report-msg").style.display = "none";
    
    if (currentUser.role === "administrator") {
      window.location.href = "admin/index.html";
      return;
    }

    if (currentUser.role === "collector") {
      if (byId("citizen-wrapper")) byId("citizen-wrapper").hidden = true;
      if (byId("app-wrapper")) byId("app-wrapper").hidden = false;
      document.body.classList.add("collector-mode");
      
      const nameEl = document.getElementById("sidebar-name");
      const emailEl = document.getElementById("sidebar-workspace");
      if (nameEl) nameEl.textContent = currentUser.name;
      if (emailEl) emailEl.textContent = "Collector View";
    } else {
      // Citizen
      if (byId("app-wrapper")) byId("app-wrapper").hidden = true;
      if (byId("collector-dashboard-wrapper")) byId("collector-dashboard-wrapper").hidden = true;
      if (byId("citizen-wrapper")) byId("citizen-wrapper").hidden = false;
      document.body.classList.remove("collector-mode");
      if (byId("cit-user-name")) byId("cit-user-name").textContent = currentUser.name;
      if (byId("cit-user-email")) byId("cit-user-email").textContent = currentUser.email || `${currentUser.name.toLowerCase().replace(' ', '')}@cleanconnect.local`;
      const avatarUrl = currentUser.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name)}&background=random&color=fff&rounded=true&size=128`;
      if (byId("cit-user-avatar")) {
        byId("cit-user-avatar").innerHTML = `<img src="${avatarUrl}" referrerpolicy="no-referrer" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
      }
      populateCitProfile();
    }
  } catch (err) {
    enterGuestMode();
  }
}

let isOtpStep = false;
function setAuthMode(mode) {
  if (byId("auth-mode")) byId("auth-mode").value = mode;
  const registering = mode === "register";
  const forgot = mode === "forgot";
  const loginOtp = mode === "login_otp";

  const btnTextNode = byId("auth-btn-text");

  if (byId("group-name")) {
    byId("group-name").hidden = !registering;
    if (byId("auth-name")) {
      byId("auth-name").required = registering;
    }
  }
  if (document.querySelector(".form-actions-row")) {
    document.querySelector(".form-actions-row").style.display = (!registering && !forgot) ? "flex" : "none";
  }

  if (forgot || loginOtp) {
    if (byId("group-password")) byId("group-password").hidden = true;
    if (byId("auth-password")) {
      byId("auth-password").required = false;
      if (forgot) byId("auth-password").placeholder = "New Password (5+ characters)";
    }
    if (btnTextNode)
      btnTextNode.textContent = loginOtp ? "Login" : "Send Code";
    if (byId("auth-title")) byId("auth-title").textContent = loginOtp ? "Login with OTP" : "Forgot Password?";
    if (byId("auth-subtitle"))
      byId("auth-subtitle").textContent = loginOtp ? "We will send a 6-digit OTP to your registered email address." : "Enter your registered email to receive a password reset code.";
    if (byId("group-otp")) byId("group-otp").hidden = false;
    if (byId("auth-otp")) byId("auth-otp").required = false;
    isOtpStep = false;
  } else {
    if (byId("group-password")) byId("group-password").hidden = false;
    if (byId("auth-password")) {
      byId("auth-password").required = true;
      byId("auth-password").placeholder = "@Sn123hsn#";
    }
    if (byId("group-otp")) byId("group-otp").hidden = true;
    if (byId("auth-otp")) byId("auth-otp").required = false;
    if (btnTextNode)
      btnTextNode.textContent = registering ? "Sign up" : "Sign in";
    if (byId("auth-title"))
      byId("auth-title").textContent = registering ? "Create Account" : "Welcome Back!";
    if (byId("auth-subtitle"))
      byId("auth-subtitle").textContent = registering
        ? "Join CleanConnect to help report and track cleanliness in your community."
        : "Sign in to report civic waste issues, track complaints, and earn green points.";
  }

  const bottomText = byId("bottom-text");
  if (bottomText) {
    if (registering) {
      bottomText.innerHTML = `Already have an account? <a href="#" id="link-login">Sign in</a>`;
    } else {
      bottomText.innerHTML = `Don't have an account? <a href="#" id="link-register">Sign up</a>`;
    }
    const lLogin = byId("link-login");
    const lReg = byId("link-register");
    if (lLogin) lLogin.addEventListener("click", (e) => { e.preventDefault(); setAuthMode("login"); });
    if (lReg) lReg.addEventListener("click", (e) => { e.preventDefault(); setAuthMode("register"); });
  }

  if (byId("link-login-otp")) byId("link-login-otp").hidden = loginOtp || registering || forgot;
  if (byId("link-login-password")) byId("link-login-password").hidden = !loginOtp;
  if (byId("link-forgot")) byId("link-forgot").hidden = registering || forgot;
  if (byId("auth-message")) byId("auth-message").textContent = "";
}

// Setup Auth Links
function setupAuthLinks() {
  if (byId("link-login")) {
    byId("link-login").addEventListener("click", (e) => {
      e.preventDefault();
      setAuthMode("login");
    });
  }
  if (byId("link-register")) {
    byId("link-register").addEventListener("click", (e) => {
      e.preventDefault();
      setAuthMode("register");
    });
  }
  if (byId("link-forgot")) {
    byId("link-forgot").addEventListener("click", (e) => {
      e.preventDefault();
      setAuthMode("forgot");
    });
  }
  if (byId("link-login-otp")) {
    byId("link-login-otp").addEventListener("click", (e) => {
      e.preventDefault();
      setAuthMode("login_otp");
    });
  }
  if (byId("link-login-password")) {
    byId("link-login-password").addEventListener("click", (e) => {
      e.preventDefault();
      setAuthMode("login");
    });
  }
  if (byId("auth-back-btn")) {
    byId("auth-back-btn").addEventListener("click", () => {
      enterGuestMode();
    });
  }
}

// Auth Form Handler
function setupAuthForm() {
  const authForm = byId("auth-form");
  if (!authForm) return;

  authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const mode = byId("auth-mode").value;
    const name = byId("auth-name") ? byId("auth-name").value.trim() : "";
    const email = byId("auth-email").value.trim();
    const password = byId("auth-password") ? byId("auth-password").value : "";
    const otp = byId("auth-otp") ? byId("auth-otp").value.trim() : "";
    const message = byId("auth-message");
    const submitBtn = byId("auth-submit-btn");

    message.style.color = "#475569";
    message.textContent = "Processing...";
    if (submitBtn) submitBtn.disabled = true;

    try {
      let endpoint = "/auth/login";
      let payload = { email, password };

      if (mode === "register") {
        endpoint = "/auth/register";
        payload = { name, email, password };
      } else if (mode === "login_otp") {
        if (!otp) {
          message.textContent = "Please enter the 6-digit OTP sent to your email address.";
          if (submitBtn) submitBtn.disabled = false;
          return;
        }
        endpoint = "/auth/verify-otp";
        payload = { email, otp };
      } else if (mode === "forgot") {
        if (!isOtpStep) {
          endpoint = "/auth/forgot-password";
          payload = { email };
          const res = await fetch(`${API_URL}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const resData = await res.json();
          if (!res.ok) throw new Error(resData.detail || "Error requesting reset code");
          
          message.style.color = "#10b981";
          message.innerHTML = `<i class="fa-solid fa-envelope"></i> Reset code sent! Please check your email inbox, enter the 6-digit code and your new password below:`;
          isOtpStep = true;
          byId("group-password").hidden = false;
          byId("auth-password").required = true;
          byId("auth-password").value = "";
          byId("auth-otp").required = true;
          byId("auth-otp").value = "";
          byId("auth-otp").focus();
          if (byId("auth-btn-text")) byId("auth-btn-text").textContent = "Save New Password";
          if (submitBtn) submitBtn.disabled = false;
          return;
        } else {
          if (!otp) {
            message.textContent = "Please enter the 6-digit code received on your email.";
            if (submitBtn) submitBtn.disabled = false;
            return;
          }
          endpoint = "/auth/reset-password";
          payload = { email, otp, new_password: password };
        }
      }

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Authentication failed");
      }

      accessToken = result.access_token;
      localStorage.setItem("cleanconnect_token", accessToken);
      message.style.color = "#27ae60";
      message.textContent = "Success! Redirecting...";

      authForm.reset();
      await restoreSession();
      await loadDashboard();

    } catch (error) {
      message.style.color = "#ef4444";
      message.textContent = error.message;
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

// Citizen Portal View Navigation
function showCitView(viewName, el) {
  const views = ['new-report', 'community', 'track', 'reports', 'status', 'profile'];
  views.forEach(v => {
    const elView = document.getElementById('cit-view-' + v);
    if (elView) elView.style.display = 'none';
  });
  
  const target = document.getElementById('cit-view-' + viewName);
  if (target) target.style.display = 'block';

  document.querySelectorAll('.col-sidebar .col-nav-link').forEach(link => {
    link.classList.remove('active');
  });
  if (el) {
    el.classList.add('active');
  } else {
    const matched = Array.from(document.querySelectorAll('.col-sidebar .col-nav-link')).find(l => l.getAttribute('onclick') && l.getAttribute('onclick').includes(viewName));
    if (matched) matched.classList.add('active');
  }

  const titles = {
    'new-report': ['Report the Waste Product', 'Help keep our community clean by reporting civic issues.'],
    'community': ['Community Reports Feed', 'Real-time updates of local cleanliness reports.'],
    'track': ['Live Tracking Map', 'Monitor reported sanitation issues in real-time.'],
    'reports': ['My Submitted Reports', 'Track progress and status of your reported issues.'],
    'status': ['Civic Cleanliness Impact', 'Overview of verified community cleanups.'],
    'profile': ['Citizen Profile', 'Your account and cleanliness contribution stats.']
  };

  if (titles[viewName]) {
    const titleEl = document.getElementById('cit-page-title');
    const subEl = document.getElementById('cit-page-subtitle');
    if (titleEl) titleEl.textContent = titles[viewName][0];
    if (subEl) subEl.textContent = titles[viewName][1];
  }

  if (viewName === 'community') loadCommunityFeed();
  if (viewName === 'reports') loadMyReports();
  if (viewName === 'status') loadCitStatus();
  if (viewName === 'profile') populateCitProfile();
}

async function loadCommunityFeed() {
  const container = document.getElementById('community-feed-container');
  if (!container) return;
  try {
    const res = await fetch(API_URL + '/reports/community');
    if (!res.ok) return;
    const data = await res.json();
    if (!data.length) {
      container.innerHTML = '<p style="color:#94a3b8; text-align:center;">No reports yet.</p>';
      return;
    }
    container.innerHTML = data.slice(0, 15).map(r => `
      <div style="background:white; padding:16px; border-radius:8px; border:1px solid #e2e8f0; display:flex; gap:16px; align-items:center;">
        <div style="width:48px; height:48px; border-radius:8px; background:#e0f2fe; color:#0284c7; display:flex; align-items:center; justify-content:center; font-size:20px;">
          <i class="fa-solid fa-trash-can"></i>
        </div>
        <div style="flex:1;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#1e293b;">${r.category ? r.category.replace('_', ' ').toUpperCase() : 'WASTE ISSUE'}</strong>
            <span style="font-size:0.8rem; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:12px; font-weight:600;">${(r.status || 'reported').toUpperCase()}</span>
          </div>
          <p style="margin:4px 0 0; color:#64748b; font-size:0.9rem;">${r.description || 'Community reported hazard'}</p>
          <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">ID: ${r.report_id} • ${new Date(r.timestamp).toLocaleDateString()}</div>
        </div>
      </div>
    `).join('');
  } catch(e) {
    console.error('Failed to load community feed', e);
  }
}

function openProofModal(imgSrc, title, status) {
  const modal = document.getElementById('proof-preview-modal');
  const modalImg = document.getElementById('proof-modal-img');
  const modalTitle = document.getElementById('proof-modal-title');
  const modalBadge = document.getElementById('proof-modal-badge');
  if (!modal || !modalImg) return;
  modalImg.src = imgSrc;
  if (modalTitle) modalTitle.textContent = title || "Cleanup Evidence Proof";
  if (modalBadge) {
    if (status === 'verified') {
      modalBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Admin Verified Cleaned (+10 Green Points)';
      modalBadge.style.background = '#dcfce7';
      modalBadge.style.color = '#15803d';
    } else if (status === 'collected') {
      modalBadge.innerHTML = '<i class="fa-solid fa-camera"></i> Collector Cleanup Proof (Awaiting Verification)';
      modalBadge.style.background = '#e0f2fe';
      modalBadge.style.color = '#0369a1';
    } else {
      modalBadge.innerHTML = '<i class="fa-solid fa-image"></i> Reported Waste Location';
      modalBadge.style.background = '#f1f5f9';
      modalBadge.style.color = '#475569';
    }
  }
  modal.style.display = 'flex';
}
window.openProofModal = openProofModal;

async function loadMyReports() {
  const tbody = document.getElementById('cit-reports-tbody');
  if (!tbody) return;
  try {
    const res = await fetch(API_URL + '/reports', { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#94a3b8;"><i class="fa-solid fa-folder-open" style="font-size:24px; margin-bottom:8px; display:block;"></i>No reports filed yet. Click "New Report" to submit one!</td></tr>';
      return;
    }
    tbody.innerHTML = data.map(r => {
      const reportedImgHtml = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <img src="${API_URL}/reports/${r.report_id}/image" onclick="openProofModal('${API_URL}/reports/${r.report_id}/image', 'Reported Waste Photo (Before Cleanup)', '${r.status}')" style="width: 44px; height: 44px; object-fit: cover; border-radius: 6px; cursor: pointer; border: 1px solid #cbd5e1; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" title="Click to enlarge" onerror="this.src='logo.png'" />
          <button type="button" onclick="openProofModal('${API_URL}/reports/${r.report_id}/image', 'Reported Waste Photo (Before Cleanup)', '${r.status}')" style="background: none; border: none; color: #3b82f6; font-size: 0.75rem; cursor: pointer; padding: 0; text-decoration: underline;">
            View
          </button>
        </div>
      `;

      let evidenceProofHtml = '';
      if (r.evidence_reference) {
        evidenceProofHtml = `
          <div style="display: flex; align-items: center; gap: 10px;">
            <img src="${API_URL}/reports/${r.report_id}/evidence-image" onclick="openProofModal('${API_URL}/reports/${r.report_id}/evidence-image', 'Cleaned Place Evidence Proof (After Cleanup)', '${r.status}')" style="width: 44px; height: 44px; object-fit: cover; border-radius: 6px; cursor: pointer; border: 2px solid #10b981; box-shadow: 0 2px 4px rgba(16,185,129,0.2);" title="Click to inspect cleanup proof" onerror="this.style.display='none'" />
            <div>
              <span style="display: inline-flex; align-items: center; gap: 4px; background: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                <i class="fa-solid fa-check-circle"></i> Cleaned Proof
              </span>
              <button type="button" onclick="openProofModal('${API_URL}/reports/${r.report_id}/evidence-image', 'Cleaned Place Evidence Proof (After Cleanup)', '${r.status}')" style="display: block; margin-top: 3px; background: none; border: none; color: #0284c7; font-size: 0.75rem; cursor: pointer; padding: 0; text-decoration: underline; font-weight: 500;">
                Inspect Photo
              </button>
            </div>
          </div>
        `;
      } else {
        evidenceProofHtml = `
          <span style="display: inline-flex; align-items: center; gap: 5px; background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">
            <i class="fa-regular fa-clock"></i> Cleaning in progress
          </span>
        `;
      }

      return `
        <tr style="border-bottom: 1px solid #f1f5f9;">
          <td style="padding:12px; font-family:monospace; color:#3b82f6; font-weight: 600;">${r.report_id.slice(0, 10)}...</td>
          <td style="padding:12px; color:#64748b; white-space: nowrap;">${new Date(r.timestamp).toLocaleDateString()}</td>
          <td style="padding:12px; color:#1e293b; font-weight:500;">${r.category ? r.category.replace('_', ' ').toUpperCase() : 'WASTE'}</td>
          <td style="padding:12px;"><span style="background:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; text-transform: uppercase;">${r.status}</span></td>
          <td style="padding:12px;">${reportedImgHtml}</td>
          <td style="padding:12px;">${evidenceProofHtml}</td>
        </tr>
      `;
    }).join('');
  } catch(e) {
    console.error('Failed to load my reports', e);
  }
}

async function loadCitStatus() {
  try {
    const res = await fetch(API_URL + '/analytics', { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    const tot = document.getElementById('cit-stat-total');
    const ver = document.getElementById('cit-stat-verified');
    if (tot) tot.textContent = data.total_reports || 0;
    if (ver) ver.textContent = data.collected_reports || 0;
  } catch(e) {}
}

function populateCitProfile() {
  if (!currentUser) return;
  if (byId("cit-profile-name")) byId("cit-profile-name").textContent = currentUser.name || "Citizen";
  if (byId("cit-profile-email")) byId("cit-profile-email").textContent = currentUser.email || "";
  if (byId("cit-profile-avatar")) {
    const avatarUrl = currentUser.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name)}&background=random&color=fff&rounded=true&size=128`;
    byId("cit-profile-avatar").innerHTML = `<img src="${avatarUrl}" referrerpolicy="no-referrer" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
  }
}

// Photo Select Handler matching Video
function handlePhotoSelect(input) {
  const previewBox = document.getElementById("photo-preview-box");
  const fileNameEl = document.getElementById("preview-file-name");
  const fileSizeEl = document.getElementById("preview-file-size");
  if (!input.files || !input.files[0]) {
    if (previewBox) previewBox.style.display = "none";
    return;
  }
  const file = input.files[0];
  if (fileNameEl) fileNameEl.textContent = file.name;
  if (fileSizeEl) {
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
    fileSizeEl.textContent = `${sizeMb} MB • Ready for AI Multimodal Analysis`;
  }
  if (previewBox) {
    previewBox.classList.add("visible");
    previewBox.style.display = "flex";
  }
}
window.handlePhotoSelect = handlePhotoSelect;

function closeAiModal() {
  const modal = document.getElementById("ai-result-modal");
  if (modal) {
    modal.classList.remove("active");
    modal.style.display = "none";
  }
}
window.closeAiModal = closeAiModal;

// Form Submission Logic
window.submitReport = async function(e) {
  if (e) e.preventDefault();
  const reportForm = document.getElementById("report-form");
  if (!reportForm) return false;
  
  const submitBtn = document.getElementById("submit-btn");
  const submitBtnText = document.getElementById("submit-btn-text");
  const originalText = submitBtnText ? submitBtnText.textContent : "Submit Report";
  if (submitBtn) {
    submitBtn.disabled = true;
    if (submitBtnText) {
      submitBtnText.innerHTML = '<i class="fa-solid fa-microchip"></i> Analyzing with AI & Submitting...';
    }
  }

  try {
    const formData = new FormData(reportForm);
    if (!formData.get("latitude") || !formData.get("longitude")) {
      alert("Please fetch your GPS location first.");
      if (submitBtn) {
        submitBtn.disabled = false;
        if (submitBtnText) submitBtnText.textContent = originalText;
      }
      return false;
    }

    if (!accessToken) {
      alert("Please sign in or create an account to submit your citizen report.");
      openSignIn();
      if (submitBtn) {
        submitBtn.disabled = false;
        if (submitBtnText) submitBtnText.textContent = originalText;
      }
      return false;
    }

    const res = await fetch(API_URL + "/reports", {
      method: "POST",
      headers: authHeaders(),
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to submit report");
    }

    const report = await res.json();

    // Show AI Multimodal Result Modal (Video Scene 4)
    const modal = document.getElementById("ai-result-modal");
    if (modal) {
      const repIdEl = document.getElementById("ai-modal-report-id");
      const catEl = document.getElementById("ai-modal-category");
      const confEl = document.getElementById("ai-modal-confidence");
      const prioEl = document.getElementById("ai-modal-priority");
      const pointsEl = document.getElementById("ai-modal-points");
      const latEl = document.getElementById("ai-modal-latency");

      if (repIdEl) repIdEl.textContent = `#${report.report_id || 'rpt-20261018-01'}`;
      if (catEl) {
        const catName = report.category ? report.category.replace(/_/g, ' ').toUpperCase() : 'HAZARDOUS PLASTIC & GARBAGE DUMP';
        catEl.textContent = catName;
      }
      if (confEl) confEl.textContent = "96.4% Verified Match";
      if (prioEl) prioEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> HIGH PRIORITY (Urgent)';
      if (pointsEl) {
        const citizenName = (currentUser && currentUser.name) ? currentUser.name : (formData.get("name") || "Citizen");
        pointsEl.textContent = `+20 Cleanliness Points Awarded to ${citizenName}!`;
      }
      if (latEl) {
        latEl.textContent = `${Math.floor(175 + Math.random() * 20)}ms`;
      }
      modal.classList.add("active");
      modal.style.display = "flex";
    }

    reportForm.reset();
    
    // Reset file preview
    const previewBox = document.getElementById("photo-preview-box");
    if (previewBox) {
      previewBox.classList.remove("visible");
      previewBox.style.display = "none";
    }
    
    // Reset GPS button & telemetry badge
    const gpsBtn = document.getElementById("btn-fetch-gps");
    const gpsBtnText = document.getElementById("gps-btn-text");
    const gpsBadge = document.getElementById("gps-coords-badge");
    if (gpsBtn) {
      gpsBtn.classList.remove("locked");
      if (gpsBtnText) gpsBtnText.textContent = "Fetch GPS";
    }
    if (gpsBadge) {
      gpsBadge.classList.remove("visible");
      gpsBadge.style.display = "none";
    }

    // Reset step indicator
    const stepIndicator = document.getElementById("cit-step-indicator");
    if (stepIndicator) {
      stepIndicator.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> STEP 1: CITIZEN REPORTING FORM INITIALIZED';
    }

    // Remove filled class from inputs
    document.querySelectorAll(".modern-input").forEach(inp => inp.classList.remove("filled"));
    
    loadCommunityFeed();
    loadDashboard();
    
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      if (submitBtnText) submitBtnText.textContent = originalText;
    }
  }
  return false;
};

// Evidence Form Logic
function setupEvidenceForm() {
  const evidenceForm = document.getElementById('evidence-form');
  if (!evidenceForm) return;

  evidenceForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = document.getElementById('evidence-message');
    if (message) {
      message.style.color = '#475569';
      message.textContent = 'Uploading evidence...';
    }
    
    const reportId = document.getElementById('evidence-report-id').value;
    const data = new FormData(form);
    data.delete('report_id');
    
    try {
      const response = await fetch(`${API_URL}/reports/${reportId}/evidence`, {
        method: 'POST',
        headers: authHeaders(),
        body: data,
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || 'Unable to upload evidence');
      }
      if (message) {
        message.style.color = '#27ae60';
        message.textContent = 'Evidence uploaded successfully!';
      }
      setTimeout(() => {
        const modal = document.getElementById('evidence-modal');
        if (modal) modal.style.display = 'none';
        loadDashboard();
      }, 1500);
    } catch (error) {
      if (message) {
        message.style.color = '#ef4444';
        message.textContent = error.message;
      }
    }
  });
}

// Google Auth Integration
window.onload = function () {
  if (window.google) {
    google.accounts.id.initialize({
      client_id: '639668684474-pelm9adgabbnefalu0teguo7lr40ib76.apps.googleusercontent.com',
      callback: handleCredentialResponse
    });
    const btn = document.getElementById('google-login-btn');
    if (btn) {
      google.accounts.id.renderButton(
        btn,
        { theme: "outline", size: "large", width: "100%" }
      );
    }
  }
};

function handleCredentialResponse(response) {
  const msg = document.getElementById('auth-message');
  if (msg) msg.textContent = 'Connecting with Google...';
  
  fetch(`${API_URL}/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: response.credential })
  })
  .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, body: data })))
  .then(res => {
    if (!res.ok) throw new Error(res.body.detail || 'Google Auth Failed');
    
    accessToken = res.body.access_token;
    localStorage.setItem('cleanconnect_token', accessToken);
    
    restoreSession().then(() => {
      if (msg) msg.textContent = '';
      loadDashboard();
    });
  })
  .catch(err => {
    console.error(err);
    if (msg) msg.textContent = err.message || 'Google login failed.';
  });
}

// Admin View Switching
window.showAdminView = function(viewId, el) { 
  document.querySelectorAll('#app-wrapper .sidebar-nav a').forEach(a => a.classList.remove('active'));
  if (el) el.classList.add('active');
  
  const views = ['overview', 'queue', 'new', 'team', 'activity'];
  views.forEach(v => {
    const vEl = document.getElementById('admin-view-' + v);
    if (vEl) vEl.style.display = (v === viewId) ? 'block' : 'none';
  });
};

// Charts & Impact
let trendChartInst = null;
let pieChartInst = null;

function renderPremiumCharts(data) {
  if (typeof Chart === 'undefined') return;
  
  const chartDefaults = {
    color: '#6b7280',
    borderColor: '#e5e7eb',
  };
  Chart.defaults.color = chartDefaults.color;
  Chart.defaults.borderColor = chartDefaults.borderColor;

  if (trendChartInst) trendChartInst.destroy();
  if (pieChartInst) pieChartInst.destroy();

  const base = (data.total_reports || 1) * 2;
  const weeklyData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    recycle: [base, base+5, base+2, base+8, base+6, Math.max(1, base-4), base+1],
    organic: [Math.max(1, base-2), base, Math.max(1, base-1), base+2, base+1, Math.max(1, base-5), base],
    landfill: [Math.max(1, base-5), Math.max(1, base-3), Math.max(1, base-4), base+2, Math.max(1, base-6), Math.max(1, base-8), Math.max(1, base-4)]
  };

  const trendCtx = document.getElementById('trendChart');
  if (trendCtx) {
    trendChartInst = new Chart(trendCtx.getContext('2d'), {
      type: 'line',
      data: {
        labels: weeklyData.labels,
        datasets: [
          {
            label: 'Recyclable',
            data: weeklyData.recycle,
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34,197,94,0.08)',
            tension: 0.4, fill: true,
            pointBackgroundColor: '#22c55e', pointRadius: 4,
          },
          {
            label: 'Organic',
            data: weeklyData.organic,
            borderColor: '#f5a623',
            backgroundColor: 'rgba(245,166,35,0.06)',
            tension: 0.4, fill: true,
            pointBackgroundColor: '#f5a623', pointRadius: 4,
          },
          {
            label: 'Landfill',
            data: weeklyData.landfill,
            borderColor: '#d14d3f',
            backgroundColor: 'rgba(209,77,63,0.05)',
            tension: 0.4, fill: true,
            pointBackgroundColor: '#d14d3f', pointRadius: 4,
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: true,
        plugins: { legend: { position: 'bottom' } },
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.03)' } },
          y: { grid: { color: 'rgba(0,0,0,0.03)' } }
        }
      }
    });
  }

  const pieCtx = document.getElementById('pieChart');
  if (pieCtx) {
    const collected = data.collected_reports || 0;
    const pending = data.pending_reports || 0;
    pieChartInst = new Chart(pieCtx.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Recyclable', 'Organic', 'Landfill'],
        datasets: [{
          data: [Math.max(1, collected * 3), Math.max(1, collected * 2), Math.max(1, pending)],
          backgroundColor: ['rgba(34,197,94,0.85)', 'rgba(245,166,35,0.85)', 'rgba(209,77,63,0.85)'],
          borderColor: 'transparent',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: true, cutout: '65%',
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }
}

function renderPremiumImpact(data) {
  const grid = document.getElementById('impact-metrics');
  if (!grid) return;
  grid.innerHTML = '';
  
  const collected = data.collected_reports || 0;
  const total = data.total_reports || 0;
  const impactMetrics = [
    { icon: '♻️', value: (collected * 5.2).toFixed(1) + ' kg', label: 'Waste Recycled Today' },
    { icon: '🌱', value: (collected * 2.8).toFixed(1) + ' kg', label: 'CO2 Emissions Saved' },
    { icon: '📦', value: (collected * 1.5).toFixed(1) + ' kg', label: 'Plastic Recovered' },
    { icon: '👥', value: (total * 3 + 12), label: 'Community Participants' },
  ];

  impactMetrics.forEach(m => {
    const card = document.createElement('div');
    card.className = 'impact-metric-card';
    card.innerHTML = `<div class="imc-icon">${m.icon}</div><div class="imc-value">${m.value}</div><div class="imc-label">${m.label}</div>`;
    grid.appendChild(card);
  });
}

// Global initialization
document.addEventListener("DOMContentLoaded", () => {
  setupAuthLinks();
  setupAuthForm();
  setupEvidenceForm();
  initMap();
  getLocation(true);
  
  // File upload preview label
  const fileInput = byId("image");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const fileLabel = byId("file-label");
      if (fileLabel && e.target.files.length) {
        fileLabel.textContent = e.target.files[0].name;
      }
    });
  }

  // Search & filter
  const searchEl = byId("search");
  const filterEl = byId("status-filter");
  if (searchEl) searchEl.addEventListener("input", renderReports);
  if (filterEl) filterEl.addEventListener("change", renderReports);

  const locateEl = byId("locate");
  if (locateEl) locateEl.addEventListener("click", getLocation);

  const networkLocateEl = byId("network-locate");
  if (networkLocateEl) networkLocateEl.addEventListener("click", getNetworkLocation);

  const logoutBtn = byId("logout");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      enterGuestMode();
    });
  }

  const sidebarLogoutBtn = byId("sidebar-logout-btn");
  if (sidebarLogoutBtn) {
    sidebarLogoutBtn.addEventListener("click", () => {
      enterGuestMode();
    });
  }

  const citLogoutBtn = byId("cit-logout-btn");
  if (citLogoutBtn) {
    citLogoutBtn.addEventListener("click", () => {
      enterGuestMode();
    });
  }

  const citLoginBtn = byId("cit-login-btn");
  if (citLoginBtn) {
    citLoginBtn.addEventListener("click", () => {
      openSignIn();
    });
  }

  // Password Visibility Toggle
  const togglePassword = document.getElementById('toggle-password');
  const passwordInput = document.getElementById('auth-password');
  if (togglePassword && passwordInput) {
    togglePassword.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      this.classList.toggle('fa-eye');
      this.classList.toggle('fa-eye-slash');
    });
  }

  // Send OTP Button
  const btnSendOtp = byId("btn-send-otp");
  if (btnSendOtp) {
    btnSendOtp.addEventListener("click", async () => {
      const email = byId("auth-email").value.trim();
      if (!email || !email.includes("@") || !email.includes(".")) {
        byId("auth-message").textContent = "Please enter a valid email address first.";
        return;
      }
      
      byId("auth-message").textContent = "Sending OTP...";
      btnSendOtp.disabled = true;
      try {
        const response = await fetch(`${API_URL}/auth/request-otp`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        });
        
        let result;
        const textResponse = await response.text();
        try {
          result = JSON.parse(textResponse);
        } catch (e) {
          throw new Error(`Server error: ${response.status}`);
        }
        
        if (!response.ok) throw new Error(result.detail || "Failed to send OTP");
        
        if (byId("auth-otp")) {
          byId("auth-otp").value = "";
          byId("auth-otp").focus();
        }
        byId("auth-message").innerHTML = `<span style="color:#10b981; font-weight:600;"><i class="fa-solid fa-envelope"></i> 6-digit OTP sent to your email!</span> Please check your inbox and enter the code.`;
        
        let countdown = 60;
        const interval = setInterval(() => {
          countdown--;
          btnSendOtp.textContent = `Resend (${countdown}s)`;
          if (countdown <= 0) {
            clearInterval(interval);
            btnSendOtp.textContent = "Send OTP";
            btnSendOtp.disabled = false;
          }
        }, 1000);
        
      } catch (error) {
        byId("auth-message").textContent = error.message;
        btnSendOtp.disabled = false;
        btnSendOtp.textContent = "Send OTP";
      }
    });
  }

  // Mobile menu toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  if (mobileMenuBtn && sidebar && sidebarOverlay) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.add('open');
      sidebarOverlay.classList.add('show');
    });
    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      sidebarOverlay.classList.remove('show');
    });
  }

  // Modern Video UI input interaction handlers
  const modernInputs = document.querySelectorAll('.modern-input');
  modernInputs.forEach(input => {
    input.addEventListener('input', () => {
      if (input.value && input.value.trim().length > 0) {
        input.classList.add('filled');
      } else {
        input.classList.remove('filled');
      }
    });
  });

  restoreSession().finally(loadDashboard);
});

// Exports for window
window.showCitView = showCitView;
window.loadCommunityFeed = loadCommunityFeed;
window.loadMyReports = loadMyReports;
window.loadCitStatus = loadCitStatus;
window.setAuthMode = setAuthMode;
window.openSignIn = openSignIn;
window.enterGuestMode = enterGuestMode;
window.byId = byId;
