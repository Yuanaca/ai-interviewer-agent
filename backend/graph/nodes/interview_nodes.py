"""
LangGraph 面试图节点实现
每个节点执行特定的面试阶段任务
"""

from typing import Dict, Any

from ..state import InterviewState, InterviewPhase
from config import LLMConfig
from services.llm_service import (
    analyze_resume,
    generate_questions,
    evaluate_answer,
    generate_final_report,
)
from services.rag_service import build_rag_context


async def init_session(state: InterviewState) -> Dict[str, Any]:
    """
    初始化会话：验证配置，准备基础信息
    """
    return {
        "phase": InterviewPhase.RESUME_ANALYSIS.value,
        "chat_history": [{
            "role": "system",
            "content": f"面试会话已创建 | 类型: {state.get('interview_type', 'technical')} | 语言: {state.get('language', 'zh')}"
        }]
    }


async def analyze_resume_node(state: InterviewState) -> Dict[str, Any]:
    """
    简历分析节点：解析候选人简历，提取关键信息
    """
    resume_text = state.get("resume_text", "").strip()
    llm_config = LLMConfig(**state.get("llm_config", {}))
    language = state.get("language", "zh")

    if not resume_text:
        return {
            "phase": InterviewPhase.RAG_RETRIEVAL.value,
            "resume_summary": "未提供简历",
            "resume_analysis": {},
            "chat_history": [{
                "role": "system",
                "content": "未提供候选人简历，将基于职位要求进行面试。"
            }]
        }

    # 检测简历文本是否为二进制垃圾（如上传了图片）
    if _is_garbage_text(resume_text):
        return {
            "phase": InterviewPhase.RAG_RETRIEVAL.value,
            "resume_summary": "简历文本无效",
            "resume_analysis": {},
            "chat_history": [{
                "role": "system",
                "content": "⚠️ 检测到简历内容似乎不是有效文本（可能是图片文件），请上传 .txt 或 .pdf 格式的文本简历。将基于职位要求继续面试。"
            }]
        }

    try:
        result = await analyze_resume(llm_config, resume_text, language)

        # 提取结构化信息
        skills = result.get("skills", [])
        companies = result.get("companies", [])
        roles = result.get("roles", [])
        name = result.get("name", "未知")
        years = result.get("years_of_experience", "未知")
        education = result.get("education", "未知")
        summary = result.get("summary", "简历分析完成")
        strengths = result.get("strengths", [])
        weaknesses = result.get("weaknesses", [])

        # 构建丰富的简历摘要
        skills_str = "、".join(skills) if skills else "待识别"
        exp_str = f"{years}年经验" if years and years != "未知" else ""
        edu_str = education if education and education != "未知" else ""

        detail_parts = [p for p in [exp_str, edu_str] if p]
        detail = "，".join(detail_parts)

        rich_summary = f"{name} | {detail} | 技能: {skills_str}"
        if summary and summary != "简历分析完成":
            rich_summary = f"{summary}\n\n📋 关键信息：{name} | {detail} | 技能: {skills_str}"

        return {
            "phase": InterviewPhase.RAG_RETRIEVAL.value,
            "resume_summary": rich_summary,
            "resume_analysis": {
                "name": name,
                "years_of_experience": years,
                "education": education,
                "skills": skills,
                "companies": companies,
                "roles": roles,
                "summary": summary,
                "strengths": strengths,
                "weaknesses": weaknesses,
            },
            "chat_history": [{
                "role": "system",
                "content": f"📋 简历分析完成\n{rich_summary}"
            }]
        }
    except Exception as e:
        # JSON 解析失败或 LLM 调用失败时的回退
        return {
            "phase": InterviewPhase.RAG_RETRIEVAL.value,
            "resume_summary": resume_text[:500].replace('\n', ' '),
            "resume_analysis": {"raw": resume_text[:500], "skills": [], "summary": "简历内容已接收"},
            "error_message": str(e),
            "chat_history": [{
                "role": "system",
                "content": "📋 简历已接收，正在分析中..."
            }]
        }


async def rag_retrieval_node(state: InterviewState) -> Dict[str, Any]:
    """
    RAG 检索节点：从知识库中检索与面试相关的上下文
    """
    job_title = state.get("job_position", {}).get("title", "")
    job_desc = state.get("job_position", {}).get("description", "")
    resume_text = state.get("resume_text", "")
    llm_config_dict = state.get("llm_config", {})

    llm_config = LLMConfig(**llm_config_dict) if llm_config_dict else None

    # 构建综合检索查询
    query = f"{job_title} {job_desc} 面试知识点"

    try:
        rag_context = build_rag_context(
            query=query,
            job_title=job_title,
            resume_text=resume_text,
            config=llm_config,
        )
    except Exception:
        rag_context = "暂无相关面试资料。"

    return {
        "phase": InterviewPhase.QUESTION_GENERATION.value,
        "rag_context": rag_context,
        "chat_history": [{
            "role": "system",
            "content": "知识库检索完成，正在生成面试问题..."
        }]
    }


