function csrfToken() {
  const meta = document.querySelector("meta[name='csrf-token']");
  return meta ? meta.getAttribute("content") : "";
}

async function heartbeat() {
  try {
    await fetch("/api/heartbeat", {
      method: "POST",
      headers: {"X-CSRFToken": csrfToken()}
    });
  } catch (err) {
    console.warn("Heartbeat failed", err);
  }
}

async function refreshOnlineList() {
  try {
    const response = await fetch("/api/online");
    const data = await response.json();
    if (!data.ok) return;

    const list = document.getElementById("onlineList");
    if (!list) return;

    if (data.users.length === 0) {
      list.innerHTML = '<p class="text-muted mb-0">No online users.</p>';
      return;
    }

    list.innerHTML = data.users.map(user => `
      <div class="online-row">
        <span class="online-dot"></span>
        <a href="/profile/${encodeURIComponent(user.username)}">${user.username}</a>
      </div>
    `).join("");
  } catch (err) {
    console.warn("Online refresh failed", err);
  }
}

heartbeat();
refreshOnlineList();
setInterval(heartbeat, 30000);
setInterval(refreshOnlineList, 10000);
