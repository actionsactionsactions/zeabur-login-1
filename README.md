# Zeabur Keep Alive

通过 GitHub Actions 定时模拟登录 Zeabur 控制台，保持账户活跃。支持 Telegram 通知和自动更新 Cookie。

## 功能

- ✅ 定时模拟浏览器登录 Zeabur
- 📸 登录成功后截图并发送到 Telegram
- 🔄 自动更新 Cookie 到 GitHub Secrets

## 配置步骤

### 1. 获取 Zeabur Cookie

1. 登录 [Zeabur 控制台](https://zeabur.com)
2. 浏览器 F12 打开开发者工具
3. **Application → Cookies → zeabur.com**
4. 复制所有 Cookie，格式：`name1=value1; name2=value2`

### 2. 创建 Telegram Bot

1. 在 Telegram 搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建 Bot
3. 保存 Bot Token
4. 获取 Chat ID：
   - 给 Bot 发送任意消息
   - 访问 `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - 找到 `chat.id` 字段

### 3. 创建 GitHub Personal Access Token

1. [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. 生成 Token，勾选 **repo** scope

### 4. 配置 GitHub Secrets

进入仓库 **Settings → Secrets and variables → Actions**：

| Secret 名称 | 说明 |
|------------|------|
| `ZEABUR_COOKIE` | Zeabur 登录 Cookie |
| `REPO_TOKEN` | GitHub PAT（用于自动更新 Cookie） |
| `TG_BOT_TOKEN` | Telegram Bot Token |
| `TG_CHAT_ID` | Telegram Chat ID |

## 执行频率

默认每天 08:00（北京时间）执行。修改 cron：

```yaml
schedule:
  - cron: '0 0 * * *'     # 每天
  - cron: '0 */12 * * *'  # 每12小时
```

## 手动测试

```bash
pip install -r requirements.txt
playwright install chromium
export ZEABUR_COOKIE="your_cookie"
export TG_BOT_TOKEN="your_bot_token"
export TG_CHAT_ID="your_chat_id"
python scripts/keep_alive.py
```