async def generate_questions_node(state: InterviewState) -> Dict[str, Any]:
    """
    问题生成节点：基于职位、简历、知识库生成面试问题
    """
    job_position = state.get("job_position", {})
    job_info = f"""
职位：{job_position.get('title', '未指定')}
部门：{job_position.get('department', '未指定')}
描述：{job_position.get('description', '未指定')}
要求：{job_position.get('requirements', '未指定')}
技能：{', '.join(job_position.get('skills_required', []))}
"""

    # 优先使用结构化简历分析，回退到纯文本
    resume_analysis = state.get("resume_analysis", {})
    if resume_analysis and resume_analysis.get("skills"):
        resume_info = f"""
候选人：{resume_analysis.get('name', '未知')}
经验：{resume_analysis.get('years_of_experience', '未知')}年
学历：{resume_analysis.get('education', '未知')}
技能：{', '.join(resume_analysis.get('skills', []))}
公司：{', '.join(resume_analysis.get('companies', []))}
职位：{', '.join(resume_analysis.get('roles', []))}
优势：{', '.join(resume_analysis.get('strengths', []))}
不足：{', '.join(resume_analysis.get('weaknesses', []))}
总结：{resume_analysis.get('summary', '')}
"""
    else:
        resume_info = state.get("resume_summary", "") or state.get("resume_text", "")

    rag_context = state.get("rag_context", "")
    question_count = state.get("question_count", 5)
    interview_type = state.get("interview_type", "technical")
    language = state.get("language", "zh")

    llm_config = LLMConfig(**state.get("llm_config", {}))

    try:
        questions = await generate_questions(
            config=llm_config,
            job_info=job_info,
            resume_info=resume_info,
            knowledge_context=rag_context,
            question_count=question_count,
            interview_type=interview_type,
            language=language,
        )

        # 为每个问题添加索引
        for i, q in enumerate(questions):
            q["index"] = i

        return {
            "phase": InterviewPhase.ASKING.value,
            "questions": questions,
            "current_question_index": 0,
            "chat_history": [{
                "role": "system",
                "content": f"已生成 {len(questions)} 道面试题，开始面试。"
            }, {
                "role": "interviewer",
                "content": questions[0]["question"] if questions else "让我们开始面试吧。"
            }]
        }
    except Exception as e:
        # 如果 LLM 调用失败，使用预设问题
        fallback_questions = _get_fallback_questions(question_count, interview_type, language)
        for i, q in enumerate(fallback_questions):
            q["index"] = i

        return {
            "phase": InterviewPhase.ASKING.value,
            "questions": fallback_questions,
            "current_question_index": 0,
            "error_message": str(e),
            "chat_history": [{
                "role": "system",
                "content": f"问题生成遇到问题，使用预设题库。"
            }, {
                "role": "interviewer",
                "content": fallback_questions[0]["question"] if fallback_questions else "让我们开始吧。"
            }]
        }


async def ask_question_node(state: InterviewState) -> Dict[str, Any]:
    """
    提问节点：向候选人发出当前问题
    实际使用中，此节点将问题推送到前端
    """
    questions = state.get("questions", [])
    idx = state.get("current_question_index", 0)

    if idx >= len(questions):
        return {"phase": InterviewPhase.REPORT_GENERATION.value}

    current_q = questions[idx]

    return {
        "phase": InterviewPhase.ASKING.value,
        "chat_history": [{
            "role": "interviewer",
            "content": current_q.get("question", "")
        }]
    }


async def evaluate_answer_node(state: InterviewState) -> Dict[str, Any]:
    """
    答案评估节点：评估候选人的回答
    """
    questions = state.get("questions", [])
    idx = state.get("current_question_index", 0)
    answer = state.get("current_answer", "").strip()
    llm_config = LLMConfig(**state.get("llm_config", {}))
    language = state.get("language", "zh")

    if idx >= len(questions) or not answer:
        return {
            "phase": InterviewPhase.NEXT_QUESTION.value,
            "chat_history": [{
                "role": "system",
                "content": "候选人未作答，进入下一题。"
            }],
            "evaluations": [{"score": 0, "strengths": [], "improvements": [], "feedback": "未作答"}]
        }

    current_q = questions[idx]

    try:
        evaluation = await evaluate_answer(
            config=llm_config,
            question=current_q.get("question", ""),
            reference_answer=current_q.get("reference_answer", ""),
            candidate_answer=answer,
            language=language,
        )

        eval_msg = f"评分: {evaluation.get('score', 'N/A')}/100 | {evaluation.get('feedback', '')[:200]}"

        return {
            "phase": InterviewPhase.NEXT_QUESTION.value,
            "evaluations": [evaluation],
            "chat_history": [{
                "role": "system",
                "content": eval_msg
            }]
        }
    except Exception as e:
        return {
            "phase": InterviewPhase.NEXT_QUESTION.value,
            "error_message": str(e),
            "evaluations": [{"score": 50, "strengths": [], "improvements": [], "feedback": "评估出错"}]
        }


