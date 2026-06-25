"""
LangGraph 面试流程图 - 核心编排逻辑

面试流程:
  INIT → RESUME_ANALYSIS → RAG_RETRIEVAL → QUESTION_GENERATION
    → ASKING ←→ EVALUATING → NEXT_QUESTION
    → REPORT_GENERATION → COMPLETED

支持两种模式:
  1. 自动模式: 一次性运行整个流程
  2. 交互模式: 逐步执行，每次等待候选人回答
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import InterviewState, InterviewPhase
from .nodes import (
    init_session,
    analyze_resume_node,
    rag_retrieval_node,
    generate_questions_node,
    ask_question_node,
    evaluate_answer_node,
    next_question_node,
    generate_report_node,
)


def build_interview_graph() -> StateGraph:
    """
    构建面试 LangGraph 图
    
    图结构:
    
    [INIT] → [RESUME_ANALYSIS] → [RAG_RETRIEVAL] → [QUESTION_GENERATION]
                                                        ↓
    [COMPLETED] ← [REPORT_GENERATION] ← [NEXT_QUESTION] ← [EVALUATING] ← [ASKING]
                                               ↑                          ↓
                                               └──────── (循环) ──────────┘
    """
    graph = StateGraph(InterviewState)

    # 1. 添加所有节点
    graph.add_node("init", init_session)
    graph.add_node("resume_analysis", analyze_resume_node)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("generate_questions", generate_questions_node)
    graph.add_node("ask_question", ask_question_node)
    graph.add_node("evaluate_answer", evaluate_answer_node)
    graph.add_node("next_question", next_question_node)
    graph.add_node("generate_report", generate_report_node)

    # 2. 定义流程边

    # 入口 → 初始化
    graph.set_entry_point("init")

    # init → resume_analysis (总是执行)
    graph.add_edge("init", "resume_analysis")

    # resume_analysis → rag_retrieval
    graph.add_edge("resume_analysis", "rag_retrieval")

    # rag_retrieval → generate_questions
    graph.add_edge("rag_retrieval", "generate_questions")

    # generate_questions → ask_question
    graph.add_edge("generate_questions", "ask_question")

    # ask_question → evaluate_answer (等待候选人回答后)
    graph.add_edge("ask_question", "evaluate_answer")

    # evaluate_answer → next_question (条件路由)
    graph.add_conditional_edges(
        "evaluate_answer",
        _route_after_evaluation,
        {
            "next": "next_question",
            "report": "generate_report",
        }
    )

    # next_question → ask_question (循环) 或 → generate_report
    graph.add_conditional_edges(
        "next_question",
        _route_after_next,
        {
            "ask": "ask_question",
            "report": "generate_report",
        }
    )

    # generate_report → END
    graph.add_edge("generate_report", END)

    return graph


def _route_after_evaluation(state: InterviewState) -> str:
    """评估后的路由：判断是否继续面试"""
    questions = state.get("questions", [])
    current_idx = state.get("current_question_index", 0)

    # 还有问题 → 进入 next_question
    if current_idx < len(questions) - 1:
        return "next"
    else:
        return "report"


def _route_after_next(state: InterviewState) -> str:
    """下一题后的路由：继续提问还是生成报告"""
    questions = state.get("questions", [])
    next_idx = state.get("current_question_index", 0)

    if next_idx < len(questions):
        return "ask"
    else:
        return "report"


def create_interview_graph():
    """创建编译好的面试图（带记忆）"""
    memory = MemorySaver()
    graph = build_interview_graph()
    return graph.compile(checkpointer=memory)
