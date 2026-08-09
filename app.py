from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Grab the JSON data the browser sent.
    data = request.get_json()

    # Pull out the 'message' field. .get() is safer than data['message'] —
    # it won't crash if the key is missing, it just returns None.
    user_message = data.get('message', '')

    # For now we just echo it back. Real AI logic replaces this in Week 2.
    reply_text = f"You said: {user_message}"

    # jsonify converts this Python dict into a proper JSON HTTP response.
    return jsonify({'reply': reply_text})

app.run(debug=True)