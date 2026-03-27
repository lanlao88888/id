import requests
import re
import time

BOT_TOKEN = "7811494395:AAGYHFwy-pnblT5WU-mzBoSA-nH1RDLc96o"


def extract_username(text):
    """从文本中提取用户名"""
    text = text.strip()

    # 处理 @username
    if text.startswith('@'):
        return text[1:]

    # 处理各种链接
    patterns = [
        r't\.me/([a-zA-Z0-9_]+)',
        r'telegram\.me/([a-zA-Z0-9_]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return text if re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,}$', text) else None


def get_chat_id(username):
    """获取群组ID"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    response = requests.get(url, params={'chat_id': f'@{username}'})
    return response.json()


def send_message(chat_id, text):
    """发送消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})


def main():
    last_update_id = 0
    print("机器人已启动，等待消息...")

    while True:
        try:
            # 获取更新
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {'offset': last_update_id + 1, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            data = response.json()

            if data['ok'] and data['result']:
                for update in data['result']:
                    last_update_id = update['update_id']

                    if 'message' in update:
                        msg = update['message']
                        chat_id = msg['chat']['id']
                        text = msg.get('text', '')

                        # 处理命令
                        if text == '/start':
                            send_message(chat_id,
                                         "👋 发送群组链接给我，我会返回群组ID！\n"
                                         "例如：https://t.me/username 或 @groupname")

                        elif text:
                            # 提取用户名
                            username = extract_username(text)

                            if username:
                                send_message(chat_id, f"🔍 正在查询 @{username}...")

                                # 获取群组信息
                                result = get_chat_id(username)

                                if result['ok']:
                                    chat = result['result']
                                    info = f"""
✅ <b>群组信息</b>

<b>ID:</b> <code>{chat['id']}</code>
<b>类型:</b> {chat['type']}
<b>标题:</b> {chat.get('title', 'N/A')}
                                    """
                                    if 'username' in chat:
                                        info += f"\n<b>用户名:</b> @{chat['username']}"
                                    if 'member_count' in chat:
                                        info += f"\n<b>成员数:</b> {chat['member_count']}"

                                    send_message(chat_id, info)
                                else:
                                    send_message(chat_id,
                                                 f"❌ 无法获取群组信息\n\n"
                                                 f"原因：{result.get('description', '未知错误')}\n\n"
                                                 f"可能机器人不在该群组中")
                            else:
                                send_message(chat_id, "❌ 无法识别链接格式")

            time.sleep(1)

        except Exception as e:
            print(f"错误: {e}")
            time.sleep(3)


if __name__ == '__main__':
    main()