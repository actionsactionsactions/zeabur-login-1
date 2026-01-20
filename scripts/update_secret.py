"""
GitHub Secret 更新模块
使用 GitHub API + PyNaCl 加密更新 Repository Secret
"""

import base64
import requests
from nacl import encoding, public


def update_secret(token: str, owner: str, repo: str, secret_name: str, secret_value: str):
    """更新 GitHub Repository Secret"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    
    # 1. 获取仓库公钥
    key_url = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key'
    key_response = requests.get(key_url, headers=headers, timeout=30)
    key_response.raise_for_status()
    key_data = key_response.json()
    
    public_key = key_data['key']
    key_id = key_data['key_id']
    
    # 2. 使用 PyNaCl 加密
    encrypted_value = encrypt_secret(public_key, secret_value)
    
    # 3. 更新 Secret
    update_url = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}'
    update_response = requests.put(
        update_url,
        headers=headers,
        json={
            'encrypted_value': encrypted_value,
            'key_id': key_id,
        },
        timeout=30,
    )
    update_response.raise_for_status()


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """使用 libsodium sealed box 加密"""
    public_key_bytes = base64.b64decode(public_key_b64)
    sealed_box = public.SealedBox(public.PublicKey(public_key_bytes))
    encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')
