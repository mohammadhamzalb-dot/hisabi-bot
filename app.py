from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import json
import os

app = Flask(_name_, static_folder='static')
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    records = data.get('records', [])
    
    system_prompt = f"""أنت بوت محاسبة ذكي للتجار الصغار. تفهم كل اللهجات العربية.

السجلات الحالية:
{json.dumps(records, ensure_ascii=False)}

أنواع العمليات:
- ADD_OM: بدهم إليّ. أمثلة: "محمد بدي منو 50" / "خالد بدنا منو 100" / "سجل على أحمد 30"
- ADD_OH: علي لهم. أمثلة: "سمير بدو منا 90" / "علي لخالد 50" / "دفعت لسامر 30"  
- PAID_ME: شخص دفع لي. أمثلة: "محمد دفع 20" / "استلمت من خالد 50"
- PAID_HIM: دفعت لشخص. أمثلة: "دفعت لأحمد 30" / "سددت لخالد 100"
- QUERY_OM: من يدين لي
- QUERY_OH: ما علي
- QUERY_PERSON: سؤال عن شخص
- QUERY_ALL: كل الديون
- DELETE_ALL: مسح كل شيء
- RECEIPT: طلب وصل دفع. أمثلة: "عطيني وصل لمحمد" / "وصل دفعة خالد"
- UNKNOWN: لا يفهم

قاعدة ذهبية:
- "بدنا من فلان" = ADD_OM (هو مدين لي)
- "فلان بدو منا" = ADD_OH (أنا مدين له)

رد بـ JSON فقط:
{{"action":"...","p":"اسم","a":رقم_أو_null,"n":"ملاحظة","msg":"رسالة للمستخدم"}}"""

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

if _name_ == '_main_':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
