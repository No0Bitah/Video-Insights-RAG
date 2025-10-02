  const API_URL = "http://127.0.0.1:8000";
    let transcriptionComplete = false;

    // File upload handling
    const uploadArea = document.getElementById("uploadArea");
    const fileInput = document.getElementById("fileInput");
    const fileInfo = document.getElementById("fileInfo");
    const fileName = document.getElementById("fileName");
    const removeFile = document.getElementById("removeFile");
    const transcribeBtn = document.getElementById("transcribeBtn");
    const statusMessage = document.getElementById("statusMessage");
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");

    uploadArea.addEventListener("click", () => fileInput.click());

    uploadArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      uploadArea.classList.add("dragover");
    });

    uploadArea.addEventListener("dragleave", () => {
      uploadArea.classList.remove("dragover");
    });

    uploadArea.addEventListener("drop", (e) => {
      e.preventDefault();
      uploadArea.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect();
      }
    });

    fileInput.addEventListener("change", handleFileSelect);

    function handleFileSelect() {
      if (fileInput.files.length) {
        fileName.textContent = fileInput.files[0].name;
        fileInfo.classList.add("show");
        transcribeBtn.disabled = false;
        statusMessage.classList.remove("show");
      }
    }

    removeFile.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      fileInput.value = "";
      fileInfo.classList.remove("show");
      transcribeBtn.disabled = true;
      transcriptionComplete = false;
      sendBtn.disabled = true;
      statusMessage.classList.remove("show");
      document.getElementById("chatBox").innerHTML = "";
    });

    function showStatus(message, type) {
      statusMessage.className = "status-message show " + type;
      statusMessage.innerHTML = type === "loading" 
        ? `<span class="spinner"></span> ${message}`
        : (type === "success" ? "✅ " : "❌ ") + message;
    }

    async function transcribe() {
      if (!fileInput.files.length) {
        showStatus("Please select a file first", "error");
        return;
      }

      // Clear chat box when starting new transcription
      document.getElementById("chatBox").innerHTML = "";
      transcriptionComplete = false;
      sendBtn.disabled = true;

      showStatus("Transcribing... please wait", "loading");
      transcribeBtn.disabled = true;

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      try {
        const res = await fetch(`${API_URL}/transcribe/`, {
          method: "POST",
          body: formData,
        });

        if (!res.ok) throw new Error(`Error: ${res.status}`);

        const data = await res.json();
        showStatus("Transcription complete! You can now chat with the transcript.", "success");
        transcriptionComplete = true;
        sendBtn.disabled = false;
        chatInput.focus();
      } catch (err) {
        console.error(err);
        showStatus("Failed to transcribe file. Please try again.", "error");
        transcribeBtn.disabled = false;
      }
    }

    // Chat functionality
    chatInput.addEventListener("input", function() {
      this.style.height = "auto";
      this.style.height = Math.min(this.scrollHeight, 120) + "px";
    });

    chatInput.addEventListener("keydown", function(event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        if (this.value.trim() !== "" && transcriptionComplete) {
          sendChat();
        }
      }
    });

    async function sendChat() {
      const chatBox = document.getElementById("chatBox");
      const message = chatInput.value.trim();
      
      if (!message || !transcriptionComplete) return;

      // Add user message
      const userMsg = document.createElement("div");
      userMsg.className = "message message-user";
      userMsg.innerHTML = `
        <div class="message-label">You</div>
        <div class="message-content">${escapeHtml(message)}</div>
      `;
      chatBox.appendChild(userMsg);
      chatInput.value = "";
      chatInput.style.height = "auto";
      chatBox.scrollTop = chatBox.scrollHeight;

      // Add loading message
      const loadingMsg = document.createElement("div");
      loadingMsg.className = "message message-assistant";
      loadingMsg.id = "loading-" + Date.now();
      loadingMsg.innerHTML = `
        <div class="message-label">Assistant</div>
        <div class="message-content"><span class="spinner"></span> Thinking...</div>
      `;
      chatBox.appendChild(loadingMsg);
      chatBox.scrollTop = chatBox.scrollHeight;

      sendBtn.disabled = true;

      try {
        const res = await fetch(`${API_URL}/chat/`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ query: message }),
        });

        if (!res.ok) throw new Error(`Error: ${res.status}`);
        const data = await res.json();

        // Replace loading with actual response
        loadingMsg.innerHTML = `
          <div class="message-label">Assistant</div>
          <div class="message-content" id="typing-${loadingMsg.id}"></div>
        `;

        const typingEl = document.getElementById(`typing-${loadingMsg.id}`);
        const text = data.answer;
        let i = 0;

        function typeChar() {
          if (i < text.length) {
            typingEl.textContent += text.charAt(i);
            i++;
            chatBox.scrollTop = chatBox.scrollHeight;
            setTimeout(typeChar, 20);
          } else {
            sendBtn.disabled = false;
          }
        }
        typeChar();

      } catch (err) {
        console.error(err);
        loadingMsg.innerHTML = `
          <div class="message-label">Assistant</div>
          <div class="message-content" style="color: #e53e3e;">Failed to get response. Please try again.</div>
        `;
        sendBtn.disabled = false;
      }
    }

    function escapeHtml(text) {
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }