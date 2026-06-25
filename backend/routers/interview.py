"""
面试会话 API 路由
核心功能：创建面试、提交回答、获取状态、生成报告
"""

import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import (
    InterviewSessionCreate,
    AnswerSubmission,
    ResumeAnalyzeRequest,
    APIResponse,
    InterviewPhase,
)
from graph import create_initial_state
from graph.nodes import (
    init_session,
    analyze_resume_node,
    rag_retrieval_node,
    generate_questions_node,
    ask_question_node,
    evaluate_answer_node,
    next_question_node,
    generate_report_node,
)
from services.mongodb import (
    save_interview_session,
    get_interview_session,
    list_interview_sessions,
    save_report,
    get_report,
)
from services.llm_service import analyze_resume as llm_analyze_resume
from config import LLMConfig

router = APIRouter(prefix="/api/interview", tags=["interview"])

# 运行时状态缓存（内存）
_session_states: dict[str, dict] = {}


def _merge_state(state: dict, result: dict) -> None:
    """
    合并节点返回结果到 state。
    chat_history 和 evaluations 使用 operator.add 语义（追加），
    其他字段正常替换。
    """
    for key, value in result.items():
        if key in ("chat_history", "evaluations") and isinstance(value, list):
            # 追加而非替换
            if key not in state:
                state[key] = []
            state[key].extend(value)
        else:
            state[key] = value


def _serialize_state(state: dict) -> dict:
    """序列化 LangGraph 状态为前端可用的格式"""
    questions = state.get("questions", [])
    evaluations = state.get("evaluations", [])
    current_idx = state.get("current_question_index", 0)

    return {
        "session_id": state.get("session_id", ""),
        "phase": state.get("phase", "init"),
        "current_question_index": current_idx,
        "total_questions": len(questions),
        "current_question": questions[current_idx].get("question", "") if questions and current_idx < len(questions) else "",
        "questions": questions,
        "chat_history": state.get("chat_history", []),
        "evaluations": evaluations,
        "final_report": state.get("final_report", {}),
        "resume_summary": state.get("resume_summary", ""),
        "resume_analysis": state.get("resume_analysis", {}),
        "error_message": state.get("error_message", ""),
    }


