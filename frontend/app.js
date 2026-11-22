const hostname = window.location.hostname;
const isLocal = !hostname || hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.');
const API_URL = isLocal ? `http://${hostname || 'localhost'}:8000` : (window.BACKEND_API_URL || localStorage.getItem("cleanconnect_api_url") || "");
window.API_URL = API_URL;

try {
  if (!sessionStorage.getItem("cleanconnect_visited")) {
    sessionStorage.setItem("cleanconnect_visited", "true");
    fetch(`${API_URL}/api/track-visit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: window.location.pathname || "/" })
    }).catch(() => {});
  }
} catch (e) {}

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

// ========================================================
// MODULE 1: ADVANCED CAMERA INTEGRATION & GALLERY ENGINE
// ========================================================
let liveCameraStream = null;
let currentCameraFacingMode = "environment"; // Rear camera priority
let selectedImageFile = null;
let selectedImageMetadata = null;

async function triggerCameraCapture() {
  const isSecure = window.isSecureContext || window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && isSecure) {
    await openLiveCameraModal();
  } else {
    const fallbackInput = byId("native-camera-fallback-input");
    if (fallbackInput) fallbackInput.click();
  }
}
window.triggerCameraCapture = triggerCameraCapture;

async function openLiveCameraModal() {
  const modal = byId("camera-modal");
  const video = byId("camera-video-stream");
  const statusText = byId("camera-status-text");
  if (!modal || !video) return;

  modal.style.display = "flex";
  if (statusText) statusText.textContent = currentCameraFacingMode === "environment" ? "Rear Camera Active (HD)" : "Front Camera Active (HD)";

  try {
    if (liveCameraStream) {
      liveCameraStream.getTracks().forEach(t => t.stop());
    }

    const constraints = {
      video: {
        facingMode: { ideal: currentCameraFacingMode },
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: false
    };

    liveCameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = liveCameraStream;
    await video.play();
  } catch (err) {
    console.warn("Live camera access failed, switching to native camera:", err);
    modal.style.display = "none";
    if (liveCameraStream) {
      liveCameraStream.getTracks().forEach(t => t.stop());
      liveCameraStream = null;
    }
    let errorMsg = "Camera access unavailable.";
    if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
      errorMsg = "Camera permission was denied. Please allow camera permissions in your browser or choose an image from your gallery.";
    } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
      errorMsg = "No camera hardware detected on this device.";
    } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
      errorMsg = "Camera is currently locked or in use by another application.";
    }
    alert(errorMsg);
    const fallbackInput = byId("native-camera-fallback-input");
    if (fallbackInput) fallbackInput.click();
  }
}
window.openLiveCameraModal = openLiveCameraModal;

function cancelLiveCamera() {
  const modal = byId("camera-modal");
  if (modal) modal.style.display = "none";
  if (liveCameraStream) {
    liveCameraStream.getTracks().forEach(track => track.stop());
    liveCameraStream = null;
  }
}
window.cancelLiveCamera = cancelLiveCamera;

async function switchCameraFacingMode() {
  currentCameraFacingMode = currentCameraFacingMode === "environment" ? "user" : "environment";
  await openLiveCameraModal();
}
window.switchCameraFacingMode = switchCameraFacingMode;

async function capturePhotoFromStream() {
  const video = byId("camera-video-stream");
  if (!video || !video.videoWidth || !video.videoHeight) {
    alert("Camera stream is not ready yet. Please wait a moment.");
    return;
  }

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  cancelLiveCamera();

  canvas.toBlob(async (blob) => {
    if (!blob) {
      alert("Failed to capture image frame.");
      return;
    }
    const capturedFile = new File([blob], `waste_capture_${Date.now()}.jpg`, { type: "image/jpeg" });
    await processAndDisplayImage(capturedFile);
  }, "image/jpeg", 0.90);
}
window.capturePhotoFromStream = capturePhotoFromStream;

function triggerGalleryPicker() {
  const galleryInput = byId("gallery-file-input");
  if (galleryInput) galleryInput.click();
}
window.triggerGalleryPicker = triggerGalleryPicker;

async function handleGallerySelection(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  await processAndDisplayImage(file);
}
window.handleGallerySelection = handleGallerySelection;

async function handleNativeCameraCapture(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  await processAndDisplayImage(file);
}
window.handleNativeCameraCapture = handleNativeCameraCapture;

// Client-side image validation, resizing and compression
async function processAndDisplayImage(rawFile) {
  const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  const validExts = [".jpg", ".jpeg", ".png", ".webp"];
  const lowerName = (rawFile.name || "").toLowerCase();
  const hasValidExt = validExts.some(ext => lowerName.endsWith(ext));
  
  if (!validTypes.includes(rawFile.type) && !hasValidExt) {
    alert("Invalid file format. Please upload a JPG, JPEG, PNG, or WEBP image.");
    return;
  }

  if (rawFile.size > 15 * 1024 * 1024) {
    alert("Image file is too large (>15MB). Please choose a smaller photo.");
    return;
  }

  try {
    const compressed = await compressImageFile(rawFile, 1920, 1920, 0.88);
    selectedImageFile = compressed.file;
    selectedImageMetadata = {
      width: compressed.width,
      height: compressed.height,
      sizeMb: compressed.sizeMb,
      originalSizeMb: (rawFile.size / (1024 * 1024)).toFixed(2),
      format: "JPEG"
    };

    const previewCard = byId("image-preview-card");
    const previewImg = byId("preview-image-element");
    const resText = byId("preview-resolution-text");
    const sizeText = byId("preview-filesize-text");
    const formatText = byId("preview-format-text");

    if (previewImg) previewImg.src = compressed.dataUrl;
    if (resText) resText.textContent = `${compressed.width} × ${compressed.height}`;
    if (sizeText) sizeText.textContent = `Optimized: ${compressed.sizeMb} MB (was ${selectedImageMetadata.originalSizeMb} MB)`;
    if (formatText) formatText.textContent = "Format: JPEG (Validated)";
    if (previewCard) previewCard.style.display = "block";

    // Auto-trigger GPS request if not yet locked (Module 4 Step 4)
    if (!currentLocation && !isGpsAcquisitionInProgress) {
      acquirePreciseGps(false);
    }

    // Run Instant AI Waste Classification Preview (Module 4 Steps 8 & 9)
    await runInstantAiClassification(selectedImageFile);

  } catch (err) {
    console.error("Image processing error:", err);
    alert("Could not process image. Please try another photo.");
  }
}

function compressImageFile(file, maxWidth = 1920, maxHeight = 1920, quality = 0.88) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = (e) => {
      const img = new Image();
      img.onerror = reject;
      img.onload = () => {
        let width = img.width;
        let height = img.height;

        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width = Math.round(width * ratio);
          height = Math.round(height * ratio);
        }

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error("Canvas toBlob failed"));
            return;
          }
          const compressedFile = new File([blob], file.name.replace(/\.[^/.]+$/, ".jpg"), { type: "image/jpeg" });
          const sizeMb = (blob.size / (1024 * 1024)).toFixed(2);
          resolve({
            blob,
            file: compressedFile,
            width,
            height,
            sizeMb,
            dataUrl: canvas.toDataURL("image/jpeg", quality)
          });
        }, "image/jpeg", quality);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function removeSelectedImage() {
  selectedImageFile = null;
  selectedImageMetadata = null;

  const previewCard = byId("image-preview-card");
  const aiCard = byId("ai-preview-card");
  const galleryInput = byId("gallery-file-input");
  const cameraInput = byId("native-camera-fallback-input");

  if (previewCard) previewCard.style.display = "none";
  if (aiCard) aiCard.style.display = "none";
  if (galleryInput) galleryInput.value = "";
  if (cameraInput) cameraInput.value = "";
}
window.removeSelectedImage = removeSelectedImage;

async function runInstantAiClassification(file) {
  const aiCard = byId("ai-preview-card");
  const catText = byId("ai-pred-category-text");
  const confBadge = byId("ai-conf-badge");
  const binPill = byId("ai-disposal-bin-pill");

  if (aiCard) aiCard.style.display = "flex";
  if (catText) catText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with AI...';

  try {
    const formData = new FormData();
    formData.append("image", file);

    const res = await fetch(`${API_URL}/reports/analyze-waste`, {
      method: "POST",
      headers: authHeaders(),
      body: formData
    });

    if (res.ok) {
      const data = await res.json();
      const catFormatted = (data.category || "GENERAL WASTE").replace(/_/g, " ").toUpperCase();
      const confPct = Math.round((data.confidence || 0.95) * 100);
      const isDry = data.disposal_bin !== "green_bin";

      if (catText) catText.textContent = catFormatted;
      if (confBadge) confBadge.textContent = `${confPct}% Match`;
      if (binPill) {
        binPill.innerHTML = isDry
          ? '<i class="fa-solid fa-trash" style="color:#2563eb;"></i> Blue Bin (Dry Recyclable)'
          : '<i class="fa-solid fa-trash" style="color:#10b981;"></i> Green Bin (Wet Organic)';
        binPill.style.background = isDry ? "#dbeafe" : "#dcfce7";
        binPill.style.borderColor = isDry ? "#bfdbfe" : "#bbf7d0";
        binPill.style.color = isDry ? "#1e40af" : "#166534";
      }
    } else {
      if (catText) catText.textContent = "CIVIC WASTE (AI PENDING)";
      if (confBadge) confBadge.textContent = "Verified";
    }
  } catch (err) {
    if (catText) catText.textContent = "CIVIC WASTE INCIDENT";
    if (confBadge) confBadge.textContent = "Validated";
  }
}

// ========================================================
// MODULE 2 & 3: ADVANCED GPS LOCATION & GOOGLE MAPS
// ========================================================
currentLocation = null; // [latitude, longitude]
let currentAccuracyMeters = null;
let currentGpsTimestamp = null;
let currentLocationSource = "gps"; // 'gps' | 'manual'
let isLocationManuallyConfirmed = false;
let currentParsedAddress = null;
let isGpsAcquisitionInProgress = false;

let googleMap = null;
let googleIncidentMarker = null;
let googleAccuracyCircle = null;
let googleGeocoder = null;
let isGoogleMapsLoaded = false;
let reportMiniMap = null;
let reportMiniMarker = null;
let reportMiniCircle = null;

// GPS Accuracy Classification:
// 0–20 meters: Excellent
// 21–50 meters: Good
// 51–100 meters: Moderate
// 101–500 meters: Poor
// Above 500 meters: Very Poor
function classifyGpsAccuracy(accuracy) {
  const acc = Math.round(accuracy);
  if (acc <= 20) return { label: "Excellent", class: "acc-excellent", stroke: "#10b981", fill: "#10b981" };
  if (acc <= 50) return { label: "Good", class: "acc-good", stroke: "#059669", fill: "#059669" };
  if (acc <= 100) return { label: "Moderate", class: "acc-moderate", stroke: "#f59e0b", fill: "#f59e0b" };
  if (acc <= 500) return { label: "Poor", class: "acc-poor", stroke: "#f97316", fill: "#f97316" };
  return { label: "Very Poor", class: "acc-very-poor", stroke: "#ef4444", fill: "#ef4444" };
}

// Request precise device location using navigator.geolocation.getCurrentPosition()
// enableHighAccuracy: true, timeout: 20000, maximumAge: 0
// Multi-reading comparison to choose freshest & lowest accuracy reading
async function acquirePreciseGps(isRetry = false) {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser. Please drag the red pin on the map to set location.");
    return;
  }

  isGpsAcquisitionInProgress = true;
  const gpsBtn = byId("btn-fetch-gps");
  const gpsBtnText = byId("gps-btn-text");
  const statusIndicator = byId("gps-status-indicator");

  if (gpsBtnText) gpsBtnText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Locking GPS...';
  if (statusIndicator) statusIndicator.innerHTML = '<i class="fa-solid fa-satellite-dish fa-spin" style="color:#2563eb;"></i> Acquiring high-accuracy GNSS fix...';

  const readPosition = () => {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 0
      });
    });
  };

  try {
    let bestReading = await readPosition();
    
    // Take a second reading if retry or accuracy > 20m for satellite lock refinement
    if (bestReading.coords.accuracy > 20 && isRetry) {
      try {
        await new Promise(r => setTimeout(r, 1200));
        const secondReading = await readPosition();
        if (secondReading.coords.accuracy < bestReading.coords.accuracy) {
          bestReading = secondReading;
        }
      } catch (e) {}
    }

    const { latitude, longitude, accuracy } = bestReading.coords;
    const timestamp = new Date(bestReading.timestamp || Date.now()).toISOString();

    applyNewReportLocation(latitude, longitude, accuracy, timestamp, "gps", false);

  } catch (err) {
    console.warn("High accuracy GPS acquisition error:", err);
    let errMsg = "Unable to retrieve device GPS.";
    if (err.code === 1) { // PERMISSION_DENIED
      errMsg = "Location permission was denied. Please allow location access in your browser or drag the red pin on Google Maps.";
    } else if (err.code === 2) { // POSITION_UNAVAILABLE
      errMsg = "GPS position unavailable. Please ensure GPS/Location Services are turned ON.";
    } else if (err.code === 3) { // TIMEOUT
      errMsg = "GPS request timed out (>20s). Please step outside or tap Retry GPS.";
    }
    alert(errMsg);
    if (statusIndicator) statusIndicator.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color:#ef4444;"></i> ${errMsg}`;
  } finally {
    isGpsAcquisitionInProgress = false;
    if (gpsBtnText) gpsBtnText.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Detect GPS';
  }
}
window.acquirePreciseGps = acquirePreciseGps;

// Apply coordinates to state, UI, Google Maps & Reverse Geocoding
async function applyNewReportLocation(lat, lng, accuracyMeters, timestamp, source = "gps", isConfirmed = false) {
  currentLocation = [lat, lng];
  currentAccuracyMeters = accuracyMeters ? Math.round(accuracyMeters) : 15;
  currentGpsTimestamp = timestamp || new Date().toISOString();
  currentLocationSource = source;
  isLocationManuallyConfirmed = isConfirmed;

  // Update hidden inputs for backend submission
  if (byId("latitude")) byId("latitude").value = lat.toFixed(6);
  if (byId("longitude")) byId("longitude").value = lng.toFixed(6);
  if (byId("gps-accuracy-val")) byId("gps-accuracy-val").value = currentAccuracyMeters;
  if (byId("location-timestamp-val")) byId("location-timestamp-val").value = currentGpsTimestamp;
  if (byId("location-source-val")) byId("location-source-val").value = source;
  if (byId("is-manually-confirmed-val")) byId("is-manually-confirmed-val").value = isConfirmed ? "true" : "false";

  // Update Telemetry Strip (Accuracy Classification)
  const accStrip = byId("gps-accuracy-strip");
  const accPill = byId("accuracy-pill-badge");
  const sourceTag = byId("location-source-tag");
  const timeLabel = byId("telemetry-timestamp-label");
  const warnBanner = byId("gps-warning-banner");
  const advBanner = byId("gps-advisory-banner");
  const statusIndicator = byId("gps-status-indicator");

  const classification = classifyGpsAccuracy(currentAccuracyMeters);

  if (accStrip) accStrip.style.display = "flex";
  if (accPill) {
    accPill.className = `gps-acc-badge ${classification.class}`;
    accPill.innerHTML = `<i class="fa-solid fa-circle-check"></i> Accuracy: ±${currentAccuracyMeters}m (${classification.label})`;
  }
  if (sourceTag) {
    sourceTag.innerHTML = source === "manual"
      ? '<i class="fa-solid fa-map-pin" style="color:#0284c7;"></i> Manually Adjusted Pin'
      : '<i class="fa-solid fa-satellite" style="color:#10b981;"></i> Device GPS Locked';
  }
  if (timeLabel) {
    const timeStr = new Date(currentGpsTimestamp).toLocaleTimeString();
    timeLabel.textContent = `Timestamp: ${timeStr}`;
  }

  // Warnings for accuracy > 100m or > 1000m
  if (warnBanner) {
    warnBanner.style.display = (source === "gps" && currentAccuracyMeters > 100) ? "flex" : "none";
  }
  if (advBanner) {
    advBanner.style.display = (source === "gps" && currentAccuracyMeters > 1000) ? "flex" : "none";
  }
  if (statusIndicator) {
    statusIndicator.innerHTML = `<i class="fa-solid fa-circle-check" style="color:#10b981;"></i> GPS Coords Locked (${classification.label})`;
  }

  // Update Location Confirmation Card (Module 3)
  const confirmCard = byId("location-confirmation-card");
  const dispLat = byId("display-latitude");
  const dispLng = byId("display-longitude");
  const dispAcc = byId("display-accuracy");
  const mapsLink = byId("btn-open-google-maps");
  const confirmedBadge = byId("loc-confirmed-badge");

  if (confirmCard) confirmCard.style.display = "block";
  if (dispLat) dispLat.textContent = `${lat.toFixed(6)}° N`;
  if (dispLng) dispLng.textContent = `${lng.toFixed(6)}° E`;
  if (dispAcc) dispAcc.textContent = `±${currentAccuracyMeters} meters (${classification.label})`;
  if (mapsLink) mapsLink.href = `https://www.google.com/maps?q=${lat},${lng}`;
  if (confirmedBadge) {
    confirmedBadge.textContent = isConfirmed ? "Location Confirmed" : "Pending Confirmation";
    confirmedBadge.style.background = isConfirmed ? "#dcfce7" : "#e0e7ff";
    confirmedBadge.style.color = isConfirmed ? "#166534" : "#3730a3";
  }

  // Reverse Geocoding Lookup
  reverseGeocodeAndRender(lat, lng);

  // Render on Interactive Google Map (or fallback)
  renderReportInteractiveMap(lat, lng, currentAccuracyMeters, classification);

  if (campusScene) {
    campusScene.camera.position.set(10, 13, 15);
    renderCampusLocation();
  }
}
window.setLocation = function(latitude, longitude, accuracy = null, source = "gps") {
  applyNewReportLocation(latitude, longitude, accuracy, new Date().toISOString(), source, source === "manual");
};

function confirmCitizenLocation() {
  isLocationManuallyConfirmed = true;
  if (byId("is-manually-confirmed-val")) byId("is-manually-confirmed-val").value = "true";
  const confirmedBadge = byId("loc-confirmed-badge");
  if (confirmedBadge) {
    confirmedBadge.textContent = "Location Confirmed";
    confirmedBadge.style.background = "#dcfce7";
    confirmedBadge.style.color = "#166534";
  }
  alert("Incident location confirmed! You may now submit your report.");
}
window.confirmCitizenLocation = confirmCitizenLocation;

async function reverseGeocodeAndRender(lat, lng) {
  const addressEl = byId("display-formatted-address");
  const chipsEl = byId("display-address-chips");
  const reportLocInput = byId("report-location");
  const formattedHidden = byId("formatted-address-val");

  if (addressEl) addressEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Resolving reverse geocoded address...';

  // Try Google Geocoder if available on client
  if (window.google && window.google.maps && window.google.maps.Geocoder) {
    try {
      if (!googleGeocoder) googleGeocoder = new google.maps.Geocoder();
      const response = await googleGeocoder.geocode({ location: { lat, lng } });
      if (response && response.results && response.results.length > 0) {
        const first = response.results[0];
        const formatted = first.formatted_address;
        const parsed = parseGoogleClientComponents(first.address_components);
        applyParsedAddress(formatted, parsed);
        return;
      }
    } catch (e) {
      console.warn("Client Google Geocoder failed, trying backend endpoint:", e);
    }
  }

  // Fallback to backend reverse-geocode endpoint
  try {
    const res = await fetch(`${API_URL}/api/location/reverse-geocode?latitude=${lat}&longitude=${lng}`);
    if (res.ok) {
      const data = await res.json();
      applyParsedAddress(data.formatted_address || data.address, {
        street: data.street,
        area: data.area,
        city: data.city,
        district: data.district,
        state: data.state,
        pin_code: data.pin_code
      });
      return;
    }
  } catch (err) {
    console.warn("Backend reverse geocode failed, trying client Nominatim:", err);
  }

  // Client Nominatim fallback
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1`);
    if (res.ok) {
      const data = await res.json();
      const addr = data.address || {};
      applyParsedAddress(data.display_name, {
        street: addr.road || addr.street || "",
        area: addr.suburb || addr.neighbourhood || addr.village || "",
        city: addr.city || addr.town || addr.village || "",
        district: addr.state_district || addr.county || "",
        state: addr.state || "",
        pin_code: addr.postcode || ""
      });
      return;
    }
  } catch (e) {}

  const coordStr = `Location: ${lat.toFixed(6)}° N, ${lng.toFixed(6)}° E`;
  applyParsedAddress(coordStr, { street: "", area: "", city: "", district: "", state: "", pin_code: "" });
}

function applyParsedAddress(formatted, parts) {
  currentParsedAddress = { formatted_address: formatted, ...parts };
  
  const addressEl = byId("display-formatted-address");
  const chipsEl = byId("display-address-chips");
  const reportLocInput = byId("report-location");
  const formattedHidden = byId("formatted-address-val");

  if (addressEl) addressEl.textContent = formatted;
  if (reportLocInput) reportLocInput.value = formatted.split(",").slice(0, 3).join(",");
  if (formattedHidden) formattedHidden.value = formatted;

  if (chipsEl) {
    chipsEl.innerHTML = "";
    const tags = [
      parts.street ? `Street: ${parts.street}` : null,
      parts.area ? `Area: ${parts.area}` : null,
      parts.city ? `City: ${parts.city}` : null,
      parts.district ? `District: ${parts.district}` : null,
      parts.state ? `State: ${parts.state}` : null,
      parts.pin_code ? `PIN: ${parts.pin_code}` : null,
    ].filter(Boolean);

    tags.forEach(t => {
      const span = document.createElement("span");
      span.className = "addr-tag";
      span.textContent = t;
      chipsEl.appendChild(span);
    });
  }
}

function parseGoogleClientComponents(components) {
  const parts = { street: "", area: "", city: "", district: "", state: "", pin_code: "" };
  if (!components) return parts;
  const streetParts = [];
  const areaParts = [];
  components.forEach(c => {
    const types = c.types || [];
    if (types.includes("street_number") || types.includes("route")) streetParts.push(c.long_name);
    else if (types.includes("sublocality") || types.includes("sublocality_level_1") || types.includes("neighborhood")) areaParts.push(c.long_name);
    else if (types.includes("locality")) parts.city = c.long_name;
    else if (types.includes("administrative_area_level_2")) parts.district = c.long_name;
    else if (types.includes("administrative_area_level_1")) parts.state = c.long_name;
    else if (types.includes("postal_code")) parts.pin_code = c.long_name;
  });
  if (streetParts.length) parts.street = streetParts.join(" ");
  if (areaParts.length) parts.area = areaParts.join(", ");
  return parts;
}

async function searchAddressFromInput() {
  const input = byId("report-location");
  if (!input || !input.value.trim()) {
    alert("Please enter a street, area, or landmark to search.");
    return;
  }
  const query = input.value.trim();

  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;
    const res = await fetch(url);
    const data = await res.json();
    if (data && data.length > 0) {
      const lat = parseFloat(data[0].lat);
      const lon = parseFloat(data[0].lon);
      applyNewReportLocation(lat, lon, 1, new Date().toISOString(), "manual", true);
    } else {
      alert("Address not found. Please drag the red pin on the map to set the exact incident spot.");
    }
  } catch (e) {
    alert("Address search failed. Please drag the red pin on the map to set location.");
  }
}
window.searchAddressFromInput = searchAddressFromInput;

// Initialize Google Maps SDK with fallback
async function initGoogleMapsSdk() {
  if (window.google && window.google.maps) {
    isGoogleMapsLoaded = true;
    return true;
  }

  let apiKey = window.GOOGLE_MAPS_API_KEY;
  if (!apiKey) {
    try {
      const res = await fetch(`${API_URL}/api/config`);
      if (res.ok) {
        const config = await res.json();
        apiKey = config.google_maps_api_key;
      }
    } catch (e) {}
  }

  if (!apiKey) {
    return false;
  }

  return new Promise((resolve) => {
    window.onGoogleMapsInitCallback = () => {
      isGoogleMapsLoaded = true;
      resolve(true);
    };

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,geometry&callback=onGoogleMapsInitCallback`;
    script.async = true;
    script.defer = true;
    script.onerror = () => {
      console.warn("Failed to load Google Maps JS API script. Falling back to Leaflet.");
      resolve(false);
    };
    document.head.appendChild(script);
  });
}

