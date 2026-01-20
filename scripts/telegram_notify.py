"""
Telegram 通知模块
"""

import requests


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """发送 Telegram 文本消息"""
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f'Telegram 消息发送失败: {e}')
        return False


def send_telegram_photo(bot_token: str, chat_id: str, photo_path: str, caption: str = '') -> bool:
    """发送 Telegram 图片"""
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, data=data, files=files, timeout=60)
            response.raise_for_status()
        return True
    except Exception as e:
        print(f'Telegram 图片发送失败: {e}')
        return False
