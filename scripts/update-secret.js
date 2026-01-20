/**
 * GitHub Secret 更新模块
 * 使用 GitHub API + libsodium 加密更新 Repository Secret
 */

import sodium from 'libsodium-wrappers';

/**
 * 更新 GitHub Repository Secret
 * @param {string} token - GitHub Personal Access Token
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {string} secretName - Secret 名称
 * @param {string} secretValue - Secret 值
 */
export async function updateSecret(token, owner, repo, secretName, secretValue) {
  await sodium.ready;

  // 1. 获取仓库公钥
  const keyResponse = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/secrets/public-key`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
    }
  );

  if (!keyResponse.ok) {
    throw new Error(`获取公钥失败: ${keyResponse.status} ${await keyResponse.text()}`);
  }

  const { key, key_id } = await keyResponse.json();

  // 2. 使用 libsodium 加密 secret
  const publicKey = sodium.from_base64(key, sodium.base64_variants.ORIGINAL);
  const messageBytes = sodium.from_string(secretValue);
  const encryptedBytes = sodium.crypto_box_seal(messageBytes, publicKey);
  const encryptedValue = sodium.to_base64(encryptedBytes, sodium.base64_variants.ORIGINAL);

  // 3. 更新 secret
  const updateResponse = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/secrets/${secretName}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        encrypted_value: encryptedValue,
        key_id: key_id,
      }),
    }
  );

  if (!updateResponse.ok) {
    throw new Error(`更新 Secret 失败: ${updateResponse.status} ${await updateResponse.text()}`);
  }
}