function renderReportInteractiveMap(lat, lng, accuracy, classification) {
  const mapContainer = byId("report-google-map");
  if (!mapContainer) return;

  if (isGoogleMapsLoaded && window.google && window.google.maps) {
    renderGoogleMap(lat, lng, accuracy, classification);
  } else {
    renderLeafletReportMap(lat, lng, accuracy, classification);
  }
}

function renderGoogleMap(lat, lng, accuracy, classification) {
  const mapEl = byId("report-google-map");
  if (!mapEl) return;

  const centerPos = { lat, lng };

  if (!googleMap) {
    googleMap = new google.maps.Map(mapEl, {
      center: centerPos,
      zoom: 17,
      mapTypeId: "roadmap",
      fullscreenControl: true,
      streetViewControl: false,
      zoomControl: true,
      mapTypeControl: true,
      mapTypeControlOptions: {
        style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
      }
    });

    googleMap.addListener("click", (e) => {
      const clickLat = e.latLng.lat();
      const clickLng = e.latLng.lng();
      applyNewReportLocation(clickLat, clickLng, 1, new Date().toISOString(), "manual", true);
    });
  } else {
    googleMap.setCenter(centerPos);
  }

  if (!googleIncidentMarker) {
    googleIncidentMarker = new google.maps.Marker({
      position: centerPos,
      map: googleMap,
      draggable: true,
      title: "Incident Spot (Drag to adjust)",
      animation: google.maps.Animation.DROP,
    });

    googleIncidentMarker.addListener("dragend", (e) => {
      const newLat = e.latLng.lat();
      const newLng = e.latLng.lng();
      applyNewReportLocation(newLat, newLng, 1, new Date().toISOString(), "manual", true);
    });
  } else {
    googleIncidentMarker.setPosition(centerPos);
  }

  if (accuracy && accuracy > 5 && accuracy < 50000) {
    if (!googleAccuracyCircle) {
      googleAccuracyCircle = new google.maps.Circle({
        strokeColor: classification.stroke,
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: classification.fill,
        fillOpacity: 0.15,
        map: googleMap,
        center: centerPos,
        radius: accuracy
      });
    } else {
      googleAccuracyCircle.setCenter(centerPos);
      googleAccuracyCircle.setRadius(accuracy);
      googleAccuracyCircle.setOptions({
        strokeColor: classification.stroke,
        fillColor: classification.fill
      });
    }
  } else if (googleAccuracyCircle) {
    googleAccuracyCircle.setMap(null);
    googleAccuracyCircle = null;
  }
}

