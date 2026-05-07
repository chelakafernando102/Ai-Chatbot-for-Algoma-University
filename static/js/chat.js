const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const statusBadge = document.getElementById("statusBadge");

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function createMessage(sender, text, isTyping = false) {
  const message = document.createElement("div");
  message.className = `message ${sender}-message${isTyping ? " typing" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = sender === "user" ? "You" : "AU";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  message.appendChild(avatar);
  message.appendChild(bubble);
  chatWindow.appendChild(message);
  scrollToBottom();

  return message;
}

function setLoading(isLoading) {
  messageInput.disabled = isLoading;
  sendButton.disabled = isLoading;
  sendButton.textContent = isLoading ? "Sending..." : "Send";
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();

    if (data.status === "ok" && data.gemini_configured) {
      statusBadge.textContent = "Gemini connected";
      return;
    }

    if (data.status === "ok") {
      statusBadge.textContent = "Local mode";
      return;
    }

    statusBadge.textContent = "Offline";
  } catch (_error) {
    statusBadge.textContent = "Offline";
  }
}

async function sendMessage(message) {
  createMessage("user", message);
  const typingMessage = createMessage("bot", "Thinking...", true);
  setLoading(true);

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.response || data.error || "Request failed");
    }

    typingMessage.remove();
    createMessage("bot", data.response || "I could not find an answer.");
  } catch (error) {
    typingMessage.remove();
    createMessage("bot", `Something went wrong: ${error.message}`);
  } finally {
    setLoading(false);
    messageInput.focus();
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  messageInput.value = "";
  await sendMessage(message);
});

checkHealth();
messageInput.focus();
