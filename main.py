# Create Flask app to host chatbot
from flask import Flask, render_template, request, redirect
from chat import ChatBot

app = Flask(__name__)

model_name = 'sadgpt_model'
chat_history = []
model = ChatBot(model_name)

@app.route('/')
def index():
    return render_template('index.html', chat_history=chat_history, user_icon='user_icon.png', bot_icon='sadgpt.png')

@app.route('/chat', methods=['POST'])
def chat():
    text = request.form['text']
    reply = model.generate_reply(text)
    global chat_history
    chat_history.append((text, reply))
    return redirect('/')


@app.route('/restart')
def restart_chat():
    global model
    model = None
    model = ChatBot(model_name)
    global chat_history
    chat_history = []
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

# {% for user_msg, bot_msg in chat_history %}
# 