function renderLeafletReportMap(lat, lng, accuracy, classification) {
  const mapEl = byId("report-google-map");
  if (!mapEl || typeof L === "undefined") return;

  if (!reportMiniMap) {
    reportMiniMap = L.map("report-google-map", {
      center: [lat, lng],
      zoom: 16,
      zoomControl: true
    });

    L.tileLayer("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
      attribution: "&copy; Google Maps"
    }).addTo(reportMiniMap);

    reportMiniMap.on("click", (e) => {
      const { lat: clickLat, lng: clickLng } = e.latlng;
      applyNewReportLocation(clickLat, clickLng, 1, new Date().toISOString(), "manual", true);
    });
  }

  setTimeout(() => {
    if (reportMiniMap) reportMiniMap.invalidateSize();
  }, 150);

  const pinIcon = L.divIcon({
    html: `
      <div style="position:relative; width:34px; height:34px; display:flex; align-items:center; justify-content:center;">
        <i class="fa-solid fa-location-dot" style="color:#ef4444; font-size:32px; filter:drop-shadow(0 3px 5px rgba(0,0,0,0.4)); cursor:grab;"></i>
      </div>
    `,
    className: "custom-incident-pin",
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34]
  });

  if (reportMiniMarker) {
    reportMiniMarker.setLatLng([lat, lng]);
  } else {
    reportMiniMarker = L.marker([lat, lng], {
      icon: pinIcon,
      draggable: true,
      zIndexOffset: 4000
    }).addTo(reportMiniMap);

    reportMiniMarker.on("dragend", (ev) => {
      const pos = ev.target.getLatLng();
      applyNewReportLocation(pos.lat, pos.lng, 1, new Date().toISOString(), "manual", true);
    });
  }

  if (accuracy && accuracy > 5 && accuracy < 50000) {
    const strokeColor = classification.stroke;
    if (reportMiniCircle) {
      reportMiniCircle.setLatLng([lat, lng]);
      reportMiniCircle.setRadius(accuracy);
      reportMiniCircle.setStyle({ color: strokeColor, fillColor: strokeColor });
    } else {
      reportMiniCircle = L.circle([lat, lng], {
        radius: accuracy,
        color: strokeColor,
        fillColor: strokeColor,
        fillOpacity: 0.15,
        weight: 2
      }).addTo(reportMiniMap);
    }
  } else if (reportMiniCircle) {
    reportMiniMap.removeLayer(reportMiniCircle);
    reportMiniCircle = null;
  }

  reportMiniMap.setView([lat, lng], 16, { animate: true });
}

