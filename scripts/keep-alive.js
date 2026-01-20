/**
 * Zeabur Keep Alive Script
 * 使用 Playwright 模拟浏览器登录，保持账户活跃
 */

import { chromium } from 'playwright';
import { updateSecret } from './update-secret.js';

const ZEABUR_DASHBOARD_URL = 'https://zeabur.com/projects';

async function main() {
  const cookieString = process.env.ZEABUR_COOKIE;
  const repoToken = process.env.REPO_TOKEN;
  const repoOwner = process.env.GITHUB_REPOSITORY_OWNER;
  const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1];

  if (!cookieString) {
    console.error('❌ 错误: ZEABUR_COOKIE 环境变量未设置');
    process.exit(1);
  }

  console.log('🚀 启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();

  // 解析并设置 Cookie
  const cookies = parseCookies(cookieString);
  await context.addCookies(cookies);

  const page = await context.newPage();

  try {
    console.log('📡 访问 Zeabur 控制台...');
    await page.goto(ZEABUR_DASHBOARD_URL, { waitUntil: 'networkidle' });

    // 检查是否登录成功（页面上应该有项目列表或用户信息）
    const isLoggedIn = await checkLoginStatus(page);

    if (!isLoggedIn) {
      console.error('❌ 登录失败: Cookie 可能已过期');
      process.exit(1);
    }

    console.log('✅ 登录成功！');
    console.log(`⏰ 执行时间: ${new Date().toISOString()}`);

    // 提取更新后的 Cookie
    const newCookies = await context.cookies();
    const newCookieString = formatCookies(newCookies);

    // 如果 Cookie 有变化且配置了更新参数，则更新 GitHub Secret
    if (repoToken && repoOwner && repoName && newCookieString !== cookieString) {
      console.log('🔄 检测到 Cookie 变化，正在更新 GitHub Secret...');
      await updateSecret(repoToken, repoOwner, repoName, 'ZEABUR_COOKIE', newCookieString);
      console.log('✅ GitHub Secret 已更新');
    }

  } catch (error) {
    console.error('❌ 执行失败:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

/**
 * 检查登录状态
 */
async function checkLoginStatus(page) {
  try {
    // 检查是否被重定向到登录页
    const url = page.url();
    if (url.includes('/login')) {
      return false;
    }

    // 等待页面加载完成，检查是否有项目相关内容
    await page.waitForTimeout(2000);
    
    // 检查页面标题或特定元素
    const title = await page.title();
    return title.includes('Zeabur') && !title.includes('Login');
  } catch {
    return false;
  }
}

/**
 * 解析 Cookie 字符串为 Playwright Cookie 格式
 * 支持格式: "name1=value1; name2=value2"
 */
function parseCookies(cookieString) {
  return cookieString.split(';').map(cookie => {
    const [name, ...valueParts] = cookie.trim().split('=');
    return {
      name: name.trim(),
      value: valueParts.join('=').trim(),
      domain: '.zeabur.com',
      path: '/',
    };
  }).filter(c => c.name && c.value);
}

/**
 * 格式化 Cookies 为字符串
 */
function formatCookies(cookies) {
  return cookies
    .filter(c => c.domain.includes('zeabur.com'))
    .map(c => `${c.name}=${c.value}`)
    .join('; ');
}

main();
