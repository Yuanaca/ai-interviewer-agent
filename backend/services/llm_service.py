"""
LLM 服务层 - 抽象多种大模型提供商
支持: OpenAI / DeepSeek / 智谱 / 通义千问 / Ollama / Anthropic
所有模型选择和 API Key 由前端动态传入
"""

from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import LLMConfig


def build_llm(config: LLMConfig) -> ChatOpenAI:
    """
    根据前端配置构建 LLM 实例。
    除 Anthropic 外，主流国产模型都兼容 OpenAI SDK 格式。
    """
    kwargs = {
        "model": config.model_name,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "api_key": config.api_key,
    }

    base_url = config.get_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    # Anthropic 需要特殊处理
    if config.provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key,
            )
        except ImportError:
            # 回退：通过 OpenAI 兼容代理
            kwargs["base_url"] = base_url or "https://api.anthropic.com/v1"
            pass

    return ChatOpenAI(**kwargs)


async def generate_text(
    config: LLMConfig,
    system_prompt: str,
    user_prompt: str,
    messages: List[Dict[str, str]] = None,
) -> str:
    """
    通用文本生成接口
    - config: 前端传入的 LLM 配置
    - system_prompt: 系统提示
    - user_prompt: 用户提示
    - messages: 可选的历史消息列表
    """
    llm = build_llm(config)

    chat_messages = [SystemMessage(content=system_prompt)]

    if messages:
        for msg in messages:
            if msg["role"] == "user":
                chat_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_messages.append(AIMessage(content=msg["content"]))

    chat_messages.append(HumanMessage(content=user_prompt))

    response = await llm.ainvoke(chat_messages)
    return response.content


async def generate_questions(
    config: LLMConfig,
    job_info: str,
    resume_info: str,
    knowledge_context: str,
    question_count: int = 5,
    interview_type: str = "technical",
    language: str = "zh",
) -> List[Dict[str, Any]]:
    """
    根据职位、简历和知识库生成面试问题
    """
    system_prompt = f"""你是一位资深的{interview_type}面试官。
请根据提供的职位描述、候选人简历和相关知识库内容，生成{question_count}个有针对性的面试问题。

要求：
1. 问题要结合候选人的实际经历和职位要求
2. 覆盖技术能力、项目经验、行为面试等多个维度
3. 难度递进，从基础到深入
4. 每个问题附带参考答案要点

请用{language}回答，严格按照以下 JSON 格式输出（不要输出其他内容）：
```json
[
  {{
    "category": "technical|behavioral|experience",
    "difficulty": "easy|medium|hard",
    "question": "...",
    "reference_answer": "..."
  }}
]
```"""

    user_prompt = f"""
职位信息：
{job_info}

候选人简历：
{resume_info}

相关知识库：
{knowledge_context}

请生成{question_count}个面试问题。
"""

    response = await generate_text(config, system_prompt, user_prompt)
    return _parse_json_response(response)


async def evaluate_answer(
    config: LLMConfig,
    question: str,
    reference_answer: str,
    candidate_answer: str,
    language: str = "zh",
) -> Dict[str, Any]:
    """
    评估候选人的回答
    """
    system_prompt = f"""你是一位严格的面试评估专家。
请根据面试问题和参考答案，评估候选人的回答。

评估维度：
- 准确性 (30%): 回答是否准确、是否触及核心
- 深度 (25%): 回答的深度和细节
- 表达 (20%): 逻辑清晰度、表达能力
- 经验匹配 (25%): 与职位要求的匹配程度

请用{language}回答，严格按照以下 JSON 格式输出：
```json
{{
  "score": 0-100的整数,
  "strengths": ["优点1", "优点2"],
  "improvements": ["改进点1", "改进点2"],
  "feedback": "综合反馈文字",
  "keyword_match": ["匹配的关键词1", "匹配的关键词2"]
}}
```"""

    user_prompt = f"""
面试问题：{question}

参考答案要点：{reference_answer}

候选人回答：{candidate_answer}

请进行评估。
"""

    response = await generate_text(config, system_prompt, user_prompt)
    return _parse_json_response(response)


async def generate_final_report(
    config: LLMConfig,
    job_info: str,
    resume_info: str,
    questions_and_answers: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    language: str = "zh",
) -> Dict[str, Any]:
    """
    生成最终面试评估报告
    """
    qa_text = "\n---\n".join([
        f"Q{i+1}: {qa['question']}\nA: {qa['answer']}"
        for i, qa in enumerate(questions_and_answers)
    ])

    eval_text = "\n".join([
        f"Q{i+1} 评分: {e.get('score', 'N/A')}/100 - {e.get('feedback', '')}"
        for i, e in enumerate(evaluations)
    ])

    system_prompt = f"""你是一位资深招聘顾问和技术面试评估专家。
请根据候选人的面试表现，生成一份全面的面试评估报告。

报告应包含：
1. 总体评分 (0-100)
2. 各维度评分 (技术能力、沟通表达、项目经验、学习能力、文化契合)
3. 核心优势 (3-5条)
4. 待改进点 (2-3条)
5. 综合评价
6. 录用建议 (strong_hire / hire / weak_hire / no_hire)

请用{language}回答，严格按照以下 JSON 格式输出：
```json
{{
  "overall_score": 0-100,
  "scores_by_dimension": {{
    "technical": 0-100,
    "communication": 0-100,
    "experience": 0-100,
    "learning": 0-100,
    "culture_fit": 0-100
  }},
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["不足1", "不足2"],
  "summary": "综合评价...",
  "recommendation": "strong_hire|hire|weak_hire|no_hire"
}}
```"""

    user_prompt = f"""
职位信息：{job_info}

候选人简历：{resume_info}

面试问答记录：
{qa_text}

各题评分：
{eval_text}

请生成最终报告。
"""

    response = await generate_text(config, system_prompt, user_prompt)
    return _parse_json_response(response)


async def analyze_resume(
    config: LLMConfig,
    resume_text: str,
    language: str = "zh",
) -> Dict[str, Any]:
    """解析和总结简历"""
    system_prompt = f"""你是一位专业的简历分析师。请分析以下简历内容并提取关键信息。

请用{language}回答，严格按照以下 JSON 格式输出：
```json
{{
  "name": "候选人姓名（如果能识别）",
  "years_of_experience": 工作年限,
  "education": "最高学历",
  "skills": ["技能1", "技能2"],
  "companies": ["公司1", "公司2"],
  "roles": ["职位1", "职位2"],
  "summary": "简历总结（2-3句话）",
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["不足1"]
}}
```"""

    user_prompt = f"请分析以下简历：\n\n{resume_text[:3000]}"

    response = await generate_text(config, system_prompt, user_prompt)
    return _parse_json_response(response)


def _parse_json_response(text: str) -> Any:
    """从 LLM 回复中提取 JSON"""
    import json
    import re

    # 尝试提取 ```json ... ``` 代码块
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试直接找 JSON 数组/对象
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return {"raw": text, "error": "JSON parse failed"}
