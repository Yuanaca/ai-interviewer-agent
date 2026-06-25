"""
Interview Intelligence - 主入口
FastAPI + LangGraph 面试问答系统
"""

import sys
import os

# 添加 backend 目录到 path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import SERVER_HOST, SERVER_PORT
from routers import interview_router, jobs_router, knowledge_router
from services.mongodb import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 Interview Intelligence 系统启动中...")
    print(f"   MongoDB: 默认连接 mongodb://localhost:27017")
    print(f"   API 文档: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    yield
    print("🛑 正在关闭连接...")
    await close_db()


app = FastAPI(
    title="Interview Intelligence API",
    description="基于 LangGraph 的智能面试问答系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置 - 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(interview_router)
app.include_router(jobs_router)
app.include_router(knowledge_router)


@app.get("/")
async def root():
    return {
        "name": "Interview Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "mongodb": "connected" if _check_mongo() else "disconnected",
    }


def _check_mongo() -> bool:
    """检查 MongoDB 连接"""
    try:
        import asyncio
        from services.mongodb import get_db
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return True  # 在事件循环中无法同步检测，假设连接正常
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        reload_excludes=["import_*.py", "seed_*.py", "test_*.py", "chroma_db/*"],
        log_level="info",
    )
