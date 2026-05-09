from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import json
import os

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        data = request.json
        user_message = data.get('message', '')
        records = data.get('records', [])
        records_str = json.dumps(records, ensure_ascii=False)

        system_prompt = (
            "You are an Arabic accounting bot. Reply ONLY with valid JSON, nothing else. "
            "No explanation, no markdown, just JSON. "
            "Current records: " + records_str + ". "
            "Actions: ADD_OM=they owe me, ADD_OH=I owe them, PAID_ME, PAID_HIM, QUERY_OM, QUERY_OH, QUERY_PERSON, QUERY_ALL, DELETE_ALL, RECEIPT, UNKNOWN. "
            "Reply format: {\"action\":\"...\",\"p\":\"name or null\",\"a\":number or null,\"n\":\"note\",\"msg\":\"Arabic reply\"}"
        )

        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        text = message.content[0].text.strip()
        if text.startswith(""):
            text = text.split("")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        result = json.loads(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"action": "UNKNOWN", "msg": str(e), "p": None, "a": None, "n": ""})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
