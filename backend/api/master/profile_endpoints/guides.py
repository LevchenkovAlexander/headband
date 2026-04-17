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
    views: int
    likes: int
    like: bool
    guide_type: int


class MyGuidesResponse(BaseGuideResponse):
    created: date
    changed: date
    approved: date


class GuidesPageResponse(StatusResponse):
    my_guides: List[MyGuidesResponse]
    liked_guides: List[BaseGuideResponse]
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
    liked_guides =  await miniapp_db_fcn.get_liked_guides(master_id=master_id, session=session)
    #TODO доделать вывод гайдов
    master_guides = await miniapp_db_fcn
    if master.ambassador:
