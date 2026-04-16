from fastapi import FastAPI, Request
import re
import pyodide_http
pyodide_http.patch_all()
import requests

app = FastAPI()

BOT_TOKEN = "7811494395:AAGYHFwy-pnblT5WU-mzBoSA-nH1RDLc96o"

def extract_username(text):
    text = text.strip()
    if text.startswith('@'): return text[1:]
    patterns = [r't\.me/([a-zA-Z0-9_]+)', r'telegram\.me/([a-zA-Z0-9_]+)']
    for p in patterns:
        m = re.search(p, text)
        if m: return m.group(1)
    return text if re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,}$', text) else None

@app.get("/")
async def root():
    return {"status": "Bot is running"}

@app.post("/")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')

            if text == '/start':
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                             json={'chat_id': chat_id, 'text': "👋 发送群组链接给我！"})
            elif text:
                username = extract_username(text)
                if username:
                    res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChat", 
                                     params={'chat_id': f'@{username}'}).json()
                    if res.get('ok'):
                        cid = res['result']['id']
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                                     json={'chat_id': chat_id, 'text': f"✅ ID: <code>{cid}</code>", 'parse_mode': 'HTML'})
                    else:
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                                     json={'chat_id': chat_id, 'text': "❌ 找不到该群组"})
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}