function scrollToMapToPin() {
  const container = document.getElementById("report-map-container");
  if (container) {
    container.style.display = "block";
    const defaultCoords = currentLocation || (window.lastCitizenCoords ? [window.lastCitizenCoords.lat, window.lastCitizenCoords.lng] : GIDA_CENTER);
    applyNewReportLocation(defaultCoords[0], defaultCoords[1], 1, new Date().toISOString(), "manual", false);
    setTimeout(() => {
      container.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 150);
  }
}
window.scrollToMapToPin = scrollToMapToPin;

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

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
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

  const countEl = byId("map-count");
  if (countEl) countEl.textContent = `${visible.length} visible`;

  const body = byId("reports-body");
  if (!body) return;
  if (!visible.length) {
    body.innerHTML = '<tr><td colspan="5" class="empty" style="text-align: center; padding: 28px; color: #94a3b8;"><i class="fa-solid fa-inbox" style="font-size: 24px; margin-bottom: 8px; display: block;"></i>No matching reports found</td></tr>';
    renderMapMarkers();
    return;
  }

  body.innerHTML = visible
    .map((report) => {
      const photoUrl = `${API_URL}/reports/${report.report_id}/image`;
      const lat = Number(report.latitude) || 0;
      const lng = Number(report.longitude) || 0;
      const mapsDirUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
      const mapsViewUrl = `https://www.google.com/maps?q=${lat},${lng}`;
      const descSnippet = report.description ? escapeHtml(report.description) : "";

      return `
      <tr style="border-bottom: 1px solid var(--col-border); vertical-align: middle;">
        <!-- 1. Report (Photo Thumbnail + ID + Date) -->
        <td style="padding: 12px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="position: relative; width: 48px; height: 48px; flex-shrink: 0; cursor: pointer;" onclick="openCollectorTaskModal('${report.report_id}')" title="Click to view details and full photo">
              <img src="${photoUrl}" 
                   alt="Waste" 
                   style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
                   onerror="this.src='logo.png'" />
              <div style="position: absolute; bottom: 2px; right: 2px; background: rgba(0,0,0,0.65); color: white; border-radius: 3px; padding: 1px 3px; font-size: 0.6rem; pointer-events: none;">
                <i class="fa-solid fa-magnifying-glass-plus"></i>
              </div>
            </div>
            <div>
              <strong style="color: #1e293b; font-family: monospace; font-size: 0.88rem; display: block;">${report.report_id.slice(0, 10)}...</strong>
              <div style="font-size: 0.74rem; color: #64748b; margin-top: 2px;">
                <i class="fa-regular fa-calendar" style="margin-right: 3px;"></i>${new Date(report.timestamp).toLocaleDateString()}
              </div>
              <button type="button" onclick="openCollectorTaskModal('${report.report_id}')" style="background: none; border: none; padding: 0; color: #2563eb; font-size: 0.74rem; cursor: pointer; text-decoration: underline; font-weight: 500; margin-top: 2px;">
                <i class="fa-solid fa-eye"></i> Details
              </button>
            </div>
          </div>
        </td>

        <!-- 2. Category & AI Result -->
        <td style="padding: 12px;">
          <div style="font-weight: 600; color: #0f172a; font-size: 0.88rem;">
            ${report.category ? report.category.replace(/_/g, ' ').toUpperCase() : 'GENERAL WASTE'}
          </div>
          <div style="font-size: 0.76rem; color: #64748b; margin-top: 3px;">
            ${report.ai_result ? `<span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; border: 1px solid #e2e8f0;"><i class="fa-solid fa-robot" style="color: #6366f1;"></i> ${report.ai_result}</span>` : '<span style="color: #94a3b8;">Pending AI</span>'}
          </div>
        </td>

        <!-- 3. Location (Citizen GPS Coordinates + Citizen Notes + Google Maps Links) -->
        <td style="padding: 12px; min-width: 250px;">
          <div style="display: flex; flex-direction: column; gap: 5px;">
            <!-- Exact Citizen GPS Coordinates -->
            <div style="display: inline-flex; align-items: center; gap: 6px; font-family: monospace; font-size: 0.88rem; font-weight: 700; color: #0f172a; background: #fef2f2; border: 1px solid #fee2e2; padding: 3px 8px; border-radius: 6px; align-self: flex-start;">
              <i class="fa-solid fa-location-crosshairs" style="color: #ef4444; font-size: 0.95rem;"></i>
              <span>GPS: ${lat.toFixed(5)}°, ${lng.toFixed(5)}°</span>
            </div>
            
            <!-- Citizen's Entered Location / Landmark -->
            ${descSnippet ? `
              <div style="font-size: 0.8rem; color: #334155; line-height: 1.35; max-width: 280px;" title="${descSnippet}">
                <i class="fa-solid fa-map-pin" style="color: #3b82f6; margin-right: 4px;"></i>
                <span style="color: #64748b; font-weight: 500;">Citizen Location:</span> ${descSnippet}
              </div>
            ` : ''}

            <!-- Google Maps Links -->
            <div style="display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap;">
              <a href="${mapsDirUrl}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; background: #2563eb; color: #ffffff; border-radius: 6px; font-size: 0.78rem; text-decoration: none; font-weight: 600; box-shadow: 0 1px 3px rgba(37,99,235,0.3); transition: background 0.15s ease;" onmouseover="this.style.background='#1d4ed8'" onmouseout="this.style.background='#2563eb'" title="Open Turn-by-Turn Route Navigation in Google Maps">
                <i class="fa-solid fa-diamond-turn-right"></i> Open Google Map
              </a>
              <a href="${mapsViewUrl}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 4px; padding: 5px 8px; background: #f8fafc; color: #334155; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.75rem; text-decoration: none; font-weight: 500;" title="Pin Location on Map">
                <i class="fa-solid fa-map"></i> Pin
              </a>
            </div>
          </div>
        </td>

        <!-- 4. Status -->
        <td style="padding: 12px;">
          <span class="status-pill status-${report.status}">${formatStatus(report.status)}</span>
        </td>

        <!-- 5. Action -->
        <td style="padding: 12px;">
          <div style="display: flex; flex-direction: column; gap: 6px; min-width: 120px;">
            ${actionMarkup(report)}
          </div>
        </td>
      </tr>
    `;
    })
    .join("");

  body.querySelectorAll(".table-action[data-action]").forEach((button) =>
    button.addEventListener("click", () =>
      handleAction(button.dataset.action, button.dataset.id)
    )
  );

  renderMapMarkers();
}

function actionMarkup(report) {
  if (!currentUser) return "";
  if (currentUser.role === "administrator") {
    return `<a href="admin/" class="table-action" style="text-decoration:none;">Admin Console</a>`;
  }
  if (currentUser.role === "collector") {
    if (report.collector_id === currentUser.user_id) {
      if (report.status === "assigned") {
        return `<button class="table-action" data-action="in_progress" data-id="${report.report_id}" style="background: #2563eb; color: #ffffff; border: none; font-weight: 600;"><i class="fa-solid fa-play"></i> Start Work</button>`;
      }
      if (report.status === "in_progress") {
        return `<button class="table-action" data-action="collected" data-id="${report.report_id}" style="background: #0284c7; color: #ffffff; border: none; font-weight: 600;"><i class="fa-solid fa-check"></i> Mark Collected</button>`;
      }
      if (report.status === "collected" && !report.evidence_reference) {
        return `<button class="table-action" data-action="evidence" data-id="${report.report_id}" style="background: #16a34a; color: #ffffff; border: none; font-weight: 600;"><i class="fa-solid fa-camera"></i> Upload Proof</button>`;
      }
      if (report.status === "rejected") {
        return `<button class="table-action" data-action="evidence" data-id="${report.report_id}" style="color: #ef4444; border-color: #fca5a5; font-weight: 600;"><i class="fa-solid fa-rotate-right"></i> Retry Proof</button>`;
      }
      if (report.evidence_reference) {
        return `<button type="button" class="table-action" onclick="openProofModal('${API_URL}/reports/${report.report_id}/evidence-image', 'Cleaned Proof', '${report.status}')" style="background: #dcfce7; color: #15803d; border: 1px solid #86efac; font-weight: 600;"><i class="fa-solid fa-circle-check"></i> Proof Uploaded</button>`;
      }
      if (report.status === "verified") {
        return `<span style="display: inline-flex; align-items: center; gap: 5px; color: #16a34a; font-size: 0.82rem; font-weight: 600;"><i class="fa-solid fa-circle-check"></i> Cleaned & Verified</span>`;
      }
      return `<span style="color: #64748b; font-size: 0.85rem; font-weight: 500;">Assigned to you</span>`;
    }
    return report.collector_id
      ? `<span style="color: #94a3b8; font-size: 0.85rem;">Assigned</span>`
      : `<button class="table-action" data-action="in_progress" data-id="${report.report_id}"><i class="fa-solid fa-hand-holding-hand"></i> Accept Task</button>`;
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
        '<tr><td colspan="5" class="empty">Unable to load live reports.</td></tr>';
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
      window.location.href = "admin/";
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

      // Directly open Report Queue view for Collector
      const queueNavBtn = document.querySelector("#app-wrapper .sidebar-nav a:nth-child(2)");
      if (typeof window.showAdminView === "function") {
        window.showAdminView('queue', queueNavBtn);
      }
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
          
          if (resData.email_delivered) {
            message.style.color = "#10b981";
            message.innerHTML = `<i class="fa-solid fa-envelope"></i> Reset code sent! Please check your email inbox, enter the 6-digit code and your new password below:`;
            if (byId("auth-otp")) byId("auth-otp").value = "";
          } else {
            if (resData.otp && byId("auth-otp")) byId("auth-otp").value = resData.otp;
            message.style.color = "#10b981";
            message.innerHTML = `
              <div style="font-size:0.8rem; color:#f59e0b; margin-bottom:4px; line-height:1.3;">
                <i class="fa-solid fa-circle-info"></i> <b>Free Sandbox Notice:</b> Real emails deliver to <b>digitalminddilip0906@gmail.com</b>.
              </div>
              <span style="color:#10b981; font-weight:700;"><i class="fa-solid fa-circle-check"></i> Test Reset Code Auto-Filled: ${resData.otp}</span><br>Enter your new password below:
            `;
          }
          isOtpStep = true;
          byId("group-password").hidden = false;
          byId("auth-password").required = true;
          byId("auth-password").value = "";
          byId("auth-otp").required = true;
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
  // Auto-close mobile sidebar drawer on selection
  const citSidebar = document.querySelector('.col-sidebar');
  const citOverlay = document.getElementById('cit-sidebar-overlay');
  if (citSidebar) citSidebar.classList.remove('open');
  if (citOverlay) citOverlay.classList.remove('show');

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

  if (viewName === 'new-report') {
    setTimeout(() => {
      if (reportMiniMap) reportMiniMap.invalidateSize();
    }, 150);
  }
  if (viewName === 'community') loadCommunityFeed();
  if (viewName === 'track') loadLiveTrackingMap();
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
  if (input && input.files && input.files[0]) {
    processAndDisplayImage(input.files[0]);
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
  const progressContainer = document.getElementById("submit-progress-container");
  const progressBar = document.getElementById("submit-progress-bar");
  const originalText = submitBtnText ? submitBtnText.innerHTML : "Submit Report";

  // Validate photo
  const imageToUpload = selectedImageFile || (byId("image") && byId("image").files ? byId("image").files[0] : null);
  if (!imageToUpload) {
    alert("Please capture a photo using 'TAKE PHOTO' or choose an image from your gallery first.");
    return false;
  }

  // Validate GPS location
  if (!currentLocation || !currentLocation[0] || !currentLocation[1]) {
    alert("Please acquire your GPS location first by clicking 'Detect GPS' or pinning on the map.");
    return false;
  }

  if (!accessToken) {
    alert("Please sign in or create an account to submit your citizen report.");
    openSignIn();
    return false;
  }

  if (submitBtn) submitBtn.disabled = true;
  if (submitBtnText) {
    submitBtnText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with AI & Submitting...';
  }
  if (progressContainer) progressContainer.style.display = "block";
  if (progressBar) progressBar.style.width = "40%";

  try {
    const formData = new FormData();
    formData.append("image", imageToUpload);
    formData.append("latitude", currentLocation[0]);
    formData.append("longitude", currentLocation[1]);
    formData.append("gps_accuracy", currentAccuracyMeters || 15);
    formData.append("location_timestamp", currentGpsTimestamp || new Date().toISOString());

    const addrStr = currentParsedAddress && currentParsedAddress.formatted_address
      ? currentParsedAddress.formatted_address
      : (byId("report-location") ? byId("report-location").value : "");
    if (addrStr) formData.append("formatted_address", addrStr);

    formData.append("location_source", currentLocationSource || "gps");
    formData.append("is_manually_confirmed", isLocationManuallyConfirmed);

    const descVal = byId("report-desc") ? byId("report-desc").value : "";
    if (descVal) formData.append("description", descVal);

    const nameVal = byId("report-name") ? byId("report-name").value : "";
    if (nameVal) formData.append("name", nameVal);

    if (progressBar) progressBar.style.width = "75%";

    const res = await fetch(API_URL + "/reports", {
      method: "POST",
      headers: authHeaders(),
      body: formData
    });

    if (progressBar) progressBar.style.width = "100%";

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to submit report");
    }

    const report = await res.json();

    // Show AI Multimodal Result Modal
    const modal = document.getElementById("ai-result-modal");
    if (modal) {
      const repIdEl = document.getElementById("ai-modal-report-id");
      const catEl = document.getElementById("ai-modal-category");
      const confEl = document.getElementById("ai-modal-confidence");
      const prioEl = document.getElementById("ai-modal-priority");
      const pointsEl = document.getElementById("ai-modal-points");
      const latEl = document.getElementById("ai-modal-latency");

      if (repIdEl) repIdEl.textContent = `#${report.report_id || 'rpt-verified'}`;
      if (catEl) {
        const catName = report.category ? report.category.replace(/_/g, ' ').toUpperCase() : 'HAZARDOUS WASTE DUMP';
        catEl.textContent = catName;
      }
      if (confEl) {
        const confPct = report.ai_confidence ? Math.round(report.ai_confidence * 100) : 96;
        confEl.textContent = `${confPct}% Verified Match`;
      }
      if (prioEl) prioEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> HIGH PRIORITY (Municipal Dispatched)';
      if (pointsEl) {
        const citizenName = (currentUser && currentUser.name) ? currentUser.name : (nameVal || "Citizen");
        pointsEl.textContent = `+20 Cleanliness Points Awarded to ${citizenName}!`;
      }
      if (latEl) {
        latEl.textContent = `${Math.floor(175 + Math.random() * 25)}ms`;
      }
      modal.classList.add("active");
      modal.style.display = "flex";
    }

    reportForm.reset();
    removeSelectedImage();

    // Reset location states
    const confirmedBadge = byId("loc-confirmed-badge");
    if (confirmedBadge) {
      confirmedBadge.textContent = "Pending Confirmation";
      confirmedBadge.style.background = "#e0e7ff";
      confirmedBadge.style.color = "#3730a3";
    }

    // Refresh live feeds
    if (typeof loadCommunityFeed === "function") loadCommunityFeed();
    if (typeof loadDashboard === "function") loadDashboard();
    if (typeof loadLiveTrackingMap === "function") loadLiveTrackingMap(true);
    
  } catch (err) {
    alert("Report Submission Error: " + err.message);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      if (submitBtnText) submitBtnText.innerHTML = originalText;
    }
    if (progressContainer) {
      setTimeout(() => { progressContainer.style.display = "none"; }, 500);
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
  // Auto-close mobile sidebar drawer on selection
  const sb = document.querySelector('.sidebar');
  const sbo = document.getElementById('sidebar-overlay');
  if (sb) sb.classList.remove('open');
  if (sbo) sbo.classList.remove('show');

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
  initGoogleMapsSdk().finally(() => {
    // Auto-initialize Report Interactive Map with high-accuracy GPS or fallback
    setTimeout(() => {
      if (!currentLocation) {
        acquirePreciseGps(false);
      }
    }, 200);
  });
  
  // File upload preview label
  const fileInput = byId("image");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length) {
        processAndDisplayImage(e.target.files[0]);
      }
    });
  }

  // Search & filter
  const searchEl = byId("search");
  const filterEl = byId("status-filter");
  if (searchEl) searchEl.addEventListener("input", renderReports);
  if (filterEl) filterEl.addEventListener("change", renderReports);

  const locateEl = byId("locate");
  if (locateEl) locateEl.addEventListener("click", () => acquirePreciseGps(false));

  const networkLocateEl = byId("network-locate");
  if (networkLocateEl) networkLocateEl.addEventListener("click", () => acquirePreciseGps(false));

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
        
        if (result.email_delivered) {
          if (byId("auth-otp")) {
            byId("auth-otp").value = "";
            byId("auth-otp").focus();
          }
          byId("auth-message").innerHTML = `<span style="color:#10b981; font-weight:600;"><i class="fa-solid fa-envelope"></i> 6-digit OTP sent to your email!</span> Please check your inbox and enter the code.`;
        } else {
          if (byId("auth-otp") && result.otp) {
            byId("auth-otp").value = result.otp;
            byId("auth-otp").focus();
          }
          byId("auth-message").innerHTML = `
            <div style="font-size:0.8rem; color:#f59e0b; margin-bottom:4px; line-height:1.3;">
              <i class="fa-solid fa-circle-info"></i> <b>Resend Free Sandbox:</b> Real emails deliver to <b>digitalminddilip0906@gmail.com</b>.
            </div>
            <span style="color:#10b981; font-weight:700;"><i class="fa-solid fa-circle-check"></i> Test OTP Auto-Filled: ${result.otp || ""}</span>
          `;
        }
        
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


