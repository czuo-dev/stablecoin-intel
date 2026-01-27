# check_twitter_app.py
"""
检查Twitter App配置和访问级别
"""

import sys
import os
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import TWITTER_BEARER_TOKEN
    import tweepy
    import requests
    
    print("=" * 70)
    print("🔍 Twitter App 配置检查")
    print("=" * 70 + "\n")
    
    if not TWITTER_BEARER_TOKEN:
        print("❌ 未配置 TWITTER_BEARER_TOKEN")
        exit(1)
    
    decoded_token = urllib.parse.unquote(TWITTER_BEARER_TOKEN)
    
    print("📋 检查项目:")
    print("-" * 70)
    
    # 1. 检查Token格式
    print("\n1️⃣ Token 格式检查:")
    print(f"   - 长度: {len(decoded_token)} 字符")
    print(f"   - 格式: {'✅ 正确' if decoded_token.startswith('AAAAAAAAAAAAAAAAAAAAA') else '⚠️  可能有问题'}")
    special_chars = ['%', ' ', '\n', '\t']
    has_special = any(c in decoded_token for c in special_chars)
    print(f"   - 包含特殊字符: {'是' if has_special else '否'}")
    
    # 2. 尝试直接API调用（不通过tweepy）
    print("\n2️⃣ 直接API调用测试:")
    try:
        headers = {
            'Authorization': f'Bearer {decoded_token}'
        }
        response = requests.get(
            'https://api.twitter.com/2/tweets/search/recent',
            params={'query': 'stablecoin', 'max_results': 10},
            headers=headers,
            timeout=10
        )
        
        print(f"   - HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - ✅ API调用成功！")
            print(f"   - 返回数据: {len(data.get('data', []))} 条推文")
        elif response.status_code == 401:
            error_data = response.json()
            print(f"   - ❌ 401 Unauthorized")
            print(f"   - 错误详情: {error_data}")
            print("\n   💡 这通常意味着:")
            print("      - Token 无效或已过期")
            print("      - App 权限不足")
            print("      - App 状态不是 Active")
        elif response.status_code == 403:
            error_data = response.json()
            print(f"   - ❌ 403 Forbidden")
            print(f"   - 错误详情: {error_data}")
            print("\n   💡 这通常意味着:")
            print("      - App 没有访问 Twitter API v2 的权限")
            print("      - 需要升级到 Free tier 或更高")
            print("      - 检查 Developer Portal 中的 App 访问级别")
        else:
            print(f"   - ⚠️  其他错误: {response.status_code}")
            print(f"   - 响应: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   - ❌ 请求失败: {e}")
    
    # 3. 通过tweepy测试
    print("\n3️⃣ Tweepy 客户端测试:")
    try:
        client = tweepy.Client(bearer_token=decoded_token, wait_on_rate_limit=True)
        
        # 尝试获取用户信息（最简单的API调用）
        try:
            user = client.get_user(username="twitter")
            if user.data:
                print(f"   - ✅ Tweepy 连接成功！")
                print(f"   - 测试用户: @{user.data.username}")
        except tweepy.Unauthorized:
            print(f"   - ❌ 401 Unauthorized (通过tweepy)")
        except tweepy.Forbidden:
            print(f"   - ❌ 403 Forbidden (通过tweepy)")
            print("   - 💡 可能需要检查App的访问级别")
        except Exception as e:
            print(f"   - ⚠️  其他错误: {e}")
            
    except Exception as e:
        print(f"   - ❌ Tweepy初始化失败: {e}")
    
    # 4. 提供诊断建议
    print("\n" + "=" * 70)
    print("💡 诊断建议:")
    print("=" * 70)
    print("\n如果看到 401 Unauthorized:")
    print("   1. 确认Token是从正确的App复制的")
    print("   2. 检查App状态是否为 'Active'")
    print("   3. 尝试删除旧Token，生成全新的")
    print("   4. 确保Token没有多余的空格或换行")
    print("\n如果看到 403 Forbidden:")
    print("   1. 检查App的API访问级别")
    print("   2. 可能需要申请更高的访问级别")
    print("   3. 检查App权限设置")
    print("\n如果Token看起来一样:")
    print("   - 这是正常的，格式相同但内容不同")
    print("   - 确保完全替换config.py中的旧Token")
    print("   - 保存文件后重新运行测试")
    
    print("\n" + "=" * 70)
    print("✅ 检查完成")
    print("=" * 70)

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("   请安装: pip install tweepy requests")
    exit(1)
