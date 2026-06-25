"""
LangGraph 面试状态定义
使用 TypedDict + Annotated 定义图的状态结构
"""

from typing import TypedDict, List, Dict, Any, Annotated
from enum import Enum
import operator


class InterviewPhase(str, Enum):
    INIT = "init"
    RESUME_ANALYSIS = "resume_analysis"
    RAG_RETRIEVAL = "rag_retrieval"
    QUESTION_GENERATION = "question_generation"
    ASKING = "asking"
    EVALUATING = "evaluating"
    NEXT_QUESTION = "next_question"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"
    ERROR = "error"


class InterviewState(TypedDict):
    """面试会话的完整状态"""
    # 会话标识
    session_id: str

    # 当前阶段
    phase: str

    # LLM 配置 (前端传入)
    llm_config: Dict[str, Any]

    # 职位信息
    job_position: Dict[str, Any]

    # 简历信息
    resume_text: str
    resume_summary: str
    resume_analysis: Dict[str, Any]

    # 知识库 / RAG 上下文
    knowledge_items: List[Dict[str, Any]]
    rag_context: str

    # 面试配置
    interview_type: str          # technical | behavioral | mixed
    question_count: int
    language: str

    # 问题列表
    questions: List[Dict[str, Any]]

    # 当前问题索引
    current_question_index: int

    # 对话历史
    chat_history: Annotated[List[Dict[str, str]], operator.add]

    # 当前候选人的回答
    current_answer: str

    # 评估结果列表
    evaluations: Annotated[List[Dict[str, Any]], operator.add]

    # 最终报告
    final_report: Dict[str, Any]

    # 错误信息
    error_message: str


def create_initial_state(
    session_id: str,
    llm_config: Dict[str, Any],
    job_position: Dict[str, Any] = None,
    resume_text: str = "",
    knowledge_items: List[Dict[str, Any]] = None,
    interview_type: str = "technical",
    question_count: int = 5,
    language: str = "zh",
) -> InterviewState:
    """创建初始面试状态"""
    return InterviewState(
        session_id=session_id,
        phase=InterviewPhase.INIT.value,
        llm_config=llm_config,
        job_position=job_position or {},
        resume_text=resume_text,
        resume_summary="",
        resume_analysis={},
        knowledge_items=knowledge_items or [],
        rag_context="",
        interview_type=interview_type,
        question_count=question_count,
        language=language,
        questions=[],
        current_question_index=0,
        chat_history=[],
        current_answer="",
        evaluations=[],
        final_report={},
        error_message="",
    )
