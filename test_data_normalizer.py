# tests/test_data_normalizer.py

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.collectors.data_normalizer import DataNormalizer

def create_sample_tweet():
    """创建样本Twitter数据"""
    return {
        'id': '1234567890',
        'text': 'BREAKING: Circle announces USDC expansion in Singapore. Major regulatory approval received. This is huge for stablecoin adoption in Asia! 🚀 #stablecoin #USDC',
        'author_username': 'circle',
        'author_verified': True,
        'author_followers': 500000,
        'created_at': '2025-01-17T10:30:00Z',
        'public_metrics': {
            'like_count': 1200,
            'retweet_count': 450,
            'reply_count': 89
        },
        'categories': ['company', 'policy'],
        'regions': ['Asia'],
        'mentioned_stablecoins': ['USDC'],
        'quality_score': 85,
        'url': 'https://twitter.com/circle/status/1234567890'
    }

def create_sample_news():
    """创建样本NewsAPI数据"""
    return {
        'title': 'SEC Approves New Stablecoin Framework for US Markets',
        'description': 'The Securities and Exchange Commission has approved a comprehensive regulatory framework for stablecoin issuers operating in the United States.',
        'content': 'The Securities and Exchange Commission has approved a comprehensive regulatory framework for stablecoin issuers operating in the United States. The new rules require issuers to maintain 1:1 reserves and submit to monthly audits.',
        'url': 'https://example.com/sec-stablecoin-framework',
        'source': {
            'name': 'Reuters'
        },
        'author': 'John Smith',
        'publishedAt': '2025-01-17T09:00:00Z',
        'categories': ['policy'],
        'regions': ['US'],
        'mentioned_coins': ['USDC', 'USDT'],
        'relevance_score': 95
    }

