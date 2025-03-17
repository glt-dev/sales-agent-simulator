from flask import Flask, render_template, request, jsonify
from agents.openai_agent import initiate_chat, end_chat, send_message
from dotenv import load_dotenv
from pydub import AudioSegment
import openai, os, json

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

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

@app.route('/audio_transcribe', methods=['POST'])
def audio_transcribe():
    audio_file = request.files['audio']
    audio_webm_path = 'uploaded_audio.webm'
    audio_wav_path = 'converted_audio.wav'

    # Save WebM audio received from browser
    audio_file.save(audio_webm_path)

    # Convert from WebM to WAV (ffmpeg required)
    audio_segment = AudioSegment.from_file(audio_webm_path, format="webm")
    audio_segment.export(audio_wav_path, format="wav")

    # Use OpenAI Whisper for transcription
    with open(audio_wav_path, 'rb') as audio:
        transcript_response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            language="it",
            response_format="json"
        )
        transcript_text = transcript_response.text

    # Clean up temporary files
    os.remove(audio_webm_path)
    os.remove(audio_wav_path)

    return jsonify({"transcript": transcript_text})


if __name__ == '__main__':
    app.run(debug=True)
