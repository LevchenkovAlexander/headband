import uuid
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import miniapp_db_fcn, get_db_session
from backend.database.responses import StatusResponse
from fastapi.responses import FileResponse



#Request


class ViewRequest(BaseModel):
    master_id: uuid.UUID
    guide_id: uuid.UUID


#Responses
class GuideBaseResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    video: bool
    liked: bool
    likes: int
    views: int


class GuidePageResponse(StatusResponse):
    guides_fit: List[GuideBaseResponse]
    guides_all: List[GuideBaseResponse]


class StepInfoResponse(StatusResponse):
    step_types: List[bool]
    total: int


class StepResponse(StatusResponse):
    text: str
    title: str


"""API"""
router = APIRouter(
    prefix="/master/guides",
    tags=["Master.Guide"]
)


@router.get("/", response_model=GuidePageResponse)
async def get_guides(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение списка гайдов для мастера"""
    status, g_fitable, g_all = await miniapp_db_fcn.get_guides(
        master_id=master_id,
        session=session
    )
    return {
        "status": status,
        "guides_fit": g_fitable,
        "guides_all": g_all
    }

@router.get("/step_info", response_model=StepInfoResponse)
async def get_step_types(
        guide_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    status, step_text = await miniapp_db_fcn.get_steps(guide_id=guide_id, session=session)
    status, step_video = await miniapp_db_fcn.get_video_steps(guide_id=guide_id, session=session)
    total = len(step_video)+len(step_text)
    resp = [False]*total
    for step in step_video:
        resp[step["step_num"]-1] = True
    return {"status": "success",
            "step_types": resp,
            "total": total}

@router.get("/step_text", response_model=StepResponse)
async def get_step_text(
        step_num: int,
        guide_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    txt, title = await miniapp_db_fcn.get_text_from_step(step_num=step_num, guide_id=guide_id, session=session)
    return {"status": "success",
            "text": txt,
            "title": title}

@router.get("/step_content")
async def get_step_content(
        step_num: int,
        guide_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    filepath = await miniapp_db_fcn.get_content_from_step(step_num=step_num, guide_id=guide_id, session=session)
    return FileResponse(filepath)

@router.post("/view", response_model=StatusResponse)
async def create_view(
        request: ViewRequest,
        session: AsyncSession = Depends(get_db_session)
):
    await miniapp_db_fcn.add_view(master_id=request.master_id, guide_id=request.guide_id, session=session)
    return {"status": "success"}

@router.patch("/like", response_model=StatusResponse)
async def toggle_like(
        request: ViewRequest,
        session: AsyncSession = Depends(get_db_session)
):
    await miniapp_db_fcn.change_state(master_id=request.master_id, guide_id=request.guide_id, session=session)
    return {"status": "success"}