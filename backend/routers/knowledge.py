"""
知识库管理 API 路由
包含 RAG 向量索引同步
"""

from fastapi import APIRouter, HTTPException
from models.schemas import (
    KnowledgeItemCreate,
    KnowledgeSearchRequest,
    APIResponse,
)
from services.mongodb import (
    create_knowledge_item,
    list_knowledge_items,
    get_knowledge_item,
    update_knowledge_item,
    delete_knowledge_item,
)
from services.rag_service import (
    add_knowledge_to_rag,
    remove_knowledge_from_rag,
    search_knowledge,
    rebuild_knowledge_index,
)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/", response_model=APIResponse)
async def create_item(data: KnowledgeItemCreate):
    """添加知识条目（同步到 MongoDB + RAG 向量索引）"""
    try:
        item_dict = data.model_dump()
        item_id = await create_knowledge_item(item_dict)

        # 同步到 RAG 向量索引
        try:
            add_knowledge_to_rag(
                knowledge_id=item_id,
                title=data.title,
                content=data.content,
                metadata={"category": data.category, "tags": ",".join(data.tags)}
            )
        except Exception as e:
            print(f"RAG sync warning: {e}")

        return APIResponse(
            success=True,
            message="知识条目已添加",
            data={"id": item_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_items(category: str = None):
    """知识列表"""
    try:
        items = await list_knowledge_items(category)
        return APIResponse(success=True, data=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=APIResponse)
async def get_item(item_id: str):
    """获取知识详情"""
    item = await get_knowledge_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="条目不存在")
    return APIResponse(success=True, data=item)


@router.put("/{item_id}", response_model=APIResponse)
async def update_item(item_id: str, data: KnowledgeItemCreate):
    """更新知识条目"""
    ok = await update_knowledge_item(item_id, data.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="条目不存在")

    # 同步更新 RAG 索引（先删除再添加）
    try:
        remove_knowledge_from_rag(item_id)
        add_knowledge_to_rag(item_id, data.title, data.content)
    except Exception as e:
        print(f"RAG sync warning: {e}")

    return APIResponse(success=True, message="已更新")


@router.delete("/{item_id}", response_model=APIResponse)
async def delete_item(item_id: str):
    """删除知识条目"""
    ok = await delete_knowledge_item(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="条目不存在")

    # 同步删除 RAG 索引
    try:
        remove_knowledge_from_rag(item_id)
    except Exception as e:
        print(f"RAG sync warning: {e}")

    return APIResponse(success=True, message="已删除")


@router.post("/search", response_model=APIResponse)
async def search_knowledge_items(req: KnowledgeSearchRequest):
    """RAG 向量检索"""
    try:
        results = search_knowledge(req.query, req.top_k)
        return APIResponse(success=True, data=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild-index", response_model=APIResponse)
async def rebuild_rag_index():
    """重建整个知识库的 RAG 向量索引"""
    try:
        items = await list_knowledge_items()
        count = rebuild_knowledge_index(items)
        return APIResponse(
            success=True,
            message=f"索引重建完成，共 {count} 条",
            data={"count": count}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
