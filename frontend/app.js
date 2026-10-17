const hostname = window.location.hostname;
const isLocal = !hostname || hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.');
const API_URL = isLocal ? `http://${hostname || 'localhost'}:8000` : "";
let reports = [];
let accessToken = localStorage.getItem("cleanconnect_token");
let currentUser = null;
let map;
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
  currentUser = { name: "Guest", role: "citizen", isGuest: true };
  updateSidebarProfile("Guest");
  if (byId("session-label")) byId("session-label").textContent = "Guest mode";
  if (byId("login")) byId("login").hidden = false;
  if (byId("logout")) byId("logout").hidden = true;
  if (byId("login-screen")) byId("login-screen").hidden = true;
  if (byId("app-wrapper")) byId("app-wrapper").hidden = true;
  if (byId("collector-dashboard-wrapper")) byId("collector-dashboard-wrapper").hidden = true;
  if (byId("citizen-wrapper")) byId("citizen-wrapper").hidden = false;
  document.body.classList.remove("collector-mode");
  
  if (byId("cit-user-name")) byId("cit-user-name").textContent = "Guest";
  if (byId("cit-user-email")) byId("cit-user-email").textContent = "Login to report";
  if (byId("cit-user-avatar")) {
    byId("cit-user-avatar").innerHTML = `<img src="https://ui-avatars.com/api/?name=Guest&background=random&color=fff&rounded=true" style="width: 100%; height: 100%; border-radius: 50%;">`;
  }
  
  // Custom toggles for guest view
  if (byId("cit-logout-btn")) byId("cit-logout-btn").style.display = "none";
  if (byId("cit-login-btn")) byId("cit-login-btn").style.display = "inline-block";
  if (byId("report-form")) byId("report-form").style.display = "none";
  if (byId("guest-report-msg")) byId("guest-report-msg").style.display = "block";
}

function openSignIn() {
  if (byId("login-screen")) {
    byId("login-screen").hidden = false;
    byId("login-screen").classList.add("active");
  }
  if (byId("app-wrapper")) byId("app-wrapper").hidden = true;
  if (byId("citizen-wrapper")) byId("citizen-wrapper").hidden = true;
  if (byId("collector-dashboard-wrapper")) byId("collector-dashboard-wrapper").hidden = true;
  setAuthMode("login");
}



function initMap() {
  if (typeof THREE === "undefined") return;
  const container = byId("map");
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xdceee3);
  const camera = new THREE.PerspectiveCamera(
    42,
    container.clientWidth / container.clientHeight,
    0.1,
    1000,
  );
  camera.position.set(13, 16, 18);
  camera.lookAt(0, 0, 0);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
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
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
}

function setLocation(latitude, longitude) {
  currentLocation = [latitude, longitude];
  byId("latitude").value = latitude.toFixed(6);
  byId("longitude").value = longitude.toFixed(6);
  const locationStatus = byId("location-status");
  if (locationStatus) {
    locationStatus.textContent = `GPS locked: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
  }
  
  const locInput = byId("report-location");
  if (locInput && !locInput.value) {
    locInput.placeholder = "Locating...";
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`)
      .then(r => r.json())
      .then(data => {
        if (data && data.display_name) {
          locInput.value = data.display_name.split(",").slice(0, 3).join(",");
        }
      })
      .catch(e => {
        console.error("Reverse geocoding failed", e);
        locInput.placeholder = "Enter Location";
      });
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

function getLocation() {
  const locationStatus = byId("location-status");
  if (!navigator.geolocation) {
    if (locationStatus) locationStatus.textContent = "GPS is not supported by this browser";
    return;
  }
  if (locationStatus) locationStatus.textContent = "Requesting your location...";
  navigator.geolocation.getCurrentPosition(
    (position) =>
      setLocation(position.coords.latitude, position.coords.longitude),
    () => {
      if (locationStatus) locationStatus.textContent = "GPS unavailable. Trying network location...";
      getNetworkLocation();
    },
    { enableHighAccuracy: true, timeout: 3000, maximumAge: 300000 },
  );
}

async function getNetworkLocation() {
  const locationStatus = byId("location-status");
  if (locationStatus) locationStatus.textContent = "Detecting approximate network location...";
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
    if (locationStatus) locationStatus.textContent = "Unable to detect network location. Error: " + error.message;
  }
}
if (networkLocateEl) networkLocateEl.addEventListener("click", getNetworkLocation);
const focusReportBtn = byId("focus-report");
if (focusReportBtn) {
  focusReportBtn.addEventListener("click", () => {
    const p = byId("report-panel");
    if (p) p.scrollIntoView({ behavior: "smooth" });
  });
}

initMap();
getLocation();
setAuthMode("login");

restoreSession().finally(loadDashboard);

// Intro Animation Logic
setTimeout(() => {
  const box = document.getElementById("box");
  const place = document.getElementById("boxPlace");
  if (box && place) {
    box.style.transition = "1.2s ease";
    box.style.position = "fixed";
    box.style.left = "70%";
    box.style.top = "auto";
    box.style.bottom = "82px";
    box.style.transform = "scale(.8)";
    place.classList.add("show");
  }
}, 4200);

setTimeout(() => {
  const intro = document.getElementById("intro");
  if (intro) intro.style.opacity = "0";
}, 5400);

setTimeout(() => {
  const loginScreen = document.getElementById("login-screen");
  const intro = document.getElementById("intro");
  if (intro) intro.style.display = "none";
}, 6200);

// Password Visibility Toggle Logic
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

