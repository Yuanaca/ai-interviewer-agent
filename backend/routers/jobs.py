"""
职位管理 API 路由
"""

from fastapi import APIRouter, HTTPException
from models.schemas import (
    JobPositionCreate,
    APIResponse,
)
from services.mongodb import (
    create_job_position,
    list_job_positions,
    get_job_position,
    update_job_position,
    delete_job_position,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/", response_model=APIResponse)
async def create_job(data: JobPositionCreate):
    """创建职位"""
    try:
        job_id = await create_job_position(data.model_dump())
        return APIResponse(
            success=True,
            message="职位创建成功",
            data={"id": job_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_jobs():
    """职位列表"""
    try:
        jobs = await list_job_positions()
        return APIResponse(success=True, data=jobs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=APIResponse)
async def get_job(job_id: str):
    """获取职位详情"""
    job = await get_job_position(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    return APIResponse(success=True, data=job)


@router.put("/{job_id}", response_model=APIResponse)
async def update_job(job_id: str, data: JobPositionCreate):
    """更新职位"""
    ok = await update_job_position(job_id, data.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="职位不存在")
    return APIResponse(success=True, message="职位更新成功")


@router.delete("/{job_id}", response_model=APIResponse)
async def delete_job(job_id: str):
    """删除职位"""
    ok = await delete_job_position(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="职位不存在")
    return APIResponse(success=True, message="职位已删除")
