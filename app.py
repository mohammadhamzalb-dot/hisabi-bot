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
            "You are an Arabic accounting bot for small merchants. "
            "Understand all Arabic dialects. "
            "Current records: " + records_str + ". "
            "Rule: badna min fulan = ADD_OM, fulan baddo minna = ADD_OH. "
            "Reply in JSON only: {action, p, a, n, msg}. "
            "Actions: ADD_OM, ADD_OH, PAID_ME, PAID_HIM, QUERY_OM, QUERY_OH, QUERY_PERSON, QUERY_ALL, DELETE_ALL, RECEIPT, UNKNOWN. "
            "msg must be in Arabic."
        )

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        text = message.content[0].text
        text = text.replace('json', '').replace('', '').strip()
        result = json.loads(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"action": "UNKNOWN", "msg": str(e), "p": None, "a": None, "n": ""})

if _name_ == '_main_':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