// Send OTP Button Logic
if (byId("btn-send-otp")) {
  byId("btn-send-otp").addEventListener("click", async () => {
    const email = byId("auth-email").value;
    if (!email || !email.toLowerCase().endsWith("@gmail.com")) {
      byId("auth-message").textContent = "Please enter a valid @gmail.com address first.";
      return;
    }
    
    byId("auth-message").textContent = "Sending OTP...";
    byId("btn-send-otp").disabled = true;
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
        throw new Error(`Server error: ${response.status} - ${textResponse.slice(0, 30)}...`);
      }
      
      if (!response.ok) throw new Error(result.detail || "Failed to send OTP");
      
      byId("auth-message").textContent = "OTP sent to your email. Please verify.";
      
      // Cooldown timer
      let countdown = 60;
      const interval = setInterval(() => {
        countdown--;
        byId("btn-send-otp").textContent = `Resend (${countdown}s)`;
        if (countdown <= 0) {
          clearInterval(interval);
          byId("btn-send-otp").textContent = "Send OTP";
          byId("btn-send-otp").disabled = false;
        }
      }, 1000);
      
    } catch (error) {
      byId("auth-message").textContent = error.message;
      byId("btn-send-otp").disabled = false;
      byId("btn-send-otp").textContent = "Send OTP";
    }
  });
}


// --- Google Auth Integration ---
window.onload = function () {
  if (window.google) {
    google.accounts.id.initialize({
      client_id: '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', // Provided by user
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
    
    // Fallback if API_URL wasn't used or checkSession was deleted
    if (typeof restoreSession === 'function') {
      restoreSession().then(() => {
        if (msg) msg.textContent = '';
        if (typeof loadDashboard === 'function') loadDashboard();
      });
    } else if (typeof checkSession === 'function') {
      checkSession();
    }
  })
  .catch(err => {
    console.error(err);
    if (msg) msg.textContent = err.message || 'Google login failed.';
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
  
  // Close sidebar on nav link click in mobile view
  const navLinks = sidebar.querySelectorAll('.sidebar-nav a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('show');
      }
    });
  });
}


window.showAdminView = function(viewId, el) { 
  document.querySelectorAll('#app-wrapper .sidebar-nav a').forEach(a => a.classList.remove('active'));
  if (el) el.classList.add('active');
  
  const views = ['overview', 'queue', 'new', 'team', 'activity'];
  views.forEach(v => {
    const el = document.getElementById('admin-view-' + v);
    if(el) el.style.display = (v === viewId) ? 'block' : 'none';
  });
};

const evidenceForm = document.getElementById('evidence-form');
if (evidenceForm) {
  evidenceForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = document.getElementById('evidence-message');
    message.style.color = '#475569';
    message.textContent = 'Uploading evidence...';
    
    const reportId = document.getElementById('evidence-report-id').value;
    const data = new FormData(form);
    data.delete('report_id'); // Just need the evidence file itself
    
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
      message.style.color = '#27ae60';
      message.textContent = 'Evidence uploaded successfully!';
      setTimeout(() => {
        document.getElementById('evidence-modal').style.display = 'none';
        loadDashboard();
      }, 1500);
    } catch (error) {
      message.style.color = '#ef4444';
      message.textContent = error.message;
    }
  });
}




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

  // Simulated Weekly Trend based on real totals for demo effect
  const base = data.total_reports * 2;
  const weeklyData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    recycle: [base, base+5, base+2, base+8, base+6, base-4, base+1],
    organic: [base-2, base, base-1, base+2, base+1, base-5, base],
    landfill: [base-5, base-3, base-4, base-2, base-6, base-8, base-4]
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
    pieChartInst = new Chart(pieCtx.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Recyclable', 'Organic', 'Landfill'],
        datasets: [{
          data: [data.collected_reports * 3, data.collected_reports * 2, data.pending_reports],
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
  
  const impactMetrics = [
    { icon: '??', value: (data.collected_reports * 5.2).toFixed(1) + ' kg', label: 'Waste Recycled Today' },
    { icon: '??', value: (data.collected_reports * 2.8).toFixed(1) + ' kg', label: 'CO2 Emissions Saved' },
    { icon: '??', value: (data.collected_reports * 1.5).toFixed(1) + ' kg', label: 'Plastic Recovered' },
    { icon: '??', value: (data.total_reports * 3 + 12), label: 'Community Participants' },
  ];

  impactMetrics.forEach(m => {
    const card = document.createElement('div');
    card.className = 'impact-metric-card';
    card.innerHTML = `<div class="imc-icon">${m.icon}</div><div class="imc-value">${m.value}</div><div class="imc-label">${m.label}</div>`;
    grid.appendChild(card);
  });
}




// Form Submission Logic
window.submitReport = async function(e) {
  e.preventDefault();
  const reportForm = document.getElementById("report-form");
  if (!reportForm) return false;
  
  const submitBtn = document.getElementById("submit-btn");
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Submitting...";
  submitBtn.disabled = true;

  try {
    const formData = new FormData(reportForm);
    if (!formData.get("latitude") || !formData.get("longitude")) {
      alert("Please fetch your GPS location first.");
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
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

    alert("Successfully submitted! Thank you for your contribution.");
    
    reportForm.reset();
    const fileLabel = document.getElementById("file-label");
    if (fileLabel) fileLabel.textContent = "Choose a photo";
    
    if (typeof loadCommunityFeed === 'function') loadCommunityFeed();
    loadDashboard();
    
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
  }
  return false;
};
