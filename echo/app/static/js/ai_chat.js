function csrfToken() {
  const meta = document.querySelector("meta[name='csrf-token']");
  return meta ? meta.getAttribute("content") : "";
}

const messagesBox = document.getElementById("aiMessages");
const form = document.getElementById("aiChatForm");
const input = document.getElementById("aiChatInput");

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text || "";
  return div.innerHTML;
}

function addMessage(text, mine, label) {
  const row = document.createElement("div");
  row.className = "chat-message " + (mine ? "mine" : "theirs");
  row.innerHTML = `
    <div class="bubble">
      <div>${escapeHtml(text)}</div>
      <small>${escapeHtml(label)}</small>
    </div>
  `;
  messagesBox.appendChild(row);
  messagesBox.scrollTop = messagesBox.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  addMessage(message, true, "You");

  const loading = "Thinking...";
  addMessage(loading, false, "AI Game Assistant");

  try {
    const response = await fetch("/api/ai/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken()
      },
      body: JSON.stringify({message})
    });

    const data = await response.json();
    const bubbles = messagesBox.querySelectorAll(".chat-message.theirs .bubble div");
    if (bubbles.length) bubbles[bubbles.length - 1].textContent = data.ok ? data.reply : data.error;
  } catch (err) {
    const bubbles = messagesBox.querySelectorAll(".chat-message.theirs .bubble div");
    if (bubbles.length) bubbles[bubbles.length - 1].textContent = "AI assistant is unavailable right now.";
  }
});
