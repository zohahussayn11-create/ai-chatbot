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
function handleSend() {
  const text = chatInput.value.trim(); // .trim() removes accidental leading/trailing spaces

  // Don't send empty messages.
  if (text === '') {
    return;
  }

  // Add the user's message as a bubble on the right.
  addMessage(text, 'user-message');

  // Clear the input box so it's ready for the next message.
  chatInput.value = '';

  // NOTE: there's no real AI here yet — that comes on Day 8.
  // For now we just fake a bot reply so the interaction feels complete.
  setTimeout(() => {
    addMessage("(This is a placeholder reply — real AI comes in Week 2!)", 'bot-message');
  }, 500);
}

// Run handleSend() when the button is clicked.
sendBtn.addEventListener('click', handleSend);

// Also run it when the user presses Enter while typing in the input box.
chatInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    handleSend();
  }
});