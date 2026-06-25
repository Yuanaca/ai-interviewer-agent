"""
Pydantic 数据模型 - 前后端数据交换格式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ===================== LLM 配置 =====================

class LLMConfigRequest(BaseModel):
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


# ===================== 职位管理 =====================

class JobPosition(BaseModel):
    id: str = ""
    title: str
    department: str = ""
    description: str = ""
    requirements: str = ""
    responsibilities: str = ""
    skills_required: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class JobPositionCreate(BaseModel):
    title: str
    department: str = ""
    description: str = ""
    requirements: str = ""
    responsibilities: str = ""
    skills_required: List[str] = Field(default_factory=list)


# ===================== 知识库 =====================

class KnowledgeItem(BaseModel):
    id: str = ""
    title: str
    content: str
    category: str = "general"      # company | tech | role | general
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None


class KnowledgeItemCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)


# ===================== 面试会话 =====================

class InterviewSessionCreate(BaseModel):
    job_position_id: str = ""
    job_position: Optional[JobPosition] = None
    resume_text: str = ""
    interview_type: str = "technical"
    question_count: int = 5
    language: str = "zh"
    llm_config: LLMConfigRequest = Field(default_factory=LLMConfigRequest)
    knowledge_items: List[KnowledgeItem] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: str                    # "interviewer" | "candidate" | "system"
    content: str
    timestamp: Optional[str] = None


class AnswerSubmission(BaseModel):
    session_id: str
    answer: str
    question_index: int


# ===================== 面试状态 =====================

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


class QuestionItem(BaseModel):
    index: int
    question: str
    category: str = ""           # technical | behavioral | experience
    difficulty: str = "medium"
    reference_answer: str = ""   # 参考答案（可选）


class EvaluationResult(BaseModel):
    score: float = 0.0           # 0-100
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    feedback: str = ""
    keyword_match: List[str] = Field(default_factory=list)


class InterviewState(BaseModel):
    """面试会话的完整状态"""
    session_id: str
    phase: InterviewPhase = InterviewPhase.INIT
    job_position: Optional[JobPosition] = None
    resume_text: str = ""
    resume_summary: str = ""
    questions: List[QuestionItem] = Field(default_factory=list)
    current_question_index: int = 0
    chat_history: List[ChatMessage] = Field(default_factory=list)
    evaluations: List[EvaluationResult] = Field(default_factory=list)
    final_report: str = ""
    knowledge_context: str = ""


# ===================== 报告 =====================

class InterviewReport(BaseModel):
    session_id: str
    candidate_name: str = ""
    job_title: str = ""
    overall_score: float = 0.0
    scores_by_dimension: Dict[str, float] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    detailed_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    recommendation: str = ""     # strong_hire | hire | weak_hire | no_hire
    created_at: str = ""


# ===================== 搜索 & 简历分析请求 =====================

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class ResumeAnalyzeRequest(BaseModel):
    resume_text: str
    llm_config: Optional[Dict[str, Any]] = None


# ===================== 通用响应 =====================

class APIResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Any = None
