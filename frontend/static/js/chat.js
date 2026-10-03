// ==========================================
// HUMSAFAR CHAT.JS
// ==========================================

// Get the input box
const input = document.getElementById("messageInput");

// Create ONE conversation ID for this browser chat session
const conversationId = crypto.randomUUID();

console.log("=================================");
console.log("HUMSAFAR CHAT STARTED");
console.log("Conversation ID:", conversationId);
console.log("=================================");

// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage() {
  // Get the text typed by the user
  const text = input.value.trim();

  // Do not send empty messages
  if (!text) {
    return;
  }

  console.log("User message:", text);
  console.log("Conversation ID:", conversationId);

  // ==========================================
  // DATA WE ARE SENDING TO FLASK
  // ==========================================

  const requestData = {
    message: text,
    conversation_id: conversationId,
  };

  console.log("Data being sent to Flask:", requestData);

  try {
    // ==========================================
    // SEND REQUEST TO FLASK
    // ==========================================

    const response = await fetch("/chat", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(requestData),
    });

    // ==========================================
    // CHECK HTTP RESPONSE
    // ==========================================

    if (!response.ok) {
      console.error(
        "Flask returned an error:",
        response.status,
        response.statusText,
      );

      return;
    }

    // ==========================================
    // GET FLASK RESPONSE
    // ==========================================

    const data = await response.json();

    console.log("HUMSAFAR response:", data);

    // ==========================================
    // CLEAR INPUT BOX
    // ==========================================

    input.value = "";

    // Put cursor back in input
    input.focus();
  } catch (error) {
    console.error("Error communicating with HUMSAFAR:", error);
  }
}
