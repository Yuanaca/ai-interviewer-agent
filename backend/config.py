"""
全局配置模块 - 系统运行时的动态配置
模型选择与 API Key 由前端传入，后端不做持久化存储
"""

import os
from typing import Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM 配置 - 由前端在每次请求时传入"""
    provider: str = "openai"          # openai | anthropic | deepseek | zhipu | qwen | ollama
    model_name: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: Optional[str] = None    # 自定义 API 端点（兼容各种代理）
    temperature: float = 0.7
    max_tokens: int = 4096

    def get_base_url(self) -> Optional[str]:
        if self.base_url:
            return self.base_url
        # 默认端点映射
        defaults = {
            "openai": "https://api.openai.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "ollama": "http://localhost:11434/v1",
        }
        return defaults.get(self.provider)


class InterviewConfig(BaseModel):
    """面试会话配置"""
    session_id: str
    job_position_id: str = ""
    resume_text: str = ""
    interview_type: str = "technical"  # technical | behavioral | mixed
    question_count: int = 5
    language: str = "zh"               # zh | en
    custom_prompt: Optional[str] = None


# 服务端口
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
