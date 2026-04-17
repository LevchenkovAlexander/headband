import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session, miniapp_db_fcn
from backend.database.responses import StatusResponse



#Requests

#Responses
class BaseGuideResponse(BaseModel):
    name: str
    category: str
    guide_type: int

class StatGuideResponse(BaseGuideResponse):
    views: int
    likes: int
    like: bool

class MyGuidesResponse(StatGuideResponse):
    created: date
    changed: date
    approved: date


class GuidesPageResponse(StatusResponse):
    my_guides: List[MyGuidesResponse]
    liked_guides: List[StatGuideResponse]
    approve_guides: Optional[List[BaseGuideResponse]]


#API
router = APIRouter(
    prefix="/master/profile/guides",
    tags=["Master.Profile"])


@router.get("/", response_model=GuidesPageResponse)
async def get_guides_page(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    master = await miniapp_db_fcn.get_master(master_id=master_id, session=session)

    master_guides, liked_guides = miniapp_db_fcn.preuploaded_data(master_id=master_id, session=session)

    my_guides_resp = []
    for guide in master_guides:
        likes = sum(1 for stat in guide.guide_stats if stat.action == 1)
        views = sum(1 for stat in guide.guide_stats if stat.action == 0)

        liked_by_me = any(stat.master_id == master_id and stat.action == 1 for stat in guide.guide_stats)

        guide_type = 1 if guide.video_steps_list else 0

        my_guides_resp.append({
            "name": guide.name,
            "category": guide.category,
            "views": views,
            "likes": likes,
            "like": liked_by_me,
            "guide_type": guide_type,
            "created": guide.guide_created,
            "changed": guide.guide_last_change,
            "approved": guide.guide_approved,
        })


    liked_guides_resp = []
    for guide in liked_guides:
        likes = sum(1 for stat in guide.guide_stats if stat.action == 1)
        views = sum(1 for stat in guide.guide_stats if stat.action == 0)
        guide_type = 1 if guide.video_steps_list else 0

        liked_guides_resp.append({
            "name": guide.name,
            "category": guide.category,
            "views": views,
            "likes": likes,
            "like": True,   # мы загружали только лайкнутые
            "guide_type": guide_type,
            "created": guide.guide_created,
            "changed": guide.guide_last_change,
            "approved": guide.guide_approved,
        })

    # Если мастер амбассадор – добавляем гайды, ожидающие подтверждения
    if master.ambassador:
        pending_guides = await miniapp_db_fcn.pending_guides(session=session)
        amb_resp = []
        for guide in pending_guides:
            guide_type = 1 if guide.video_steps_list else 0
            amb_resp.append({
                "name": guide.name,
                "category": guide.category,
                "guide_type": guide_type,
            })
        return {
            "status": "success",
            "my_guides": my_guides_resp,
            "liked_guides": liked_guides_resp,
            "approve_guides": amb_resp,
        }

    return {
        "status": "success",
        "my_guides": my_guides_resp,
        "liked_guides": liked_guides_resp,
    }