@router.post("/create", response_model=APIResponse)
async def create_session(req: InterviewSessionCreate):
    """
    创建面试会话
    1. 初始化 LangGraph 状态
    2. 执行 init → resume_analysis → rag_retrieval → generate_questions
    3. 返回第一个问题
    """
    session_id = uuid.uuid4().hex[:16]

    # 构建 LLM 配置
    llm_config = req.llm_config.model_dump()

    # 构建职位信息
    job_position = {}
    if req.job_position:
        job_position = req.job_position.model_dump()
    elif req.job_position_id:
        from services.mongodb import get_job_position
        job_doc = await get_job_position(req.job_position_id)
        if job_doc:
            job_position = job_doc

    # 创建初始状态
    state = create_initial_state(
        session_id=session_id,
        llm_config=llm_config,
        job_position=job_position,
        resume_text=req.resume_text,
        knowledge_items=[k.model_dump() for k in req.knowledge_items] if req.knowledge_items else [],
        interview_type=req.interview_type,
        question_count=req.question_count,
        language=req.language,
    )

    try:
        # 逐步执行面试初始化流程: init → resume_analysis → rag_retrieval → generate_questions

        # Step 1: init
        result = await init_session(state)
        _merge_state(state, result)

        # Step 2: resume_analysis
        result = await analyze_resume_node(state)
        _merge_state(state, result)

        # Step 3: rag_retrieval
        result = await rag_retrieval_node(state)
        _merge_state(state, result)

        # Step 4: generate_questions
        result = await generate_questions_node(state)
        _merge_state(state, result)

        # 缓存状态
        _session_states[session_id] = dict(state)

        # 持久化到 MongoDB
        await save_interview_session(session_id, _serialize_state(state))

        return APIResponse(
            success=True,
            message="面试会话创建成功",
            data=_serialize_state(state)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建面试失败: {str(e)}")


@router.post("/answer", response_model=APIResponse)
async def submit_answer(req: AnswerSubmission):
    """
    提交候选人的回答
    1. 接收回答
    2. 执行 evaluate_answer → next_question → ask_question
    3. 返回下一个问题或进入报告生成
    """
    session_id = req.session_id
    state = _session_states.get(session_id)

    if not state:
        # 尝试从 MongoDB 恢复
        db_state = await get_interview_session(session_id)
        if not db_state:
            raise HTTPException(status_code=404, detail="会话不存在")
        state = db_state
        _session_states[session_id] = state

    # 记录候选人回答
    state["current_answer"] = req.answer
    state["chat_history"] = state.get("chat_history", []) + [{
        "role": "candidate",
        "content": req.answer
    }]

    try:
        # Step 1: 评估回答
        result = await evaluate_answer_node(state)
        _merge_state(state, result)

        # Step 2: 决定下一题或生成报告
        result = await next_question_node(state)
        _merge_state(state, result)

        new_phase = state.get("phase", "")

        # Step 3: 如果还有问题，发下一个问题
        if new_phase == InterviewPhase.ASKING.value:
            result = await ask_question_node(state)
            _merge_state(state, result)

        # Step 4: 如果是报告生成阶段
        elif new_phase == InterviewPhase.REPORT_GENERATION.value:
            result = await generate_report_node(state)
            _merge_state(state, result)

            # 持久化报告
            report_data = state.get("final_report", {})
            await save_report({
                "session_id": session_id,
                "job_title": state.get("job_position", {}).get("title", ""),
                "overall_score": report_data.get("overall_score", 0),
                "scores_by_dimension": report_data.get("scores_by_dimension", {}),
                "strengths": report_data.get("strengths", []),
                "weaknesses": report_data.get("weaknesses", []),
                "summary": report_data.get("summary", ""),
                "recommendation": report_data.get("recommendation", ""),
                "detailed_feedback": state.get("evaluations", []),
            })

        # 更新缓存
        _session_states[session_id] = dict(state)

        # 持久化
        await save_interview_session(session_id, _serialize_state(state))

        return APIResponse(
            success=True,
            message="回答已评估" if new_phase != InterviewPhase.COMPLETED.value else "面试已完成",
            data=_serialize_state(state)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理回答失败: {str(e)}")


@router.get("/state/{session_id}", response_model=APIResponse)
async def get_session_state(session_id: str):
    """获取会话当前状态"""
    state = _session_states.get(session_id)
    if not state:
        state = await get_interview_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="会话不存在")

    return APIResponse(
        success=True,
        data=_serialize_state(state)
    )


@router.get("/sessions", response_model=APIResponse)
async def list_sessions():
    """列出所有面试会话"""
    sessions = await list_interview_sessions()
    return APIResponse(
        success=True,
        data=sessions
    )


@router.get("/report/{session_id}", response_model=APIResponse)
async def get_session_report(session_id: str):
    """获取面试报告"""
    # 先检查内存
    state = _session_states.get(session_id)
    if state and state.get("final_report"):
        return APIResponse(
            success=True,
            data={
                "session_id": session_id,
                "report": state["final_report"],
                "evaluations": state.get("evaluations", []),
                "questions": state.get("questions", []),
            }
        )

    # MongoDB 查询
    report = await get_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    return APIResponse(
        success=True,
        data=report
    )


@router.get("/reports", response_model=APIResponse)
async def list_reports():
    """列出所有面试报告"""
    from services.mongodb import list_reports as db_list_reports
    reports = await db_list_reports()
    return APIResponse(
        success=True,
        data=reports
    )


@router.post("/resume/analyze", response_model=APIResponse)
async def analyze_resume_endpoint(req: ResumeAnalyzeRequest):
    """单独分析简历"""
    if not req.resume_text:
        raise HTTPException(status_code=400, detail="请提供简历文本")

    config = LLMConfig(**(req.llm_config or {}))
    try:
        result = await llm_analyze_resume(config, req.resume_text)
        return APIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume/extract-pdf", response_model=APIResponse)
async def extract_pdf_text(file: UploadFile = File(...)):
    """从 PDF 文件中提取文本（支持文字 PDF 和扫描件/图片 PDF OCR）"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件")

    filename = file.filename.lower()
    if not filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    try:
        content = await file.read()

        if not content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="文件不是有效的 PDF 格式")

        import io
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(content))
        total_pages = len(reader.pages)

        # 步骤1：先尝试直接提取文字
        texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                texts.append(page_text.strip())

        full_text = "\n\n".join(texts)

        # 步骤2：如果文字太少（<50字符/页），说明是扫描件，用 OCR
        avg_chars = len(full_text) / max(total_pages, 1)
        if avg_chars < 50:
            import fitz  # PyMuPDF
            from services.ocr_service import image_to_text

            doc = fitz.open(stream=content, filetype="pdf")
            ocr_texts = []

            for i in range(min(total_pages, 5)):  # 最多 OCR 前5页
                page = doc[i]
                # 渲染为图片（200 DPI）
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                page_ocr = image_to_text(img_bytes)
                if page_ocr.strip():
                    ocr_texts.append(f"--- 第{i+1}页（OCR识别）---\n{page_ocr.strip()}")

            doc.close()

            ocr_full = "\n\n".join(ocr_texts)
            if ocr_full.strip():
                full_text = ocr_full
            elif not full_text.strip():
                full_text = ""

        if not full_text.strip():
            raise HTTPException(
                status_code=400,
                detail="PDF 中未检测到文字（可能是空白页或极低质量扫描件）"
            )

        if len(full_text) > 12000:
            full_text = full_text[:12000] + "\n\n...(内容过长，已截断)"

        method = "OCR识别" if avg_chars < 50 else "直接提取"
        return APIResponse(
            success=True,
            message=f"{method}完成，{total_pages}页，共{len(full_text)}字符",
            data={"text": full_text, "pages": total_pages, "method": method}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 解析失败: {str(e)}")


@router.post("/resume/validate", response_model=APIResponse)
async def validate_resume_text(req: ResumeAnalyzeRequest):
    """验证简历文本是否有效（非二进制垃圾）"""
    text = req.resume_text or ""

    if len(text) < 10:
        return APIResponse(success=False, message="文本太短，请提供完整简历", data={"valid": False})

    # 检测乱码比例
    sample = text[:2000]
    garbage = 0
    for ch in sample:
        code = ord(ch)
        if (code < 0x20 and code not in (0x0a, 0x0d, 0x09)) or (0x80 <= code < 0xA0):
            garbage += 1

    ratio = garbage / max(len(sample), 1)

    if ratio > 0.2:
        return APIResponse(
            success=False,
            message=f"检测到 {ratio*100:.0f}% 乱码字符，请确认上传的是文本文件而非图片",
            data={"valid": False, "garbage_ratio": round(ratio, 3)}
        )

    return APIResponse(success=True, message="简历文本有效", data={"valid": True})


@router.post("/resume/ocr", response_model=APIResponse)
async def ocr_image(file: UploadFile = File(...)):
    """OCR 识别图片简历中的文字（支持 JPG/PNG/BMP/WEBP）"""
    from services.ocr_service import image_to_text, is_image_file

    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件")

    if not is_image_file(file.filename):
        raise HTTPException(status_code=400, detail="仅支持图片格式：JPG/PNG/BMP/WEBP")

    try:
        content = await file.read()

        # 校验是真实图片（魔术字节）
        if len(content) < 100:
            raise HTTPException(status_code=400, detail="文件太小，不是有效图片")

        text = image_to_text(content)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="图片中未识别到文字（可能是纯图片简历、扫描件质量过低或手写内容）"
            )

        # 截断过长文本
        if len(text) > 15000:
            text = text[:15000] + "\n\n...(内容过长，已截断)"

        return APIResponse(
            success=True,
            message=f"OCR 识别完成，共 {len(text)} 字符",
            data={"text": text}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 识别失败: {str(e)}")
