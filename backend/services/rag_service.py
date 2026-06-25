"""
RAG 服务层 - 基于 ChromaDB 的向量检索增强生成
用于从知识库中检索与面试相关的上下文信息
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from langchain_openai import OpenAIEmbeddings

from config import LLMConfig


# ChromaDB 持久化路径
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# 全局 ChromaDB 客户端
_chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_or_create_collection(collection_name: str = "knowledge_base"):
    """获取或创建向量集合"""
    return _chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def get_embedding_function(config: Optional[LLMConfig] = None):
    """
    获取嵌入函数。优先使用用户配置的 API，否则使用默认开源模型。
    兼容 OpenAI / DeepSeek / 智谱 等 API
    """
    if config and config.api_key:
        base_url = config.get_base_url()
        return OpenAIEmbeddings(
            model="text-embedding-ada-002" if config.provider == "openai" else "text-embedding-v2",
            api_key=config.api_key,
            base_url=base_url,
        )
    else:
        # 回退：使用本地模型或简单的 TF-IDF
        # 这里使用 sentence-transformers 作为备选
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
        except ImportError:
            return None


def add_knowledge_to_rag(
    knowledge_id: str,
    title: str,
    content: str,
    metadata: Dict[str, Any] = None,
    config: Optional[LLMConfig] = None,
) -> None:
    """
    将知识库条目加入向量数据库
    """
    collection = get_or_create_collection()
    embedding_fn = get_embedding_function(config)

    text_to_embed = f"{title}\n\n{content}"

    if embedding_fn:
        # 使用语义嵌入
        embedding = embedding_fn.embed_query(text_to_embed)
        collection.add(
            ids=[knowledge_id],
            embeddings=[embedding],
            documents=[text_to_embed],
            metadatas=[metadata or {"title": title}]
        )
    else:
        # 无嵌入模型时，存储原始文本用于关键词检索
        collection.add(
            ids=[knowledge_id],
            documents=[text_to_embed],
            metadatas=[metadata or {"title": title}]
        )


def remove_knowledge_from_rag(knowledge_id: str) -> None:
    """从向量数据库中删除知识条目"""
    collection = get_or_create_collection()
    try:
        collection.delete(ids=[knowledge_id])
    except Exception:
        pass


def search_knowledge(
    query: str,
    top_k: int = 5,
    config: Optional[LLMConfig] = None,
) -> List[Dict[str, Any]]:
    """
    检索与查询最相关的知识条目
    """
    collection = get_or_create_collection()
    embedding_fn = get_embedding_function(config)

    if embedding_fn and collection.count() > 0:
        query_embedding = embedding_fn.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
    elif collection.count() > 0:
        # 关键词检索（回退方案）
        results = collection.query(
            query_texts=[query],
            n_results=min(top_k, collection.count())
        )
    else:
        return []

    items = []
    if results.get("documents") and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results.get("metadatas", [[{}]])[0][i] if results.get("metadatas") else {}
            distance = results.get("distances", [[0]])[0][i] if results.get("distances") else 0
            items.append({
                "content": doc,
                "title": metadata.get("title", ""),
                "relevance": 1.0 - min(float(distance), 1.0)  # cosine 距离转相似度
            })

    return items


def build_rag_context(
    query: str,
    job_title: str = "",
    resume_text: str = "",
    top_k: int = 8,
    config: Optional[LLMConfig] = None,
) -> str:
    """
    构建 RAG 上下文：综合检索知识库中与面试相关的信息
    """
    # 多查询检索 - 提高召回率
    queries = [query]
    if job_title:
        queries.append(f"{job_title} 面试 技术要求 能力")
        queries.append(f"{job_title} 岗位职责 工作内容")
    if resume_text:
        # 从简历中提取关键词做额外检索
        queries.append(f"{resume_text[:200]} 相关技术")

    all_items = []
    seen_ids = set()

    for q in queries[:3]:  # 限制查询数量
        items = search_knowledge(q, top_k=top_k // 2, config=config)
        for item in items:
            key = item["title"] + item["content"][:50]
            if key not in seen_ids:
                seen_ids.add(key)
                all_items.append(item)

    # 按相关度排序
    all_items.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    all_items = all_items[:top_k]

    # 构建上下文文本
    context_parts = []
    for i, item in enumerate(all_items):
        context_parts.append(
            f"[知识条目 {i+1}] {item['title']}\n{item['content']}\n"
        )

    return "\n".join(context_parts) if context_parts else "暂无相关知识库内容。"


def rebuild_knowledge_index(knowledge_items: List[Dict[str, Any]], config: Optional[LLMConfig] = None) -> int:
    """
    重建整个知识库的向量索引
    """
    collection = get_or_create_collection()
    # 清空现有索引
    try:
        existing = collection.get()
        if existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    # 重新添加
    embedding_fn = get_embedding_function(config)
    count = 0

    for item in knowledge_items:
        text = f"{item.get('title', '')}\n\n{item.get('content', '')}"
        meta = {
            "title": item.get("title", ""),
            "category": item.get("category", ""),
            "tags": ",".join(item.get("tags", []))
        }

        if embedding_fn:
            embedding = embedding_fn.embed_query(text)
            collection.add(
                ids=[item["id"]],
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta]
            )
        else:
            collection.add(
                ids=[item["id"]],
                documents=[text],
                metadatas=[meta]
            )
        count += 1

    return count
