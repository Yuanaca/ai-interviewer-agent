"""
MongoDB 数据库连接与操作层
使用 motor (异步驱动) 进行所有数据库操作
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import uuid

# MongoDB 连接配置
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "interview_intelligence")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def get_db() -> AsyncIOMotorDatabase:
    """获取数据库实例（懒加载）"""
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI, maxPoolSize=10)
        _db = _client[DB_NAME]
        # 创建索引
        await _setup_indexes(_db)
    return _db


async def close_db():
    """关闭数据库连接"""
    global _client
    if _client:
        _client.close()
        _client = None


async def _setup_indexes(db: AsyncIOMotorDatabase):
    """初始化数据库索引"""
    # 职位表索引
    await db.job_positions.create_index("title")
    await db.job_positions.create_index("created_at")

    # 知识库索引
    await db.knowledge_items.create_index("category")
    await db.knowledge_items.create_index("tags")

    # 面试会话索引
    await db.interview_sessions.create_index("session_id", unique=True)
    await db.interview_sessions.create_index("created_at")

    # 报告索引
    await db.reports.create_index("session_id", unique=True)
    await db.reports.create_index("created_at")


def _now() -> str:
    return datetime.now().isoformat()


def _gen_id() -> str:
    return uuid.uuid4().hex[:16]


# ===================== 职位管理 CRUD =====================

async def create_job_position(data: dict) -> str:
    db = await get_db()
    data["id"] = _gen_id()
    data["created_at"] = _now()
    data["updated_at"] = _now()
    await db.job_positions.insert_one(data)
    return data["id"]


async def list_job_positions() -> List[dict]:
    db = await get_db()
    cursor = db.job_positions.find().sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items


async def get_job_position(job_id: str) -> Optional[dict]:
    db = await get_db()
    doc = await db.job_positions.find_one({"id": job_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def update_job_position(job_id: str, data: dict) -> bool:
    db = await get_db()
    data["updated_at"] = _now()
    result = await db.job_positions.update_one(
        {"id": job_id}, {"$set": data}
    )
    return result.modified_count > 0


async def delete_job_position(job_id: str) -> bool:
    db = await get_db()
    result = await db.job_positions.delete_one({"id": job_id})
    return result.deleted_count > 0


# ===================== 知识库 CRUD =====================

async def create_knowledge_item(data: dict) -> str:
    db = await get_db()
    data["id"] = _gen_id()
    data["created_at"] = _now()
    await db.knowledge_items.insert_one(data)
    return data["id"]


async def list_knowledge_items(category: str = None) -> List[dict]:
    db = await get_db()
    query = {}
    if category:
        query["category"] = category
    cursor = db.knowledge_items.find(query).sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items


async def get_knowledge_item(item_id: str) -> Optional[dict]:
    db = await get_db()
    doc = await db.knowledge_items.find_one({"id": item_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def update_knowledge_item(item_id: str, data: dict) -> bool:
    db = await get_db()
    result = await db.knowledge_items.update_one(
        {"id": item_id}, {"$set": data}
    )
    return result.modified_count > 0


async def delete_knowledge_item(item_id: str) -> bool:
    db = await get_db()
    result = await db.knowledge_items.delete_one({"id": item_id})
    return result.deleted_count > 0


# ===================== 面试会话 CRUD =====================

async def save_interview_session(session_id: str, data: dict) -> None:
    db = await get_db()
    data["session_id"] = session_id
    data["updated_at"] = _now()
    await db.interview_sessions.replace_one(
        {"session_id": session_id}, data, upsert=True
    )


async def get_interview_session(session_id: str) -> Optional[dict]:
    db = await get_db()
    doc = await db.interview_sessions.find_one({"session_id": session_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def list_interview_sessions() -> List[dict]:
    db = await get_db()
    cursor = db.interview_sessions.find().sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items


# ===================== 报告 CRUD =====================

async def save_report(data: dict) -> None:
    db = await get_db()
    data["created_at"] = _now()
    await db.reports.replace_one(
        {"session_id": data["session_id"]}, data, upsert=True
    )


async def get_report(session_id: str) -> Optional[dict]:
    db = await get_db()
    doc = await db.reports.find_one({"session_id": session_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def list_reports() -> List[dict]:
    db = await get_db()
    cursor = db.reports.find().sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items
