// Grab the three elements we need to work with.
// querySelector('#id') looks for an element with that id (the # matches how you'd write it in CSS).
const chatWindow = document.querySelector('#chat-window');
const chatInput = document.querySelector('#chat-input');
const sendBtn = document.querySelector('#send-btn');

// Builds a short "3:45 PM" style timestamp for the current moment.
function getTimestamp() {
  return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

// This function builds a new message bubble (with a timestamp) and adds it to the chat window.
function addMessage(text, sender) {
  // Create a new <div> element in memory (not on the page yet).
  const messageDiv = document.createElement('div');

  // Give it the same classes our CSS already styles.
  // sender will be either 'user-message' or 'bot-message'.
  messageDiv.classList.add('message', sender);

  // The message text itself.
  const textSpan = document.createElement('span');
  textSpan.classList.add('message-text');

  if (sender === 'bot-message') {
    // Bot replies often contain Markdown (**, ###, lists, etc).
    // marked.parse() converts that Markdown into real HTML so it renders
    // properly instead of showing the raw symbols.
    textSpan.innerHTML = marked.parse(text);
  } else {
    // User input stays as plain text (textContent, not innerHTML) —
    // this avoids ever accidentally running HTML/JS someone typed.
    textSpan.textContent = text;
  }

  // A small timestamp under the text.
  const timeSpan = document.createElement('span');
  timeSpan.classList.add('message-time');
  timeSpan.textContent = getTimestamp();

  messageDiv.appendChild(textSpan);
  messageDiv.appendChild(timeSpan);

  // Actually insert the new bubble into the page, at the end of the chat window.
  chatWindow.appendChild(messageDiv);

  // Auto-scroll to the bottom so the newest message is always visible.
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Builds and inserts the "typing..." indicator bubble, returns it so we can remove it later.
function showTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
  typingDiv.innerHTML = '<span></span><span></span><span></span>';
  chatWindow.appendChild(typingDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return typingDiv;
}

// This function runs every time the user sends a message (click OR Enter key).
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

  // Show the animated typing indicator while we wait for a reply.
  const typingBubble = showTypingIndicator();

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

    // Remove the typing indicator now that we have a real response.
    typingBubble.remove();

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
    typingBubble.remove();
    addMessage("Something went wrong connecting to the server. Please try again.", 'bot-message');
  }
}

// Initial greeting from the bot.
addMessage("Hi! I'm your AI assistant. What help can I do for you today?", 'bot-message');

// Run handleSend() when the button is clicked.
sendBtn.addEventListener('click', handleSend);

// Also run it when the user presses Enter while typing in the input box.
chatInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    handleSend();
  }
});