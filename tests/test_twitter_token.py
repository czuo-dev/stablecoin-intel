# test_twitter_token.py
"""
快速测试Twitter Bearer Token是否有效
"""

import sys
import os
import urllib.parse

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import TWITTER_BEARER_TOKEN
    import tweepy
    
    print("=" * 60)
    print("🧪 Twitter Bearer Token 测试")
    print("=" * 60 + "\n")
    
    if not TWITTER_BEARER_TOKEN:
        print("❌ 未配置 TWITTER_BEARER_TOKEN")
        print("   请在 config.py 中设置")
        exit(1)
    
    # URL解码token（如果包含编码字符）
    decoded_token = urllib.parse.unquote(TWITTER_BEARER_TOKEN)
    
    print(f"📋 Token 信息:")
    print(f"   原始长度: {len(TWITTER_BEARER_TOKEN)} 字符")
    print(f"   解码后长度: {len(decoded_token)} 字符")
    print(f"   是否包含URL编码: {'是' if '%' in TWITTER_BEARER_TOKEN else '否'}")
    print(f"   前20字符: {decoded_token[:20]}...")
    print()
    
    # 测试连接
    print("🔌 测试API连接...")
    try:
        client = tweepy.Client(bearer_token=decoded_token, wait_on_rate_limit=True)
        
        # 尝试一个简单的搜索
        response = client.search_recent_tweets(
            query="stablecoin",
            max_results=10,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if response.data:
            print(f"✅ Token 有效！")
            print(f"   成功获取 {len(response.data)} 条推文")
            print(f"\n   示例推文:")
            first_tweet = response.data[0]
            print(f"   - {first_tweet.text[:80]}...")
            print(f"   - 创建时间: {first_tweet.created_at}")
            print(f"   - 点赞数: {first_tweet.public_metrics.get('like_count', 0)}")
        else:
            print("⚠️  Token 有效，但未找到推文（这很正常）")
            
    except tweepy.Unauthorized as e:
        print("❌ Token 无效或已过期")
        print(f"   错误: {e}")
        print("\n🔍 可能的原因:")
        print("   1. Token 确实无效或已过期")
        print("   2. App 的 API 访问级别不足（需要 Free tier 或更高）")
        print("   3. App 的权限设置不正确")
        print("   4. Token 格式问题（包含特殊字符）")
        print("\n💡 详细检查步骤:")
        print("   1. 访问 https://developer.twitter.com/en/portal/dashboard")
        print("   2. 选择你的 App")
        print("   3. 检查 'Settings' → 'App permissions':")
        print("      - 应该至少是 'Read' 权限")
        print("   4. 检查 'Settings' → 'User authentication settings':")
        print("      - 如果启用了 OAuth，可能需要调整")
        print("   5. 检查 'Keys and tokens' → 'Bearer Token':")
        print("      - 如果显示 'Read and Write'，尝试改为 'Read only'")
        print("      - 点击 'Regenerate' 生成新 Token")
        print("      - ⚠️  确保复制完整Token（不要有空格）")
        print("   6. 检查 'Settings' → 'App info':")
        print("      - 确保 App 状态是 'Active'")
        print("\n💡 如果重新生成的Token看起来一样:")
        print("   - 这是正常的，Twitter可能返回相同格式的token")
        print("   - 但内容应该不同（中间部分）")
        print("   - 确保完全复制新token，包括所有字符")
        print("   - 检查config.py中是否有引号或空格问题")
        exit(1)
        
    except tweepy.TooManyRequests as e:
        print("⚠️  API速率限制")
        print(f"   错误: {e}")
        print("   请稍后重试")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        exit(1)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("   请确保已安装: pip install tweepy")
    exit(1)
