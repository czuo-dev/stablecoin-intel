"""
改进版AI周报生成Prompt模板
重点：准确性、深度、可读性
"""

class ImprovedPrompts:
    
    @staticmethod
    def get_summary_prompt(language: str, data: dict) -> str:
        """获取改进版周报Prompt"""
        
        prompts = {
            'zh': ImprovedPrompts._chinese_prompt_v2(data),
            'en': ImprovedPrompts._english_prompt_v2(data),
            'es': ImprovedPrompts._spanish_prompt_v2(data)
        }
        
        return prompts.get(language, prompts['zh'])
    
    @staticmethod
    def _chinese_prompt_v2(data: dict) -> str:
        """改进版中文Prompt"""
        
        period = f"{data['period']['start']} 至 {data['period']['end']}"
        total_news = data['stats']['total_news']
        
        # 提取Top 10并格式化
        top_news_text = "\n".join([
            f"{i}. 【{item.get('source', 'Unknown')}】{item['title']}\n"
            f"   时间: {item.get('published_at', 'N/A')[:10]}\n"
            f"   分类: {', '.join(item.get('categories', ['general']))}\n"
            f"   摘要: {item.get('content', item.get('description', ''))[:150]}...\n"
            for i, item in enumerate(data['top_news'][:10], 1)
        ])
        
        # 统计数据
        by_category = data['stats']['by_category']
        
        return f"""你是稳定币行业资深分析师。请基于以下真实新闻数据，生成专业、准确的中文周报。

【重要规则】
1. 只使用提供的真实新闻数据
2. 不要编造任何数据、公司名称或事件
3. 不要使用"据报道"、"有消息称"等模糊表述
4. 每条新闻必须能追溯到提供的数据源
5. 如果某个领域没有数据，明确说明"本周无相关新闻"

【数据范围】
报告期: {period}
新闻总数: {total_news}
分类统计: {by_category}

【Top 10 重要新闻】
{top_news_text}

【输出格式】

# 稳定币行业周报
**报告期**: {period}  
**新闻总数**: {total_news}

---

## 📊 本周概览

（用3-5个要点总结本周最重要的趋势，每个要点必须基于具体新闻）

**示例格式**：
- **监管进展**：新加坡金管局批准Circle支付牌照（来源：彭博社，1月15日）
- **市场动态**：稳定币总市值突破180亿美元（来源：CoinDesk，1月17日）

---

## 🔥 重点新闻深度解读

（从Top 10中选择5条最重要的，每条200-250字）

### 1. [具体新闻标题]

**来源**: [新闻来源] | **日期**: [具体日期]

**事件背景**：（简述事件）

**核心内容**：（详细说明）

**行业影响**：（分析对稳定币行业的意义）

---

## 📋 分类动态

### 监管政策 ({by_category.get('policy', 0)} 条)
（只总结本周真实的监管新闻，如果没有则说"本周无重大监管新闻"）

### 公司动态 ({by_category.get('company', 0)} 条)
（只总结本周真实的公司新闻）

### 市场数据 ({by_category.get('market', 0)} 条)
（只总结本周真实的市场数据）

---

## 🌍 地区动态

（只总结有真实新闻的地区，没有数据的地区不要提及）

---

## 📈 数据总结

- 本周收录新闻：{total_news} 条
- 监管相关：{by_category.get('policy', 0)} 条
- 公司动态：{by_category.get('company', 0)} 条
- 市场数据：{by_category.get('market', 0)} 条

---

**报告说明**  
本周报基于AI分析{total_news}条真实新闻生成。所有内容均可追溯至具体新闻来源。

【质量要求】
- 总字数：2000-2500字
- 每条重点新闻：200-250字
- 必须包含具体日期和来源
- 客观、专业的分析语言
- 适当使用emoji提升可读性
"""
    
    @staticmethod
    def _english_prompt_v2(data: dict) -> str:
        """改进版英文Prompt"""
        
        period = f"{data['period']['start']} to {data['period']['end']}"
        total_news = data['stats']['total_news']
        
        top_news_text = "\n".join([
            f"{i}. [{item.get('source', 'Unknown')}] {item['title']}\n"
            f"   Date: {item.get('published_at', 'N/A')[:10]}\n"
            f"   Category: {', '.join(item.get('categories', ['general']))}\n"
            f"   Summary: {item.get('content', item.get('description', ''))[:150]}...\n"
            for i, item in enumerate(data['top_news'][:10], 1)
        ])
        
        by_category = data['stats']['by_category']
        
        return f"""You are a senior stablecoin industry analyst. Generate a professional, accurate English weekly report based on the real news data provided.

【Critical Rules】
1. Only use the real news data provided
2. Do not fabricate any data, company names, or events
3. Avoid vague phrases like "according to reports" or "it is estimated"
4. Every news item must be traceable to the provided sources
5. If no data exists for a section, clearly state "No relevant news this week"

【Data Scope】
Period: {period}
Total News: {total_news}
Category Breakdown: {by_category}

【Top 10 Important News】
{top_news_text}

【Output Format】

# Stablecoin Weekly Report
**Period**: {period}  
**Total News**: {total_news}

---

## 📊 Weekly Overview

(Summarize the most important trends in 3-5 bullet points, each based on specific news)

**Example Format**:
- **Regulatory Progress**: Singapore MAS approves Circle payment license (Source: Bloomberg, Jan 15)
- **Market Dynamics**: Stablecoin market cap surpasses $180B (Source: CoinDesk, Jan 17)

---

## 🔥 Key Highlights In-Depth

(Select 5 most important stories from Top 10, 200-250 words each)

### 1. [Specific News Title]

**Source**: [News Source] | **Date**: [Specific Date]

**Background**: (Brief context)

**Core Content**: (Detailed explanation)

**Industry Impact**: (Analysis of significance for stablecoin industry)

---

## 📋 Category Updates

### Policy & Regulation ({by_category.get('policy', 0)} items)
(Only summarize real regulatory news from this week, state "No major regulatory news this week" if none)

### Company News ({by_category.get('company', 0)} items)
(Only summarize real company news)

### Market Data ({by_category.get('market', 0)} items)
(Only summarize real market data)

---

## 🌍 Regional Updates

(Only summarize regions with real news, omit regions without data)

---

## 📈 Data Summary

- News Collected: {total_news} items
- Policy Related: {by_category.get('policy', 0)} items
- Company News: {by_category.get('company', 0)} items
- Market Data: {by_category.get('market', 0)} items

---

**Report Notes**  
This report is AI-generated based on analysis of {total_news} real news items. All content is traceable to specific news sources.

【Quality Requirements】
- Total length: 2000-2500 words
- Each key highlight: 200-250 words
- Must include specific dates and sources
- Objective, professional analytical language
- Appropriate use of emojis for readability
"""
    
    @staticmethod
    def _spanish_prompt_v2(data: dict) -> str:
        """改进版西班牙语Prompt"""
        
        period = f"{data['period']['start']} a {data['period']['end']}"
        total_news = data['stats']['total_news']
        
        top_news_text = "\n".join([
            f"{i}. [{item.get('source', 'Unknown')}] {item['title']}\n"
            f"   Fecha: {item.get('published_at', 'N/A')[:10]}\n"
            f"   Categoría: {', '.join(item.get('categories', ['general']))}\n"
            f"   Resumen: {item.get('content', item.get('description', ''))[:150]}...\n"
            for i, item in enumerate(data['top_news'][:10], 1)
        ])
        
        by_category = data['stats']['by_category']
        
        return f"""Eres un analista senior de la industria de stablecoins. Genera un informe semanal profesional y preciso en español basado en datos de noticias reales.

【Reglas Críticas】
1. Solo usa los datos de noticias reales proporcionados
2. No inventes datos, nombres de empresas o eventos
3. Evita frases vagas como "según informes" o "se estima"
4. Cada noticia debe ser rastreable a las fuentes proporcionadas
5. Si no hay datos para una sección, indica claramente "Sin noticias relevantes esta semana"

【Alcance de Datos】
Período: {period}
Noticias Totales: {total_news}
Desglose por Categoría: {by_category}

【Top 10 Noticias Importantes】
{top_news_text}

【Formato de Salida】

# Informe Semanal de Stablecoins
**Período**: {period}  
**Noticias Totales**: {total_news}

---

## 📊 Resumen Semanal

(Resume las tendencias más importantes en 3-5 puntos, cada uno basado en noticias específicas)

**Formato de Ejemplo**:
- **Progreso Regulatorio**: MAS de Singapur aprueba licencia de pago de Circle (Fuente: Bloomberg, 15 ene)
- **Dinámica del Mercado**: Capitalización de stablecoins supera $180B (Fuente: CoinDesk, 17 ene)

---

## 🔥 Noticias Destacadas en Profundidad

(Selecciona las 5 historias más importantes del Top 10, 200-250 palabras cada una)

### 1. [Título de Noticia Específico]

**Fuente**: [Fuente de Noticia] | **Fecha**: [Fecha Específica]

**Antecedentes**: (Contexto breve)

**Contenido Principal**: (Explicación detallada)

**Impacto en la Industria**: (Análisis del significado para la industria de stablecoins)

---

## 📋 Actualizaciones por Categoría

### Política y Regulación ({by_category.get('policy', 0)} elementos)
(Solo resume noticias regulatorias reales, indica "Sin noticias regulatorias importantes esta semana" si no hay)

### Noticias de Empresas ({by_category.get('company', 0)} elementos)
(Solo resume noticias reales de empresas)

### Datos de Mercado ({by_category.get('market', 0)} elementos)
(Solo resume datos reales del mercado)

---

## 🌍 Actualizaciones Regionales

(Solo resume regiones con noticias reales, omite regiones sin datos)

---

## 📈 Resumen de Datos

- Noticias Recopiladas: {total_news} elementos
- Relacionadas con Política: {by_category.get('policy', 0)} elementos
- Noticias de Empresas: {by_category.get('company', 0)} elementos
- Datos de Mercado: {by_category.get('market', 0)} elementos

---

**Notas del Informe**  
Este informe es generado por IA basado en el análisis de {total_news} noticias reales. Todo el contenido es rastreable a fuentes de noticias específicas.

【Requisitos de Calidad】
- Longitud total: 2000-2500 palabras
- Cada noticia destacada: 200-250 palabras
- Debe incluir fechas y fuentes específicas
- Lenguaje analítico objetivo y profesional
- Uso apropiado de emojis para legibilidad
"""
