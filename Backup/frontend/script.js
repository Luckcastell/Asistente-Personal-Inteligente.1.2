
const API_URL = "http://127.0.0.1:8000";

async function uploadFile() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("Selecciona un archivo primero");

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/upload/`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  alert("Archivo subido correctamente: " + data.file_id);
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (!message) return;

  addMessage("Tú", message);
  input.value = "";

  const formData = new FormData();
  formData.append("message", message);

  const res = await fetch(`${API_URL}/chat/`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  addMessage("Bot", data.response);
}

function addMessage(sender, text) {
  const chatBox = document.getElementById("chatBox");
  const msg = document.createElement("p");
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
