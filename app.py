from flask import Flask, render_template, request, jsonify
from agents.openai_agent import initiate_chat, end_chat, send_message
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales_team')
def sales_team():
    with open('data/sales_team.json', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/archetypes')
def archetypes():
    with open('data/archetypes.json', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/start_chat', methods=['POST'])
def start_chat():
    data = request.json
    session_id, reply = initiate_chat(data['sales_person'], data['archetype'], data['business_line'])
    return jsonify({"session_id": session_id, "reply": reply})

@app.route('/send_message', methods=['POST'])
def send_message_route():
    data = request.json
    reply = send_message(data['session_id'], data['message'])
    return jsonify({"reply": reply})


@app.route('/end_chat', methods=['POST'])
def terminate_chat():
    data = request.json
    feedback = end_chat(data['session_id'])
    return jsonify(feedback)

if __name__ == '__main__':
    app.run(debug=True)
