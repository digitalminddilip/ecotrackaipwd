// CleanConnect Browser Voice AI Assistant (100% Free Lifetime)

(function () {
  // Check Speech API Support
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const isSpeechSupported = Boolean(SpeechRecognition);

  let recognition = null;
  let isListening = false;
  let isSpeaking = false;
  let synth = window.speechSynthesis;
  let currentUtterance = null;

  // DOM Elements
  let fabBtn = null;
  let modalEl = null;
  let waveContainer = null;
  let statusPill = null;
  let chatBody = null;
  let textInput = null;
  let micControlBtn = null;

  function initSpeechRecognition() {
    if (!isSpeechSupported) return;

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-IN"; // Good for English and Indian accent

    recognition.onstart = () => {
      isListening = true;
      updateUIState("listening");
    };

    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (interimTranscript) {
        updateInterimBubble(interimTranscript);
      }

      if (finalTranscript) {
        addUserBubble(finalTranscript);
        processUserQuery(finalTranscript);
      }
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      isListening = false;
      updateUIState("ready");
      if (event.error === "not-allowed") {
        addAIBubble("Microphone permission was denied. Please allow microphone access or type your question below.");
      }
    };

    recognition.onend = () => {
      isListening = false;
      if (!isSpeaking) {
        updateUIState("ready");
      }
    };
  }

  function updateUIState(state) {
    if (!statusPill || !waveContainer || !fabBtn || !micControlBtn) return;

    if (state === "listening") {
      statusPill.textContent = "Listening...";
      waveContainer.classList.add("active");
      fabBtn.classList.add("active");
      micControlBtn.classList.add("listening");
    } else if (state === "thinking") {
      statusPill.textContent = "Thinking...";
      waveContainer.classList.remove("active");
      fabBtn.classList.remove("active");
      micControlBtn.classList.remove("listening");
    } else if (state === "speaking") {
      statusPill.textContent = "Speaking...";
      waveContainer.classList.add("active");
      fabBtn.classList.remove("active");
      micControlBtn.classList.remove("listening");
    } else {
      statusPill.textContent = "Ready";
      waveContainer.classList.remove("active");
      fabBtn.classList.remove("active");
      micControlBtn.classList.remove("listening");
    }
  }

  function toggleListening() {
    stopSpeaking();

    if (!isSpeechSupported) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari, or type your message below.");
      return;
    }

    if (isListening) {
      recognition.stop();
      isListening = false;
      updateUIState("ready");
    } else {
      try {
        recognition.start();
      } catch (err) {
        console.warn("Recognition start failed:", err);
      }
    }
  }

  function speakText(text) {
    if (!synth) return;
    stopSpeaking();

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.rate = 1.0;
    currentUtterance.pitch = 1.0;

    // Pick a natural voice if available
    const voices = synth.getVoices();
    const preferredVoice = voices.find(
      (v) => v.lang.startsWith("en-IN") || v.lang.startsWith("en-US") || v.lang.startsWith("en-GB")
    );
    if (preferredVoice) {
      currentUtterance.voice = preferredVoice;
    }

    currentUtterance.onstart = () => {
      isSpeaking = true;
      updateUIState("speaking");
    };

    currentUtterance.onend = () => {
      isSpeaking = false;
      updateUIState("ready");
    };

    currentUtterance.onerror = () => {
      isSpeaking = false;
      updateUIState("ready");
    };

    synth.speak(currentUtterance);
  }

  function stopSpeaking() {
    if (synth && synth.speaking) {
      synth.cancel();
    }
    isSpeaking = false;
  }

  function addUserBubble(text) {
    const interim = document.getElementById("cc-interim-bubble");
    if (interim) interim.remove();

    const bubble = document.createElement("div");
    bubble.className = "cc-bubble cc-bubble-user";
    bubble.textContent = text;
    chatBody.appendChild(bubble);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function updateInterimBubble(text) {
    let interim = document.getElementById("cc-interim-bubble");
    if (!interim) {
      interim = document.createElement("div");
      interim.id = "cc-interim-bubble";
      interim.className = "cc-bubble cc-bubble-user";
      interim.style.opacity = "0.7";
      chatBody.appendChild(interim);
    }
    interim.textContent = text + "...";
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function addAIBubble(text, actionInfo) {
    const bubble = document.createElement("div");
    bubble.className = "cc-bubble cc-bubble-ai";
    bubble.textContent = text;

    if (actionInfo && actionInfo.type === "fill_report") {
      const actionBadge = document.createElement("div");
      actionBadge.className = "cc-bubble-action";
      actionBadge.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> <strong>Form Prepared:</strong> ${actionInfo.location || "Location set"} (${actionInfo.category || "waste"}). Take a photo and click submit!`;
      bubble.appendChild(actionBadge);
    }

    chatBody.appendChild(bubble);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  async function processUserQuery(query) {
    updateUIState("thinking");

    let token = localStorage.getItem("cleanconnect_token");
    let headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const response = await fetch("/api/voice-assistant", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ query: query })
      });

      if (!response.ok) {
        throw new Error("HTTP error " + response.status);
      }

      const data = await response.json();
      const reply = data.reply || "I received your query.";
      const action = data.action;

      addAIBubble(reply, action);
      speakText(reply);

      // Execute automated actions on the page
      if (action && action.type === "fill_report") {
        executeFormFillAction(action);
      }
    } catch (err) {
      console.error("Voice assistant query error:", err);
      const fallbackReply = "I am ready to help. You can report waste or check your complaints anytime.";
      addAIBubble(fallbackReply);
      speakText(fallbackReply);
    }
  }

  function executeFormFillAction(action) {
    // 1. Switch view to 'new-report' if in citizen mode
    if (typeof showCitView === "function") {
      const newReportLink = document.querySelector(".col-nav-link");
      showCitView("new-report", newReportLink);
    }

    // 2. Populate fields
    if (action.location) {
      const locInput = document.getElementById("report-location");
      if (locInput) locInput.value = action.location;
    }

    if (action.description) {
      const descInput = document.querySelector('textarea[name="description"]');
      if (descInput) descInput.value = action.description;
    }

    // 3. Highlight image input
    const imgInput = document.getElementById("image");
    if (imgInput) {
      imgInput.focus();
      imgInput.style.outline = "2px solid #10b981";
      setTimeout(() => {
        if (imgInput) imgInput.style.outline = "none";
      }, 4000);
    }

    const msg = document.getElementById("report-message");
    if (msg) {
      msg.style.color = "#10b981";
      msg.textContent = "AI voice assisted: Location and details filled. Upload photo to finish!";
    }
  }

  function toggleModal() {
    if (!modalEl) return;
    const isOpen = modalEl.classList.contains("open");
    if (isOpen) {
      modalEl.classList.remove("open");
      stopSpeaking();
      if (isListening && recognition) recognition.stop();
    } else {
      modalEl.classList.add("open");
      // Auto-focus input if on desktop
      if (window.innerWidth > 600 && textInput) {
        textInput.focus();
      }
    }
  }

  function setupDOM() {
    // 1. Create Floating Button
    fabBtn = document.createElement("button");
    fabBtn.className = "cc-voice-fab";
    fabBtn.title = "CleanConnect Voice AI (100% Free)";
    fabBtn.innerHTML = `
      <i class="fa-solid fa-microphone"></i>
      <span class="cc-voice-badge">AI</span>
    `;
    fabBtn.addEventListener("click", () => {
      toggleModal();
      if (modalEl.classList.contains("open") && !isListening) {
        toggleListening();
      }
    });
    document.body.appendChild(fabBtn);

    // 2. Create Assistant Modal
    modalEl = document.createElement("div");
    modalEl.className = "cc-voice-modal";
    modalEl.innerHTML = `
      <div class="cc-voice-header">
        <div class="cc-voice-header-title">
          <i class="fa-solid fa-robot"></i>
          <span>CleanConnect Voice AI</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="cc-voice-status-pill" id="cc-voice-status">Ready</span>
          <button class="cc-voice-close-btn" id="cc-voice-close" title="Close">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>

      <div class="cc-voice-wave-container" id="cc-voice-wave">
        <div class="cc-voice-bar"></div>
        <div class="cc-voice-bar"></div>
        <div class="cc-voice-bar"></div>
        <div class="cc-voice-bar"></div>
        <div class="cc-voice-bar"></div>
      </div>

      <div class="cc-voice-body" id="cc-voice-chat-body">
        <div class="cc-bubble cc-bubble-ai">
          Hello! I am your 100% Free Voice Assistant. Click the mic or tap a prompt below to speak!
        </div>
      </div>

      <div class="cc-voice-chips">
        <button class="cc-chip" data-prompt="How do I report garbage?">How to report?</button>
        <button class="cc-chip" data-prompt="Report garbage near Main Road">Report garbage</button>
        <button class="cc-chip" data-prompt="What is the difference between wet and dry waste?">Wet vs Dry waste</button>
        <button class="cc-chip" data-prompt="What is the status of my reports?">Check my status</button>
      </div>

      <div class="cc-voice-footer">
        <button class="cc-voice-mute-btn" id="cc-voice-mute" title="Stop Speaking">
          <i class="fa-solid fa-volume-xmark"></i>
        </button>
        
        <div class="cc-voice-input-wrapper">
          <input type="text" id="cc-voice-input" placeholder="Speak or type a question..." autocomplete="off">
          <button class="cc-voice-send-btn" id="cc-voice-send" title="Send">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </div>

        <button class="cc-voice-mic-control" id="cc-voice-mic" title="Click to speak">
          <i class="fa-solid fa-microphone"></i>
        </button>
      </div>
    `;
    document.body.appendChild(modalEl);

    // Cache elements
    waveContainer = document.getElementById("cc-voice-wave");
    statusPill = document.getElementById("cc-voice-status");
    chatBody = document.getElementById("cc-voice-chat-body");
    textInput = document.getElementById("cc-voice-input");
    micControlBtn = document.getElementById("cc-voice-mic");

    // Event Listeners
    document.getElementById("cc-voice-close").addEventListener("click", toggleModal);
    micControlBtn.addEventListener("click", toggleListening);
    document.getElementById("cc-voice-mute").addEventListener("click", stopSpeaking);

    // Send Button & Enter Key
    const submitText = () => {
      const text = textInput.value.trim();
      if (!text) return;
      textInput.value = "";
      addUserBubble(text);
      processUserQuery(text);
    };

    document.getElementById("cc-voice-send").addEventListener("click", submitText);
    textInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") submitText();
    });

    // Quick Prompt Chips
    modalEl.querySelectorAll(".cc-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const prompt = chip.getAttribute("data-prompt");
        addUserBubble(prompt);
        processUserQuery(prompt);
      });
    });

    initSpeechRecognition();
  }

  // Initialize once DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupDOM);
  } else {
    setupDOM();
  }
})();
