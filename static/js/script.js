const API_URL = "http://127.0.0.1:8000";

async function transcribe() {
  const fileInput = document.getElementById("fileInput");
  const statusBox = document.getElementById("transcribeStatus");
  if (!fileInput.files.length) {
    alert("Please select a file first.");
    return;
  }

  statusBox.textContent = "⏳ Transcribing... please wait.";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch(`${API_URL}/transcribe/`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error(`Error: ${res.status}`);

    const data = await res.json();
    statusBox.textContent = "✅ Transcription complete!";
  } catch (err) {
    console.error(err);
    statusBox.textContent = "❌ Failed to transcribe file.";
  }
}

document.getElementById("chatInput").addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    event.preventDefault(); // Prevent newline
    if (this.value.trim() !== "") {
      sendChat();
    }
  }
});

async function sendChat() {
  const chatBox = document.getElementById("chatBox");
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  chatBox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
  input.value = "";

  const loadingId = "loading-" + Date.now();
  chatBox.innerHTML += `<div id="${loadingId}" style="margin:5px 0; padding:5px; background:#eef; border-radius:6px; font-style:italic; color:#555;">
    🤔 Assistant is thinking...
  </div>`;
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch(`${API_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ query: message}),

    });


    if (!res.ok) throw new Error(`Error: ${res.status}`);
    const data = await res.json();

    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
      loadingEl.outerHTML = `<div id="reply-${loadingId}" style="margin:5px 0; padding:5px; background:#eef; border-radius:6px;">
        <strong>Assistant:</strong> <span id="typing-${loadingId}"></span>
      </div>`;
    }

    const typingEl = document.getElementById(`typing-${loadingId}`);
    const text = data.answer;
    let i = 0;

    function typeChar() {
      if (i < text.length) {
        typingEl.textContent += text.charAt(i);
        i++;
        chatBox.scrollTop = chatBox.scrollHeight;
        setTimeout(typeChar, 30);
      }
    }
    typeChar();

  } catch (err) {
    console.error(err);
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
      loadingEl.outerHTML = `<div style="color:red;">❌ Error fetching reply.</div>`;
    }
  }
}
