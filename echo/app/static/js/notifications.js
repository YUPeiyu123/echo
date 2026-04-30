function unreadLabel(n) {
  if (!n || n <= 0) return "";
  return n > 9 ? "9+" : String(n);
}

function csrfToken() {
  const meta = document.querySelector("meta[name='csrf-token']");
  return meta ? meta.getAttribute("content") : "";
}

let lastSeenNotificationId = Number(localStorage.getItem("lastSeenNotificationId") || "0");

function showToast(item) {
  const area = document.getElementById("notificationToastArea");
  if (!area) return;

  const toast = document.createElement("div");
  toast.className = "mini-toast";
  toast.innerHTML = `
    <strong>${escapeHtml(item.title)}</strong>
    <div>${escapeHtml(item.body)}</div>
  `;

  if (item.link) {
    toast.addEventListener("click", () => {
      window.location.href = item.link;
    });
  }

  area.appendChild(toast);
  setTimeout(() => toast.classList.add("show"), 20);
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text || "";
  return div.innerHTML;
}

async function pollNotifications() {
  try {
    const response = await fetch("/api/notifications");
    const data = await response.json();
    if (!data.ok) return;

    const badge = document.getElementById("chatBadge");
    if (badge) {
      const label = unreadLabel(data.chat_unread);
      if (label) {
        badge.textContent = label;
        badge.classList.remove("d-none");
      } else {
        badge.classList.add("d-none");
      }
    }

    const newest = data.notifications.find(n => !n.is_read);
    if (newest && newest.id > lastSeenNotificationId) {
      showToast(newest);
      lastSeenNotificationId = newest.id;
      localStorage.setItem("lastSeenNotificationId", String(lastSeenNotificationId));
    }
  } catch (err) {
    console.warn("Notification polling failed", err);
  }
}

pollNotifications();
setInterval(pollNotifications, 5000);
