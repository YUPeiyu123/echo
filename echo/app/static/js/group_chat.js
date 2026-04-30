function csrfToken() {
  const meta = document.querySelector("meta[name='csrf-token']");
  return meta ? meta.getAttribute("content") : "";
}

const messagesBox = document.getElementById("groupMessages");
const form = document.getElementById("groupChatForm");
const input = document.getElementById("groupChatInput");

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text || "";
  return div.innerHTML;
}

function renderMessages(messages) {
  messagesBox.innerHTML = messages.map(msg => {
    const cls = msg.is_mine ? "mine" : "theirs";
    return `
      <div class="chat-message ${cls}">
        <div class="bubble">
          <div>${escapeHtml(msg.content)}</div>
          <small>${escapeHtml(msg.sender)} · ${escapeHtml(msg.created_at)}</small>
        </div>
      </div>
    `;
  }).join("");
  messagesBox.scrollTop = messagesBox.scrollHeight;
}

async function loadMessages() {
  try {
    const response = await fetch(`/api/group/${window.GROUP_ID}`);
    const data = await response.json();
    if (data.ok) renderMessages(data.messages);
  } catch (err) {
    console.warn("Group chat load failed", err);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const content = input.value.trim();
  if (!content) return;
  input.value = "";

  try {
    const response = await fetch(`/api/group/${window.GROUP_ID}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken()
      },
      body: JSON.stringify({content})
    });
    const data = await response.json();
    if (data.ok) loadMessages();
  } catch (err) {
    console.warn("Group message send failed", err);
  }
});

loadMessages();
setInterval(loadMessages, 2500);
