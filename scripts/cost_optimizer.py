# scripts/cost_optimizer.py

"""
成本优化器
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

class CostOptimizer:
    """智能成本优化"""
    
    def __init__(self):
        self.cache_dir = Path('cache/reports')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, data: dict, language: str) -> str:
        """生成缓存key"""
        # 基于数据和语言生成唯一key
        content = json.dumps(data, sort_keys=True) + language
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_report(self, cache_key: str) -> str:
        """获取缓存的周报"""
        cache_file = self.cache_dir / f"{cache_key}.md"
        
        if cache_file.exists():
            # 检查缓存是否过期（7天）
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(days=7):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
        
        return None
    
    def cache_report(self, cache_key: str, content: str):
        """缓存周报"""
        cache_file = self.cache_dir / f"{cache_key}.md"
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def estimate_cost(self, total_tokens: int, model: str = 'gpt-4o-mini') -> float:
        """估算成本"""
        
        prices = {
            'gpt-4o-mini': {
                'input': 0.150 / 1_000_000,   # $0.15 per 1M tokens
                'output': 0.600 / 1_000_000   # $0.60 per 1M tokens
            }
        }
        
        # 假设输入输出比例 = 1:1.5
        input_tokens = total_tokens / 2.5
        output_tokens = total_tokens - input_tokens
        
        cost = (
            input_tokens * prices[model]['input'] +
            output_tokens * prices[model]['output']
        )
        
        return cost