def test_normalize_tweet():
    """测试Twitter数据标准化"""
    print("=" * 70)
    print("🧪 测试1: Twitter数据标准化")
    print("=" * 70)
    
    tweet = create_sample_tweet()
    normalizer = DataNormalizer()
    
    # 执行标准化
    normalized = normalizer.normalize_tweet(tweet)
    
    # 验证必需字段
    required_fields = [
        'id', 'title', 'content', 'url', 'source', 'source_type',
        'author', 'published_at', 'categories', 'regions', 
        'mentioned_coins', 'quality_score', 'engagement', 'raw_data'
    ]
    
    print("\n✅ 字段验证:")
    for field in required_fields:
        if field in normalized:
            print(f"   ✓ {field}: {type(normalized[field]).__name__}")
        else:
            print(f"   ✗ {field}: 缺失!")
    
    # 验证数据类型
    print("\n✅ 数据类型验证:")
    assert isinstance(normalized['id'], str), "ID必须是字符串"
    print("   ✓ ID是字符串")
    
    assert normalized['source_type'] == 'twitter', "source_type必须是twitter"
    print("   ✓ source_type正确")
    
    assert isinstance(normalized['categories'], list), "categories必须是列表"
    print("   ✓ categories是列表")
    
    assert isinstance(normalized['quality_score'], (int, float)), "quality_score必须是数字"
    print("   ✓ quality_score是数字")
    
    assert isinstance(normalized['engagement'], int), "engagement必须是整数"
    print("   ✓ engagement是整数")
    
    # 验证计算逻辑
    expected_engagement = 1200 + 450*2 + 89*3  # likes + retweets*2 + replies*3
    assert normalized['engagement'] == expected_engagement, f"engagement计算错误: 期望{expected_engagement}, 实际{normalized['engagement']}"
    print(f"   ✓ engagement计算正确: {normalized['engagement']}")
    
    # 打印结果
    print("\n📋 标准化结果:")
    print(json.dumps(normalized, indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n✅ 测试1通过!\n")
    return normalized

def test_normalize_news():
    """测试NewsAPI数据标准化"""
    print("=" * 70)
    print("🧪 测试2: NewsAPI数据标准化")
    print("=" * 70)
    
    news = create_sample_news()
    normalizer = DataNormalizer()
    
    # 执行标准化
    normalized = normalizer.normalize_news(news)
    
    # 验证必需字段
    required_fields = [
        'id', 'title', 'content', 'url', 'source', 'source_type',
        'author', 'published_at', 'categories', 'regions',
        'mentioned_coins', 'quality_score', 'engagement', 'raw_data'
    ]
    
    print("\n✅ 字段验证:")
    for field in required_fields:
        if field in normalized:
            print(f"   ✓ {field}: {type(normalized[field]).__name__}")
        else:
            print(f"   ✗ {field}: 缺失!")
    
    # 验证数据类型
    print("\n✅ 数据类型验证:")
    assert isinstance(normalized['id'], str), "ID必须是字符串"
    assert normalized['id'].startswith('news_'), "新闻ID必须以news_开头"
    print("   ✓ ID格式正确")
    
    assert normalized['source_type'] == 'news', "source_type必须是news"
    print("   ✓ source_type正确")
    
    assert normalized['source'] == 'Reuters', "source应该是Reuters"
    print("   ✓ source正确")
    
    # 打印结果
    print("\n📋 标准化结果:")
    print(json.dumps(normalized, indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n✅ 测试2通过!\n")
    return normalized

def test_merge_and_deduplicate():
    """测试数据合并去重"""
    print("=" * 70)
    print("🧪 测试3: 数据合并去重")
    print("=" * 70)
    
    normalizer = DataNormalizer()
    
    # 创建测试数据（包含重复）
    tweet1 = normalizer.normalize_tweet(create_sample_tweet())
    news1 = normalizer.normalize_news(create_sample_news())
    
    # 创建重复的推文（相同URL）
    tweet2 = tweet1.copy()
    tweet2['id'] = 'twitter_duplicate'
    tweet2['quality_score'] = 90  # 更高的分数
    
    # 创建相似标题的新闻
    news2_data = create_sample_news()
    news2_data['title'] = 'SEC Approves New Stablecoin Framework for US Markets'  # 相同标题
    news2_data['url'] = 'https://different-url.com/article'
    news2 = normalizer.normalize_news(news2_data)
    
    # 创建完全不同的内容
    tweet3_data = create_sample_tweet()
    tweet3_data['id'] = '9876543210'
    tweet3_data['text'] = 'Tether releases Q4 attestation report. USDT reserves confirmed by BDO.'
    tweet3_data['url'] = 'https://twitter.com/tether/status/9876543210'
    tweet3_data['mentioned_stablecoins'] = ['USDT']
    tweet3 = normalizer.normalize_tweet(tweet3_data)
    
    # 合并前
    all_items = [tweet1, news1, tweet2, news2, tweet3]
    print(f"\n📊 合并前数据:")
    print(f"   总数: {len(all_items)} 条")
    print(f"   Twitter: {sum(1 for x in all_items if x['source_type'] == 'twitter')}")
    print(f"   News: {sum(1 for x in all_items if x['source_type'] == 'news')}")
    
    # 执行合并去重
    merged = normalizer.merge_and_deduplicate(all_items)
    
    print(f"\n📊 合并后数据:")
    print(f"   总数: {len(merged)} 条")
    print(f"   Twitter: {sum(1 for x in merged if x['source_type'] == 'twitter')}")
    print(f"   News: {sum(1 for x in merged if x['source_type'] == 'news')}")
    
    # 验证去重效果
    assert len(merged) < len(all_items), "去重应该减少数据量"
    print(f"\n✅ 去重效果: 从 {len(all_items)} 条减少到 {len(merged)} 条")
    
    # 验证排序（按质量分数降序）
    scores = [item['quality_score'] for item in merged]
    assert scores == sorted(scores, reverse=True), "应该按质量分数降序排列"
    print(f"✅ 排序正确: 质量分数从 {scores[0]} 降到 {scores[-1]}")
    
    # 显示保留的内容
    print("\n📋 保留的内容:")
    for i, item in enumerate(merged, 1):
        print(f"\n   [{i}] {item['title'][:60]}...")
        print(f"       来源: {item['source']} ({item['source_type']})")
        print(f"       分数: {item['quality_score']}")
        print(f"       URL: {item['url'][:50]}...")
    
    print("\n✅ 测试3通过!\n")
    return merged

def test_categorize_by_source():
    """测试按数据源分类"""
    print("=" * 70)
    print("🧪 测试4: 按数据源分类")
    print("=" * 70)
    
    normalizer = DataNormalizer()
    
    # 创建混合数据
    items = [
        normalizer.normalize_tweet(create_sample_tweet()),
        normalizer.normalize_news(create_sample_news()),
        normalizer.normalize_tweet(create_sample_tweet()),
    ]
    
    # 执行分类
    categorized = normalizer.categorize_by_source(items)
    
    print(f"\n📊 分类结果:")
    print(f"   Twitter: {len(categorized['twitter'])} 条")
    print(f"   News: {len(categorized['news'])} 条")
    
    # 验证
    assert len(categorized['twitter']) == 2, "应该有2条Twitter数据"
    assert len(categorized['news']) == 1, "应该有1条News数据"
    
    print("\n✅ 测试4通过!\n")
    return categorized

def test_categorize_by_topic():
    """测试按主题分类"""
    print("=" * 70)
    print("🧪 测试5: 按主题分类")
    print("=" * 70)
    
    normalizer = DataNormalizer()
    
    # 创建不同主题的数据
    tweet = create_sample_tweet()
    tweet['categories'] = ['company', 'policy']
    
    news = create_sample_news()
    news['categories'] = ['policy']
    
    items = [
        normalizer.normalize_tweet(tweet),
        normalizer.normalize_news(news)
    ]
    
    # 执行分类
    categorized = normalizer.categorize_by_topic(items)
    
    print(f"\n📊 分类结果:")
    for topic, topic_items in categorized.items():
        if topic_items:
            print(f"   {topic}: {len(topic_items)} 条")
    
    # 验证
    assert len(categorized['policy']) == 2, "policy应该有2条（tweet和news都有）"
    assert len(categorized['company']) == 1, "company应该有1条（只有tweet）"
    
    print("\n✅ 测试5通过!\n")
    return categorized

def test_edge_cases():
    """测试边界情况"""
    print("=" * 70)
    print("🧪 测试6: 边界情况")
    print("=" * 70)
    
    normalizer = DataNormalizer()
    
    # 测试1: 空数据
    print("\n📌 测试空数据:")
    empty_tweet = {}
    try:
        normalized = normalizer.normalize_tweet(empty_tweet)
        print(f"   ✓ 处理空Twitter数据: {normalized['title']}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    # 测试2: 缺失字段
    print("\n📌 测试缺失字段:")
    incomplete_news = {
        'title': 'Test Article',
        'url': 'https://test.com'
        # 缺少其他字段
    }
    try:
        normalized = normalizer.normalize_news(incomplete_news)
        print(f"   ✓ 处理不完整数据: {normalized['source']}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    # 测试3: 空列表
    print("\n📌 测试空列表合并:")
    merged = normalizer.merge_and_deduplicate([])
    assert merged == [], "空列表应该返回空列表"
    print(f"   ✓ 空列表处理正确")
    
    # 测试4: 单条数据
    print("\n📌 测试单条数据:")
    single_item = [normalizer.normalize_tweet(create_sample_tweet())]
    merged = normalizer.merge_and_deduplicate(single_item)
    assert len(merged) == 1, "单条数据应该保持不变"
    print(f"   ✓ 单条数据处理正确")
    
    print("\n✅ 测试6通过!\n")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🚀 开始运行 DataNormalizer 完整测试套件".center(70))
    print("=" * 70 + "\n")
    
    try:
        # 运行所有测试
        normalized_tweet = test_normalize_tweet()
        normalized_news = test_normalize_news()
        merged_data = test_merge_and_deduplicate()
        categorized_by_source = test_categorize_by_source()
        categorized_by_topic = test_categorize_by_topic()
        test_edge_cases()
        
        # 保存测试结果
        test_results = {
            'normalized_tweet': normalized_tweet,
            'normalized_news': normalized_news,
            'merged_data': merged_data,
            'categorized_by_source': {
                'twitter': len(categorized_by_source['twitter']),
                'news': len(categorized_by_source['news'])
            },
            'categorized_by_topic': {
                k: len(v) for k, v in categorized_by_topic.items()
            }
        }
        
        # 创建输出目录
        output_dir = Path(__file__).parent / 'test_results'
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / 'normalized_output.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print("=" * 70)
        print("🎉 所有测试通过!".center(70))
        print("=" * 70)
        print(f"\n✅ 测试结果已保存: {output_file}")
        print("\n📊 测试总结:")
        print("   ✓ Twitter数据标准化")
        print("   ✓ NewsAPI数据标准化")
        print("   ✓ 数据合并去重")
        print("   ✓ 按数据源分类")
        print("   ✓ 按主题分类")
        print("   ✓ 边界情况处理")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)