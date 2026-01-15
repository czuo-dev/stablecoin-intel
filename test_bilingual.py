# test_bilingual.py

from src.processors.translator import MultilingualTranslator
from config import OPENAI_API_KEY

print("🌍 测试多语言翻译器\n")
print("="*60)

# 初始化翻译器
translator = MultilingualTranslator(OPENAI_API_KEY)

# 测试1：短文本翻译
print("\n【测试1】基础翻译 - 中文→西班牙语")
print("-"*60)

test_text_short = """
## 📋 政策监管

香港金管局本周向Circle发放了首个稳定币发行牌照，这标志着亚洲监管环境的重大突破。
"""

print("原文（中文）:")
print(test_text_short)

spanish = translator.translate_to_spanish(test_text_short)

if spanish:
    print("\n译文（西班牙语）:")
    print(spanish)
    print("\n✅ 翻译成功")
else:
    print("\n❌ 翻译失败")

# 测试2：带专业术语的翻译
print("\n" + "="*60)
print("\n【测试2】专业术语翻译")
print("-"*60)

test_text_terms = """
Circle获得监管牌照，可在香港发行USDC稳定币。该牌照要求：
- 100%储备金支持
- 定期审计
- 合规赎回机制
"""

print("原文（中文）:")
print(test_text_terms)

spanish_terms = translator.translate_to_spanish(test_text_terms)

if spanish_terms:
    print("\n译文（西班牙语）:")
    print(spanish_terms)
    
    # 检查关键术语
    print("\n术语检查:")
    key_terms = ["USDC", "stablecoin", "reservas", "auditoría", "cumplimiento"]
    for term in key_terms:
        if term.lower() in spanish_terms.lower():
            print(f"  ✅ {term} - 存在")
        else:
            print(f"  ⚠️  {term} - 未找到")
else:
    print("\n❌ 翻译失败")

# 测试3：双语摘要生成（一次调用，省成本）
print("\n" + "="*60)
print("\n【测试3】双语摘要生成（推荐方式）")
print("-"*60)

test_articles = """
【新闻1】PayPal扩展PYUSD到欧洲市场
PayPal宣布其稳定币PYUSD将在德国和法国推出。

【新闻2】香港金管局发放首个稳定币牌照
Circle成为首家获得香港稳定币发行牌照的公司。
"""

print("输入内容:")
print(test_articles)

bilingual = translator.generate_bilingual_summary(test_articles, target_lang="es")

if bilingual["zh"] and bilingual["es"]:
    print("\n【中文摘要】")
    print(bilingual["zh"])
    
    print("\n【西班牙语摘要】")
    print(bilingual["es"])
    
    print("\n✅ 双语生成成功")
    print(f"💰 成本对比：")
    print(f"   单独翻译: 2次API调用 ≈ $0.0004")
    print(f"   双语生成: 1次API调用 ≈ $0.0002")
    print(f"   节省: 50%")
else:
    print("\n❌ 双语生成失败")

print("\n" + "="*60)
print("\n🎉 测试完成！")
print("\n💡 建议：在周报生成时使用 generate_bilingual_summary() 节省成本")