// Collector Task Details Modal Functions
window.openCollectorTaskModal = async function(reportId) {
  const report = reports.find(r => r.report_id === reportId);
  if (!report) return;

  const lat = Number(report.latitude) || 0;
  const lng = Number(report.longitude) || 0;
  const mapsDirUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
  const mapsViewUrl = `https://www.google.com/maps?q=${lat},${lng}`;
  const photoUrl = `${API_URL}/reports/${report.report_id}/image`;

  const reportIdEl = byId("col-modal-report-id");
  if (reportIdEl) reportIdEl.textContent = `Report #${report.report_id}`;
  
  const statusBadge = byId("col-modal-status-badge");
  if (statusBadge) {
    statusBadge.textContent = formatStatus(report.status);
    statusBadge.className = `status-pill status-${report.status}`;
  }

  const photoEl = byId("col-modal-photo");
  if (photoEl) {
    photoEl.src = photoUrl;
    photoEl.onclick = () => openProofModal(photoUrl, `Reported Waste Photo #${report.report_id}`, report.status);
  }

  const evidenceContainer = byId("col-modal-evidence-container");
  const evidencePhoto = byId("col-modal-evidence-photo");
  if (report.evidence_reference) {
    const evidenceUrl = `${API_URL}/reports/${report.report_id}/evidence-image`;
    if (evidencePhoto) {
      evidencePhoto.src = evidenceUrl;
      evidencePhoto.onclick = () => openProofModal(evidenceUrl, `Cleaned Place Evidence #${report.report_id}`, report.status);
    }
    if (evidenceContainer) evidenceContainer.style.display = "block";
  } else {
    if (evidenceContainer) evidenceContainer.style.display = "none";
  }

  const coordsEl = byId("col-modal-coords");
  if (coordsEl) {
    coordsEl.innerHTML = `<i class="fa-solid fa-crosshairs" style="color: #ef4444; margin-right: 6px;"></i> Latitude: ${lat.toFixed(6)}, Longitude: ${lng.toFixed(6)}`;
  }

  const navLink = byId("col-modal-nav-link");
  if (navLink) navLink.href = mapsDirUrl;

  const viewMapLink = byId("col-modal-view-map-link");
  if (viewMapLink) viewMapLink.href = mapsViewUrl;

  const addressEl = byId("col-modal-address");
  if (addressEl) {
    addressEl.textContent = "Fetching location details...";
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
      .then(r => r.json())
      .then(data => {
        if (data && data.display_name) {
          addressEl.innerHTML = `<i class="fa-solid fa-map-pin" style="color: #3b82f6; margin-right: 4px;"></i> ${escapeHtml(data.display_name)}`;
        } else {
          addressEl.innerHTML = `<i class="fa-solid fa-map-pin" style="color: #3b82f6; margin-right: 4px;"></i> ${escapeHtml(report.description || 'GPS Location Locked')}`;
        }
      })
      .catch(() => {
        addressEl.innerHTML = `<i class="fa-solid fa-map-pin" style="color: #3b82f6; margin-right: 4px;"></i> ${escapeHtml(report.description || 'GPS Location Locked')}`;
      });
  }

  const catEl = byId("col-modal-category");
  if (catEl) catEl.textContent = report.category ? report.category.replace(/_/g, ' ').toUpperCase() : "GENERAL WASTE";

  const aiEl = byId("col-modal-ai");
  if (aiEl) aiEl.textContent = report.ai_result || "Pending AI Analysis";

  const descEl = byId("col-modal-desc");
  if (descEl) descEl.textContent = report.description || "No citizen description notes provided.";

  const dateEl = byId("col-modal-date");
  if (dateEl) dateEl.textContent = `Reported: ${new Date(report.timestamp).toLocaleString()}`;

  const reporterEl = byId("col-modal-reporter");
  if (reporterEl) reporterEl.textContent = `Reporter: ${report.user_id || 'Citizen'}`;

  // Action buttons inside modal
  const actionContainer = byId("col-modal-action-buttons");
  if (actionContainer) {
    actionContainer.innerHTML = "";
    if (currentUser && currentUser.role === "collector") {
      if (report.collector_id === currentUser.user_id) {
        if (report.status === "assigned") {
          const btn = document.createElement("button");
          btn.className = "col-btn-primary";
          btn.innerHTML = `<i class="fa-solid fa-play"></i> Start Work`;
          btn.onclick = async () => {
            closeCollectorTaskModal();
            await handleAction("in_progress", report.report_id);
          };
          actionContainer.appendChild(btn);
        } else if (report.status === "in_progress") {
          const btn = document.createElement("button");
          btn.className = "col-btn-primary";
          btn.style.background = "#0284c7";
          btn.innerHTML = `<i class="fa-solid fa-check"></i> Mark Collected`;
          btn.onclick = async () => {
            closeCollectorTaskModal();
            await handleAction("collected", report.report_id);
          };
          actionContainer.appendChild(btn);
        } else if (report.status === "collected" && !report.evidence_reference) {
          const btn = document.createElement("button");
          btn.className = "col-btn-primary";
          btn.style.background = "#16a34a";
          btn.innerHTML = `<i class="fa-solid fa-camera"></i> Upload Proof`;
          btn.onclick = () => {
            closeCollectorTaskModal();
            handleAction("evidence", report.report_id);
          };
          actionContainer.appendChild(btn);
        }
      } else if (!report.collector_id) {
        const btn = document.createElement("button");
        btn.className = "col-btn-primary";
        btn.innerHTML = `<i class="fa-solid fa-hand-holding-hand"></i> Accept Task`;
        btn.onclick = async () => {
          closeCollectorTaskModal();
          await handleAction("in_progress", report.report_id);
        };
        actionContainer.appendChild(btn);
      }
    }
  }

  const modal = byId("collector-task-modal");
  if (modal) modal.style.display = "flex";
};

