// Grab the three elements we need to work with.
// querySelector('#id') looks for an element with that id (the # matches how you'd write it in CSS).
const chatWindow = document.querySelector('#chat-window');
const chatInput = document.querySelector('#chat-input');
const sendBtn = document.querySelector('#send-btn');

// This function builds a new message bubble and adds it to the chat window.
function addMessage(text, sender) {
  // Create a new <div> element in memory (not on the page yet).
  const messageDiv = document.createElement('div');

  // Give it the same classes our CSS already styles.
  // sender will be either 'user-message' or 'bot-message'.
  messageDiv.classList.add('message', sender);

  // Set the visible text inside the bubble.
  // textContent (not innerHTML) is safer — it won't accidentally run HTML/JS someone typed.
  messageDiv.textContent = text;

  // Actually insert the new bubble into the page, at the end of the chat window.
  chatWindow.appendChild(messageDiv);

  // Auto-scroll to the bottom so the newest message is always visible.
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// This function runs every time the user sends a message.
// It's 'async' because fetch() takes time (a real network request) and we
// need to 'await' its result instead of moving on before it finishes.
async function handleSend() {
  const text = chatInput.value.trim(); // .trim() removes accidental leading/trailing spaces

  // Don't send empty messages.
  if (text === '') {
    return;
  }

  // Add the user's message as a bubble on the right, immediately.
  addMessage(text, 'user-message');

  // Clear the input box so it's ready for the next message.
  chatInput.value = '';

  try {
    // Send the message to our Flask backend.
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json' // tells Flask we're sending JSON
      },
      body: JSON.stringify({ message: text }) // JS object -> JSON string
    });

    // Convert Flask's JSON response back into a JS object.
    const data = await response.json();

    if (data.error) {
      // Flask caught a problem (empty input, API failure, etc.) and sent
      // back a friendly message in data.error instead of data.reply.
      addMessage(data.error, 'bot-message');
    } else {
      // data.reply is whatever Flask's jsonify({'reply': ...}) sent back.
      addMessage(data.reply, 'bot-message');
    }

  } catch (error) {
    // This catches total failures — e.g. no internet connection at all,
    // where fetch() itself throws instead of even reaching Flask.
    addMessage("Something went wrong connecting to the server. Please try again.", 'bot-message');
  }
}
addMessage("Hi! I'm your AI assistant. What help can I do for you today?", 'bot-message');
// Run handleSend() when the button is clicked.
sendBtn.addEventListener('click', handleSend);

// Also run it when the user presses Enter while typing in the input box.
chatInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    handleSend();
  }
});