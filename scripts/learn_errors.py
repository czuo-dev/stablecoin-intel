# Python 错误处理学习

import os
import json

# =========================
# Part 1: 基础 try/except
# =========================

print("=" * 50)
print("1. 基础错误处理")
print("=" * 50)

# 场景1: 文件不存在
print("\n尝试读取不存在的文件:")
try:
    with open("data/not_exist.txt", "r") as f:
        content = f.read()
    print("文件读取成功")
except FileNotFoundError:
    print("❌ 错误: 文件不存在")
    print("✅ 程序继续运行...")

# 场景2: 数字转换错误
print("\n尝试转换非数字字符串:")
try:
    number = int("abc")
    print(f"转换结果: {number}")
except ValueError:
    print("❌ 错误: 无法转换为数字")
    print("✅ 程序继续运行...")

# =========================
# Part 2: 多种错误类型
# =========================

print("\n" + "=" * 50)
print("2. 处理多种错误")
print("=" * 50)

def safe_divide(a, b):
    """安全的除法运算"""
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("❌ 错误: 不能除以零")
        return None
    except TypeError:
        print("❌ 错误: 参数类型不正确")
        return None

# 测试
print(f"10 / 2 = {safe_divide(10, 2)}")
print(f"10 / 0 = {safe_divide(10, 0)}")
print(f"10 / '2' = {safe_divide(10, '2')}")

# =========================
# Part 3: else 和 finally
# =========================

print("\n" + "=" * 50)
print("3. else 和 finally 子句")
print("=" * 50)

def read_file_safe(filepath):
    """安全读取文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件 {filepath} 不存在")
        return None
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return None
    else:
        print(f"✅ 成功读取 {filepath}")
        return content
    finally:
        print(f"📝 完成文件 {filepath} 的读取尝试")

# 测试
print("\n测试1: 读取存在的文件")
content1 = read_file_safe("data/test_write.txt")

print("\n测试2: 读取不存在的文件")
content2 = read_file_safe("data/not_exist.txt")

# =========================
# Part 4: 实用场景 - JSON 解析
# =========================

print("\n" + "=" * 50)
print("4. JSON 安全解析")
print("=" * 50)

def load_json_safe(filepath):
    """安全加载 JSON 文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ 文件 {filepath} 不存在")
        return {}
    except json.JSONDecodeError:
        print(f"❌ 文件 {filepath} 不是有效的 JSON")
        return {}
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return {}

# 测试
print("\n测试有效的 JSON:")
data1 = load_json_safe("data/stablecoins.json")
if data1:
    print(f"  加载成功，包含 {len(data1)} 个稳定币")

print("\n测试无效的文件:")
data2 = load_json_safe("data/not_exist.json")

# =========================
# Part 5: 实战 - 安全的文件操作函数
# =========================

print("\n" + "=" * 50)
print("5. 实战：安全的文件工具函数")
print("=" * 50)

def safe_write_file(filepath, content):
    """安全写入文件"""
    try:
        # 确保目录存在
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ 成功写入 {filepath}")
        return True
    except PermissionError:
        print(f"❌ 权限不足，无法写入 {filepath}")
        return False
    except Exception as e:
        print(f"❌ 写入失败: {e}")
        return False

def safe_read_file(filepath, default=""):
    """安全读取文件，如果失败返回默认值"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️  文件 {filepath} 不存在，返回默认值")
        return default
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return default

# 测试工具函数
print("\n测试写入:")
safe_write_file("data/test_safe.txt", "这是安全写入的内容\n")

print("\n测试读取:")
content = safe_read_file("data/test_safe.txt", default="文件为空")
print(f"内容: {content}")

print("\n测试读取不存在的文件:")
content = safe_read_file("data/not_exist.txt", default="使用默认内容")
print(f"内容: {content}")

# =========================
# 总结
# =========================

print("\n" + "=" * 50)
print("错误处理总结")
print("=" * 50)
print("""
基本结构:
  try:
      可能出错的代码
  except 错误类型:
      处理错误
  else:
      没有错误时执行
  finally:
      无论如何都执行

常见错误类型:
  - FileNotFoundError  文件不存在
  - ValueError         值错误（类型转换等）
  - TypeError          类型错误
  - ZeroDivisionError  除以零
  - json.JSONDecodeError  JSON 解析错误
  - Exception          捕获所有错误
""")