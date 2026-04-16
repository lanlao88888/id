from fastapi import FastAPI, Request
import requests
import re

app = FastAPI()

BOT_TOKEN = "7811494395:AAGYHFwy-pnblT5WU-mzBoSA-nH1RDLc96o"

def extract_username(text):
    text = text.strip()
    if text.startswith('@'):
        return text[1:]
    patterns = [r't\.me/([a-zA-Z0-9_]+)', r'telegram\.me/([a-zA-Z0-9_]+)']
    for pattern in patterns:
        match = re.search(pattern, text)
        if match: return match.group(1)
    return text if re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,}$', text) else None

def get_chat_id(username):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    response = requests.get(url, params={'chat_id': f'@{username}'})
    return response.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})

# 核心修改：通过 Webhook 接收消息
@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')

        if text == '/start':
            send_message(chat_id, "👋 发送群组链接给我，我会返回群组ID！")
        elif text:
            username = extract_username(text)
            if username:
                result = get_chat_id(username)
                if result['ok']:
                    chat = result['result']
                    info = f"✅ <b>群组信息</b>\n\n<b>ID:</b> <code>{chat['id']}</code>"
                    send_message(chat_id, info)
                else:
                    send_message(chat_id, "❌ 无法获取群组信息")
    
    return {"status": "ok"}