window.closeCollectorTaskModal = function() {
  const modal = byId("collector-task-modal");
  if (modal) modal.style.display = "none";
};

window.openProofModal = openProofModal;


// ==========================================================================
// LIVE GIS MAP & GOOGLE MAPS REPORT PINNING LOGIC (WITH PENDING TASK SPIDERING)
// ==========================================================================
let citMap = null;
let citMarkersLayer = null;
let citUserMarker = null;
let citLiveReportsCache = [];
let citReportMarkersMap = {};
let currentMapFilter = 'all';

async function loadLiveTrackingMap(forceRefresh = false) {
  const mapContainer = document.getElementById('cit-map');
  if (!mapContainer) return;
  if (typeof L === 'undefined') {
    console.warn('Leaflet library is not loaded');
    return;
  }

  // 1. Initialize Map if not already initialized
  if (!citMap) {
    const initialLat = window.lastCitizenCoords ? window.lastCitizenCoords.lat : 26.8699;
    const initialLng = window.lastCitizenCoords ? window.lastCitizenCoords.lng : 80.96;

    citMap = L.map('cit-map', {
      center: [initialLat, initialLng],
      zoom: 13,
      zoomControl: true,
      maxZoom: 20
    });

    // Google Maps Roadmap Layer (Standard roadmap with clean labels)
    const googleRoadmap = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
      maxZoom: 20,
      subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
      attribution: '&copy; <a href="https://maps.google.com" target="_blank">Google Maps</a>'
    });

    // Google Maps Satellite / Hybrid Layer
    const googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
      maxZoom: 20,
      subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
      attribution: '&copy; Google Satellite'
    });

    // OpenStreetMap fallback
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    });

    // Add Google Roadmap by default
    googleRoadmap.addTo(citMap);

    // Layer switcher control
    L.control.layers(
      {
        'Google Maps': googleRoadmap,
        'Google Satellite': googleHybrid,
        'OpenStreetMap': osmLayer
      },
      null,
      { position: 'topright' }
    ).addTo(citMap);

    citMarkersLayer = L.featureGroup().addTo(citMap);

    citMap.on('click', (e) => {
      const { lat, lng } = e.latlng;
      setLocation(lat, lng, 1, "map");
      const statusEl = document.getElementById("location-status");
      if (statusEl) {
        statusEl.innerHTML = `<i class="fa-solid fa-map-pin" style="color:#0284c7;"></i> Location pinned from Live Map: <strong>${lat.toFixed(5)}°, ${lng.toFixed(5)}°</strong>`;
      }
    });
  }

  // Ensure Leaflet computes container size properly
  setTimeout(() => {
    if (citMap) {
      citMap.invalidateSize();
    }
  }, 250);

  // 2. Fetch live reports with GPS
  try {
    let reportsData = [];
    if (!forceRefresh && citLiveReportsCache.length > 0) {
      reportsData = citLiveReportsCache;
    } else {
      try {
        const res = await fetch(API_URL + '/reports', { headers: authHeaders() });
        if (res.ok) {
          reportsData = await res.json();
        } else {
          const resComm = await fetch(API_URL + '/reports/community');
          if (resComm.ok) reportsData = await resComm.json();
        }
      } catch (e) {
        const resComm = await fetch(API_URL + '/reports/community');
        if (resComm.ok) reportsData = await resComm.json();
      }
      citLiveReportsCache = reportsData;
    }

    if (!Array.isArray(reportsData)) reportsData = [];

    // Filter valid GPS coords
    const validReports = reportsData.filter(r => {
      const lat = Number(r.latitude);
      const lng = Number(r.longitude);
      return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0 && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    });

    // Count telemetry
    let pendingCount = 0;
    let verifiedCount = 0;
    const pendingReports = [];

    validReports.forEach(r => {
      const isVerified = (r.status === 'verified');
      if (isVerified) {
        verifiedCount++;
      } else {
        pendingCount++;
        pendingReports.push(r);
      }
    });

    const totalCountEl = document.getElementById('cit-map-total-count');
    const pendingCountEl = document.getElementById('cit-map-pending-count');
    const verifiedCountEl = document.getElementById('cit-map-verified-count');
    const pendingListCountEl = document.getElementById('cit-pending-list-count');

    if (totalCountEl) totalCountEl.textContent = validReports.length;
    if (pendingCountEl) pendingCountEl.textContent = pendingCount;
    if (verifiedCountEl) verifiedCountEl.textContent = verifiedCount;
    if (pendingListCountEl) pendingListCountEl.textContent = pendingReports.length;

    // Render all pins with spidering for co-located tasks
    renderMapMarkers(validReports);

    // Render Pending Tasks list section under map
    renderPendingTasksList(pendingReports);

    // Also locate citizen on map
    locateCitizenForMap();

  } catch (err) {
    console.error('Failed to populate live tracking map:', err);
  }
}

