# templates/prompt_templates.py

"""
AI周报生成的Prompt模板
"""

class WeeklyReportPrompts:
    
    @staticmethod
    def get_summary_prompt(language: str, data: dict) -> str:
        """
        获取周报生成的Prompt
        
        Args:
            language: 'zh', 'en', 'es'
            data: 周报数据
        """
        
        prompts = {
            'zh': WeeklyReportPrompts._chinese_prompt(data),
            'en': WeeklyReportPrompts._english_prompt(data),
            'es': WeeklyReportPrompts._spanish_prompt(data)
        }
        
        return prompts.get(language, prompts['zh'])
    
    @staticmethod
    def _chinese_prompt(data: dict) -> str:
        """中文周报Prompt"""
        
        # 准备数据
        period = f"{data['period']['start']} 至 {data['period']['end']}"
        total_news = data['stats']['total_news']
        
        # 提取Top 10新闻
        top_news_text = ""
        for i, item in enumerate(data['top_news'][:10], 1):
            top_news_text += f"\n{i}. {item['title']}\n"
            top_news_text += f"   来源: {item['source']}\n"
            top_news_text += f"   摘要: {item.get('content', '')[:200]}...\n"
        
        return f"""
你是稳定币行业资深分析师，请基于以下数据生成专业的中文周报。

【数据范围】
时间: {period}
新闻总数: {total_news}

【Top 10 重要新闻】
{top_news_text}

【输出要求】
请按以下结构生成周报：

# 稳定币行业周报
**报告期**: {period}

## 📊 本周概览
（用3-5个要点总结本周最重要的趋势和事件）

## 🔥 重点新闻
（从Top 10中选择最重要的5条，每条150-200字深度解读）

### 1. [新闻标题]
[详细分析]

### 2. [新闻标题]
[详细分析]

[继续...]

## 📋 政策更新
（总结监管政策变化）

## 📈 市场数据
（分析市场趋势和数据）

## 🌍 区域动态
（按地区：美洲、欧洲、亚洲、拉美）

## 🔮 下周展望
（预测下周重要事件和趋势）

【要求】
- 专业、客观、易读的语言
- 总长度：2000-2500字
- 每条重点新闻包括：背景、影响分析、行业意义
- 使用适当的emoji提升可读性
"""
    
    @staticmethod
    def _english_prompt(data: dict) -> str:
        """英文周报Prompt"""
        
        period = f"{data['period']['start']} to {data['period']['end']}"
        total_news = data['stats']['total_news']
        
        top_news_text = ""
        for i, item in enumerate(data['top_news'][:10], 1):
            top_news_text += f"\n{i}. {item['title']}\n"
            top_news_text += f"   Source: {item['source']}\n"
            top_news_text += f"   Summary: {item.get('content', '')[:200]}...\n"
        
        return f"""
You are a senior stablecoin industry analyst. Generate a professional English weekly report based on the following data.

【Data Scope】
Period: {period}
Total News: {total_news}

【Top 10 Important News】
{top_news_text}

【Output Requirements】
Generate the report with the following structure:

# Stablecoin Industry Weekly Report
**Period**: {period}

## 📊 Weekly Overview
(Summarize the most important trends and events in 3-5 bullet points)

## 🔥 Key Highlights
(Select the 5 most important stories from Top 10, 150-200 words analysis each)

### 1. [News Title]
[Detailed analysis]

### 2. [News Title]
[Detailed analysis]

[Continue...]

## 📋 Policy Updates
(Summarize regulatory policy changes)

## 📈 Market Data
(Analyze market trends and data)

## 🌍 Regional Updates
(By region: Americas, Europe, Asia, LATAM)

## 🔮 Next Week Outlook
(Predict important events and trends for next week)

【Requirements】
- Professional, objective, reader-friendly language
- Total length: 2000-2500 words
- Each highlight includes: background, impact analysis, industry significance
- Use appropriate emojis to improve readability
"""
    
    @staticmethod
    def _spanish_prompt(data: dict) -> str:
        """西班牙语周报Prompt"""
        
        period = f"{data['period']['start']} a {data['period']['end']}"
        total_news = data['stats']['total_news']
        
        top_news_text = ""
        for i, item in enumerate(data['top_news'][:10], 1):
            top_news_text += f"\n{i}. {item['title']}\n"
            top_news_text += f"   Fuente: {item['source']}\n"
            top_news_text += f"   Resumen: {item.get('content', '')[:200]}...\n"
        
        return f"""
Eres un analista senior de la industria de stablecoins. Genera un informe semanal profesional en español basado en los siguientes datos.

【Alcance de Datos】
Período: {period}
Noticias Totales: {total_news}

【Top 10 Noticias Importantes】
{top_news_text}

【Requisitos de Salida】
Genera el informe con la siguiente estructura:

# Informe Semanal de Stablecoins
**Período**: {period}

## 📊 Resumen Semanal
(Resume las tendencias y eventos más importantes en 3-5 puntos)

## 🔥 Noticias Destacadas
(Selecciona las 5 historias más importantes del Top 10, análisis de 150-200 palabras cada una)

### 1. [Título de Noticia]
[Análisis detallado]

### 2. [Título de Noticia]
[Análisis detallado]

[Continuar...]

## 📋 Actualizaciones Regulatorias
(Resume los cambios en políticas regulatorias)

## 📈 Datos de Mercado
(Analiza tendencias y datos del mercado)

## 🌍 Actualizaciones Regionales
(Por región: Américas, Europa, Asia, LATAM)

## 🔮 Perspectivas para la Próxima Semana
(Predice eventos y tendencias importantes para la próxima semana)

【Requisitos】
- Lenguaje profesional, objetivo y fácil de leer
- Longitud total: 2000-2500 palabras
- Cada noticia destacada incluye: antecedentes, análisis de impacto, significancia de la industria
- Usa emojis apropiados para mejorar la legibilidad
"""
