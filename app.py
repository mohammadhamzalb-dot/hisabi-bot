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
        
        system_prompt = f"""أنت بوت محاسبة ذكي للتجار الصغار. تفهم كل اللهجات العربية.
السجلات الحالية: {json.dumps(records, ensure_ascii=False)}
قاعدة: "بدنا من فلان" = ADD_OM، "فلان بدو منا" = ADD_OH
رد بـ JSON فقط: {{"action":"...","p":"ا