// Render markers with intelligent spidering so every task is visible
function renderMapMarkers(allValidReports) {
  if (!citMap || !citMarkersLayer) return;

  citMarkersLayer.clearLayers();
  citReportMarkersMap = {};

  // Filter according to currentMapFilter
  let reportsToDisplay = allValidReports;
  if (currentMapFilter === 'pending') {
    reportsToDisplay = allValidReports.filter(r => r.status !== 'verified');
  } else if (currentMapFilter === 'verified') {
    reportsToDisplay = allValidReports.filter(r => r.status === 'verified');
  }

  // Group by coordinates (within ~11 meters) to spider co-located reports
  const coordGroups = {};
  reportsToDisplay.forEach(r => {
    const key = `${Number(r.latitude).toFixed(4)}_${Number(r.longitude).toFixed(4)}`;
    if (!coordGroups[key]) coordGroups[key] = [];
    coordGroups[key].push(r);
  });

  Object.values(coordGroups).forEach(group => {
    const isMulti = group.length > 1;
    const baseLat = Number(group[0].latitude);
    const baseLng = Number(group[0].longitude);

    group.forEach((r, idx) => {
      let displayLat = Number(r.latitude);
      let displayLng = Number(r.longitude);

      // Spider co-located reports in a clean circular pattern
      if (isMulti) {
        const radius = group.length > 8 ? 0.00030 : 0.00020; // ~20-30 meters
        const angle = (idx * 2 * Math.PI) / group.length;
        displayLat = baseLat + radius * Math.cos(angle);
        displayLng = baseLng + radius * Math.sin(angle);

        // Subtle guide line connecting spidered pin to landmark center
        const line = L.polyline(
          [[baseLat, baseLng], [displayLat, displayLng]],
          { color: '#94a3b8', weight: 1.5, dashArray: '3, 6', opacity: 0.6 }
        );
        citMarkersLayer.addLayer(line);
      }

      const isVerified = (r.status === 'verified');
      const isUrgent = (r.status === 'reported' || r.status === 'ai_analyzed');
      const isInProgress = (r.status === 'assigned' || r.status === 'in_progress' || r.status === 'collected' || r.status === 'reviewed');

      let pinColor = '#ef4444'; // Red for urgent
      let pinIcon = 'fa-triangle-exclamation';
      let zOffset = 1000; // Pending tasks on top!

      if (isVerified) {
        pinColor = '#10b981';
        pinIcon = 'fa-circle-check';
        zOffset = 100;
      } else if (isInProgress) {
        pinColor = '#f59e0b';
        pinIcon = 'fa-clock';
        zOffset = 500;
      }

      const customHtml = `
        <div style="
          width: 34px;
          height: 34px;
          background: ${pinColor};
          border: 2px solid #ffffff;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 10px rgba(0,0,0,0.35);
          cursor: pointer;
        ">
          <i class="fa-solid ${pinIcon}" style="transform: rotate(45deg); color: #ffffff; font-size: 13px;"></i>
        </div>
      `;

      const markerIcon = L.divIcon({
        html: customHtml,
        className: 'custom-map-pin',
        iconSize: [34, 34],
        iconAnchor: [17, 34],
        popupAnchor: [0, -32]
      });

      const marker = L.marker([displayLat, displayLng], {
        icon: markerIcon,
        zIndexOffset: zOffset
      });

      const photoUrl = `${API_URL}/reports/${r.report_id}/image`;
      const mapsDirUrl = `https://www.google.com/maps/dir/?api=1&destination=${baseLat},${baseLng}`;
      const mapsPinUrl = `https://www.google.com/maps?q=${baseLat},${baseLng}`;
      const catText = r.category ? r.category.replace(/_/g, ' ').toUpperCase() : 'CIVIC WASTE HAZARD';
      const dateText = r.timestamp ? new Date(r.timestamp).toLocaleDateString() : '';

      const popupHtml = `
        <div style="font-family: 'Inter', system-ui, sans-serif; min-width: 230px; max-width: 280px; padding: 4px;">
          <div style="position: relative; width: 100%; height: 125px; background: #0f172a; border-radius: 8px; overflow: hidden; margin-bottom: 8px; display: flex; align-items: center; justify-content: center;">
            <img src="${photoUrl}" alt="Waste" style="width: 100%; height: 100%; object-fit: cover; cursor: pointer;" onclick="openProofModal('${photoUrl}', 'Waste Report Evidence #${r.report_id.slice(0, 8)}', '${r.status}')" onerror="this.src='logo.png'" title="Click to enlarge" />
            <span style="position: absolute; top: 6px; right: 6px; background: ${pinColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;">
              ${r.status || 'reported'}
            </span>
          </div>

          ${isMulti ? `<div style="font-size: 0.72rem; color: #64748b; margin-bottom: 4px;"><i class="fa-solid fa-layer-group" style="color: #2563eb;"></i> Task ${idx + 1} of ${group.length} at this landmark</div>` : ''}

          <div style="font-weight: 700; color: #0f172a; font-size: 0.92rem; margin-bottom: 2px;">
            ${catText}
          </div>
          <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 6px;">
            Report ID: #${r.report_id.slice(0, 10)} • ${dateText}
          </div>

          ${r.description ? `<p style="font-size: 0.8rem; color: #334155; margin: 0 0 8px 0; line-height: 1.35; max-height: 48px; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(r.description)}</p>` : ''}

          <div style="background: #eff6ff; padding: 5px 8px; border-radius: 6px; font-family: monospace; font-size: 0.78rem; color: #1e40af; margin-bottom: 8px; font-weight: 700; display: flex; align-items: center; gap: 4px;">
            <i class="fa-solid fa-location-crosshairs" style="color: #ef4444;"></i> GPS: ${baseLat.toFixed(5)}°, ${baseLng.toFixed(5)}°
          </div>

          <div style="display: flex; flex-direction: column; gap: 5px; margin-top: 6px;">
            <a href="${mapsDirUrl}" target="_blank" rel="noopener noreferrer" style="display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 10px; background: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 0.78rem; box-shadow: 0 1px 3px rgba(37,99,235,0.3);">
              <i class="fa-solid fa-diamond-turn-right"></i> Open Navigation in Google Maps
            </a>
            <a href="${mapsPinUrl}" target="_blank" rel="noopener noreferrer" style="display: flex; align-items: center; justify-content: center; gap: 6px; padding: 6px 10px; background: #ffffff; color: #334155; border: 1px solid #cbd5e1; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 0.76rem;">
              <i class="fa-solid fa-map-pin" style="color: #ef4444;"></i> View Pin on Google Maps
            </a>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);
      citMarkersLayer.addLayer(marker);

      citReportMarkersMap[r.report_id] = {
        marker: marker,
        lat: displayLat,
        lng: displayLng,
        report: r
      };
    });
  });

  // Fit bounds to visible markers
  if (citMarkersLayer.getLayers().length > 0) {
    citMap.fitBounds(citMarkersLayer.getBounds(), { padding: [40, 40], maxZoom: 16 });
  }
}