async def next_question_node(state: InterviewState) -> Dict[str, Any]:
    """
    下一题节点：移动到下一题或完成面试
    """
    questions = state.get("questions", [])
    current_idx = state.get("current_question_index", 0)
    next_idx = current_idx + 1

    if next_idx >= len(questions):
        return {
            "phase": InterviewPhase.REPORT_GENERATION.value,
            "chat_history": [{
                "role": "system",
                "content": "所有问题已完成，正在生成面试报告..."
            }]
        }

    next_q = questions[next_idx]

    return {
        "phase": InterviewPhase.ASKING.value,
        "current_question_index": next_idx,
        "chat_history": [{
            "role": "interviewer",
            "content": next_q.get("question", "")
        }]
    }


async def generate_report_node(state: InterviewState) -> Dict[str, Any]:
    """
    报告生成节点：综合所有信息生成最终面试报告
    """
    job_position = state.get("job_position", {})
    job_info = f"{job_position.get('title', '未指定')} - {job_position.get('department', '未指定')}"

    resume_info = state.get("resume_summary", "") or state.get("resume_text", "")
    questions = state.get("questions", [])
    evaluations = state.get("evaluations", [])
    chat_history = state.get("chat_history", [])
    llm_config = LLMConfig(**state.get("llm_config", {}))
    language = state.get("language", "zh")

    # 整理问答对：从 chat_history 中按顺序配对问题和回答
    qa_pairs = []
    candidate_answers = [m.get("content", "") for m in chat_history if m.get("role") == "candidate"]

    for i, q in enumerate(questions):
        answer = candidate_answers[i] if i < len(candidate_answers) else ""
        qa_pairs.append({
            "question": q.get("question", ""),
            "answer": answer or "(未作答)",
            "category": q.get("category", ""),
        })

    try:
        report = await generate_final_report(
            config=llm_config,
            job_info=job_info,
            resume_info=resume_info,
            questions_and_answers=qa_pairs,
            evaluations=evaluations,
            language=language,
        )
    except Exception as e:
        report = {
            "overall_score": sum(e.get("score", 0) for e in evaluations) / max(len(evaluations), 1),
            "scores_by_dimension": {},
            "strengths": [],
            "weaknesses": [],
            "summary": "报告生成时遇到错误，请查看各题详情。",
            "recommendation": "no_hire",
            "error": str(e)
        }

    return {
        "phase": InterviewPhase.COMPLETED.value,
        "final_report": report,
        "chat_history": [{
            "role": "system",
            "content": f"面试完成！总体评分: {report.get('overall_score', 'N/A')}/100"
        }]
    }


def _get_fallback_questions(count: int, interview_type: str, language: str) -> list:
    """预设后备面试问题"""
    zh_technical = [
        {"category": "technical", "difficulty": "easy",
         "question": "请介绍一下你最熟悉的一个技术项目，包括技术栈和架构设计。",
         "reference_answer": "应涵盖项目背景、技术选型理由、架构图、关键挑战。"},
        {"category": "technical", "difficulty": "medium",
         "question": "你在项目中遇到过什么技术难题？你是如何解决的？",
         "reference_answer": "描述具体问题、排查过程、解决方案和最终效果。"},
        {"category": "experience", "difficulty": "medium",
         "question": "请描述一次你与团队协作完成项目的经历。",
         "reference_answer": "包含团队规模、分工、沟通方式、遇到的协作问题和解决。"},
        {"category": "behavioral", "difficulty": "medium",
         "question": "当你和同事在技术方案上有分歧时，你会怎么处理？",
         "reference_answer": "强调数据驱动、尊重他人、以项目目标为导向。"},
        {"category": "technical", "difficulty": "hard",
         "question": "如果让你从零设计一个高并发系统，你会考虑哪些方面？",
         "reference_answer": "负载均衡、缓存策略、数据库分库分表、异步消息队列、容灾等。"},
        {"category": "behavioral", "difficulty": "medium",
         "question": "你最近学到了什么新技术？你是如何学习的？",
         "reference_answer": "学习方式、实践项目、对工作的帮助。"},
        {"category": "experience", "difficulty": "hard",
         "question": "请分享一次你主导项目并推动落地的经历。",
         "reference_answer": "项目背景、你的角色、关键决策、最终成果和反思。"},
        {"category": "technical", "difficulty": "hard",
         "question": "你如何保证代码质量？请谈谈你的实践经验。",
         "reference_answer": "CR、单测、CI/CD、lint、自动化测试覆盖率、编码规范。"},
    ]

    return zh_technical[:count]


def _is_garbage_text(text: str) -> bool:
    """检测文本是否为二进制垃圾（如图片文件被当作文本读取）"""
    if len(text) < 10:
        return False
    sample = text[:2000]
    garbage = 0
    for ch in sample:
        code = ord(ch)
        if (code < 0x20 and code not in (0x0a, 0x0d, 0x09)) or (0x80 <= code < 0xA0):
            garbage += 1
    return garbage / len(sample) > 0.2
