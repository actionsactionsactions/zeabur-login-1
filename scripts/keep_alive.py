"""
Zeabur Keep Alive Script (Python)
使用 Playwright 模拟浏览器登录，保持账户活跃
登录成功后发送 Telegram 通知和截图
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright
from update_secret import update_secret
from telegram_notify import send_telegram_message, send_telegram_photo

ZEABUR_DASHBOARD_URL = 'https://zeabur.com/projects'
SCREENSHOT_PATH = '/tmp/zeabur_dashboard.png'


def main():
    cookie_string = os.environ.get('ZEABUR_COOKIE')
    repo_token = os.environ.get('REPO_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    tg_bot_token = os.environ.get('TG_BOT_TOKEN')
    tg_chat_id = os.environ.get('TG_CHAT_ID')

    if not cookie_string:
        print('❌ 错误: ZEABUR_COOKIE 环境变量未设置')
        sys.exit(1)

    print('🚀 启动浏览器...')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # 解析并设置 Cookie
        cookies = parse_cookies(cookie_string)
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print('📡 访问 Zeabur 控制台...')
            page.goto(ZEABUR_DASHBOARD_URL, wait_until='networkidle')
            
            # 检查登录状态
            is_logged_in = check_login_status(page)
            
            if not is_logged_in:
                error_msg = '❌ 登录失败: Cookie 可能已过期'
                print(error_msg)
                if tg_bot_token and tg_chat_id:
                    send_telegram_message(tg_bot_token, tg_chat_id, error_msg)
                sys.exit(1)
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'✅ 登录成功！')
            print(f'⏰ 执行时间: {now}')
            
            # 截图
            page.screenshot(path=SCREENSHOT_PATH, full_page=False)
            print(f'📸 截图已保存: {SCREENSHOT_PATH}')
            
            # 发送 Telegram 通知
            if tg_bot_token and tg_chat_id:
                message = f'✅ Zeabur 保活成功！\n⏰ 时间: {now}'
                send_telegram_message(tg_bot_token, tg_chat_id, message)
                send_telegram_photo(tg_bot_token, tg_chat_id, SCREENSHOT_PATH, caption='Zeabur 控制台截图')
                print('📤 Telegram 通知已发送')
            
            # 提取并更新 Cookie
            new_cookies = context.cookies()
            new_cookie_string = format_cookies(new_cookies)
            
            if repo_token and repo and new_cookie_string != cookie_string:
                print('🔄 检测到 Cookie 变化，正在更新 GitHub Secret...')
                owner, repo_name = repo.split('/')
                update_secret(repo_token, owner, repo_name, 'ZEABUR_COOKIE', new_cookie_string)
                print('✅ GitHub Secret 已更新')
        
        except Exception as e:
            error_msg = f'❌ 执行失败: {str(e)}'
            print(error_msg)
            if tg_bot_token and tg_chat_id:
                send_telegram_message(tg_bot_token, tg_chat_id, error_msg)
            sys.exit(1)
        
        finally:
            browser.close()


def check_login_status(page) -> bool:
    """检查登录状态"""
    try:
        url = page.url
        if '/login' in url:
            return False
        
        page.wait_for_timeout(2000)
        title = page.title()
        return 'Zeabur' in title and 'Login' not in title
    except:
        return False


def parse_cookies(cookie_string: str) -> list:
    """解析 Cookie 字符串为 Playwright 格式"""
    cookies = []
    for cookie in cookie_string.split(';'):
        parts = cookie.strip().split('=', 1)
        if len(parts) == 2:
            name, value = parts
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.zeabur.com',
                'path': '/',
            })
    return cookies


def format_cookies(cookies: list) -> str:
    """格式化 Cookies 为字符串"""
    return '; '.join(
        f"{c['name']}={c['value']}"
        for c in cookies
        if 'zeabur.com' in c.get('domain', '')
    )


if __name__ == '__main__':
    main()