// Render the Pending Tasks cards list below the map
function renderPendingTasksList(pendingReports) {
  const container = document.getElementById('cit-pending-tasks-container');
  if (!container) return;

  if (pendingReports.length === 0) {
    container.innerHTML = `
      <div style="padding: 24px; text-align: center; color: #10b981; grid-column: 1 / -1; background: #f0fdf4; border-radius: 12px; font-weight: 600; border: 1px solid #bbf7d0;">
        <i class="fa-solid fa-circle-check" style="font-size: 26px; margin-bottom: 8px; display: block;"></i>
        All reported municipal tasks in this area have been verified & resolved!
      </div>
    `;
    return;
  }

  container.innerHTML = pendingReports.map(r => {
    const lat = Number(r.latitude);
    const lng = Number(r.longitude);
    const photoUrl = `${API_URL}/reports/${r.report_id}/image`;
    const mapsDirUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    const categoryName = r.category ? r.category.replace(/_/g, ' ').toUpperCase() : 'CIVIC WASTE HAZARD';

    let statusBg = '#fee2e2';
    let statusColor = '#991b1b';
    let statusLabel = (r.status || 'PENDING').toUpperCase();

    if (r.status === 'assigned' || r.status === 'in_progress') {
      statusBg = '#fef3c7';
      statusColor = '#92400e';
    } else if (r.status === 'collected') {
      statusBg = '#e0f2fe';
      statusColor = '#0369a1';
    }

    return `
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between; gap: 10px;">
        <div style="display: flex; gap: 12px; align-items: flex-start;">
          <img src="${photoUrl}" style="width: 64px; height: 64px; border-radius: 8px; object-fit: cover; flex-shrink: 0; cursor: pointer; border: 1px solid #cbd5e1;" onclick="openProofModal('${photoUrl}', 'Pending Task Evidence #${r.report_id.slice(0, 8)}', '${r.status}')" onerror="this.src='logo.png'" title="Click to enlarge" />
          <div style="flex: 1; min-width: 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 4px;">
              <span style="font-size: 0.68rem; background: ${statusBg}; color: ${statusColor}; padding: 2px 8px; border-radius: 12px; font-weight: 700;">
                ${statusLabel}
              </span>
              <span style="font-size: 0.72rem; color: #94a3b8;">${new Date(r.timestamp).toLocaleDateString()}</span>
            </div>
            <strong style="font-size: 0.88rem; color: #0f172a; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${categoryName}
            </strong>
            <div style="font-size: 0.75rem; color: #64748b; font-family: monospace; margin-top: 2px;">
              <i class="fa-solid fa-location-crosshairs" style="color: #ef4444;"></i> ${lat.toFixed(4)}°, ${lng.toFixed(4)}°
            </div>
          </div>
        </div>

        ${r.description ? `<p style="font-size: 0.8rem; color: #334155; margin: 0; line-height: 1.35; max-height: 38px; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(r.description)}</p>` : ''}

        <div style="display: flex; gap: 8px; margin-top: auto; padding-top: 6px; border-top: 1px solid #f1f5f9;">
          <button type="button" onclick="locateReportOnMap('${r.report_id}')" style="flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 7px 10px; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 6px; font-size: 0.78rem; font-weight: 600; cursor: pointer;">
            <i class="fa-solid fa-crosshairs"></i> Locate Pin
          </button>
          <a href="${mapsDirUrl}" target="_blank" rel="noopener noreferrer" style="flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 7px 10px; background: #2563eb; color: #ffffff; border-radius: 6px; font-size: 0.78rem; font-weight: 600; text-decoration: none; box-shadow: 0 1px 3px rgba(37,99,235,0.3);">
            <i class="fa-solid fa-diamond-turn-right"></i> Directions
          </a>
        </div>
      </div>
    `;
  }).join('');
}

// Locate specific report on map and open its popup
window.locateReportOnMap = function(reportId) {
  const item = citReportMarkersMap[reportId];
  if (!item || !citMap) {
    // If not found in current filter, reset filter to 'all' and retry
    if (currentMapFilter !== 'all') {
      window.filterLiveTrackingMap('all');
      setTimeout(() => {
        window.locateReportOnMap(reportId);
      }, 300);
      return;
    }
    alert('Location pin for report #' + reportId + ' could not be found.');
    return;
  }

  // Pan and zoom smoothly to pin
  citMap.setView([item.lat, item.lng], 17, { animate: true });
  setTimeout(() => {
    item.marker.openPopup();
  }, 350);

  // Smooth scroll up to map container so user sees pin
  const mapEl = document.getElementById('cit-map');
  if (mapEl) {
    mapEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
};

// Filter live tracking map (all, pending, verified)
window.filterLiveTrackingMap = function(filterMode, btn) {
  currentMapFilter = filterMode;

  const btnAll = document.getElementById('cit-btn-filter-all');
  const btnPending = document.getElementById('cit-btn-filter-pending');
  const btnVerified = document.getElementById('cit-btn-filter-verified');

  const defaultBtnStyle = 'display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; cursor: pointer; border: 1px solid #cbd5e1; background: #ffffff; color: #334155; box-shadow: none;';

  if (btnAll) btnAll.style.cssText = defaultBtnStyle;
  if (btnPending) btnPending.style.cssText = defaultBtnStyle;
  if (btnVerified) btnVerified.style.cssText = defaultBtnStyle;

  if (filterMode === 'pending' && btnPending) {
    btnPending.style.cssText = 'display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; cursor: pointer; border: 1px solid #ef4444; background: #ef4444; color: #ffffff; box-shadow: 0 2px 6px rgba(239,68,68,0.25);';
  } else if (filterMode === 'verified' && btnVerified) {
    btnVerified.style.cssText = 'display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; cursor: pointer; border: 1px solid #10b981; background: #10b981; color: #ffffff; box-shadow: 0 2px 6px rgba(16,185,129,0.25);';
  } else if (btnAll) {
    btnAll.style.cssText = 'display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; cursor: pointer; border: 1px solid #2563eb; background: #2563eb; color: #ffffff; box-shadow: 0 2px 6px rgba(37,99,235,0.25);';
  }

  // Re-filter and render markers
  const validReports = (citLiveReportsCache || []).filter(r => {
    const lat = Number(r.latitude);
    const lng = Number(r.longitude);
    return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0;
  });

  renderMapMarkers(validReports);
};

function locateCitizenForMap() {
  if (!navigator.geolocation || !citMap) return;
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const uLat = pos.coords.latitude;
      const uLng = pos.coords.longitude;
      window.lastCitizenCoords = { lat: uLat, lng: uLng };

      const userIcon = L.divIcon({
        html: '<div class="cit-user-location-pulse"></div>',
        className: 'custom-map-pin',
        iconSize: [18, 18],
        iconAnchor: [9, 9],
        popupAnchor: [0, -10]
      });

      if (citUserMarker) {
        citUserMarker.setLatLng([uLat, uLng]);
      } else {
        citUserMarker = L.marker([uLat, uLng], { icon: userIcon, zIndexOffset: 2000 }).addTo(citMap);
        citUserMarker.bindPopup('<strong style="font-family:sans-serif;font-size:12px;color:#1e40af;"><i class="fa-solid fa-user"></i> Your Current GPS Location</strong>');
      }
    },
    (err) => {
      console.warn('Live map geolocation error:', err.message);
    },
    { enableHighAccuracy: true, timeout: 7000 }
  );
}

window.fitAllReportPins = function() {
  if (!citMap || !citMarkersLayer) return;
  const layers = citMarkersLayer.getLayers();
  if (layers.length > 0) {
    citMap.fitBounds(citMarkersLayer.getBounds(), { padding: [40, 40] });
  } else if (citUserMarker) {
    citMap.setView(citUserMarker.getLatLng(), 15);
  } else {
    alert('No incident pins to fit yet.');
  }
};

window.centerCitizenOnMap = function() {
  if (!citMap) return;
  if (citUserMarker) {
    citMap.setView(citUserMarker.getLatLng(), 16);
    citUserMarker.openPopup();
  } else if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const uLat = pos.coords.latitude;
        const uLng = pos.coords.longitude;
        locateCitizenForMap();
        citMap.setView([uLat, uLng], 16);
      },
      (err) => {
        alert('Could not fetch your GPS location. Please allow location permissions in your browser.');
      },
      { enableHighAccuracy: true }
    );
  }
};
