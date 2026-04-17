import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session, miniapp_db_fcn
from backend.database.responses import StatusResponse


#Requests
class MasterUpdateRequest(BaseModel):
    id: uuid.UUID
    full_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


#Response
class ProfileResponse(StatusResponse):
    full_name: str
    tg: str
    phone: str
    description: str
    tg_users: str
    tg_master: str
    ref_clients: int
    ref_clients_active: int
    ref_masters_active: int


router = APIRouter(
    prefix="/master/profile/personal",
    tags=["Master.Profile"]
)



@router.get("/", response_model=ProfileResponse)
async def get_personal(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение био страницы"""
    master = await miniapp_db_fcn.get_master(master_id=master_id, session=session)
    master_link, user_link = await miniapp_db_fcn.get_master_referral_links(master_id=master_id, session=session)
    stats = await miniapp_db_fcn.get_referral_stats(master_id=master_id, session=session)
    resp = {"status": "success",
            "full_name":  master.full_name,
            "tg": master.username_tg,
            "phone": master.phone,
            "description": master.description,
            "tg_users": user_link,
            "tg_master": master_link,
            "ref_clients": stats["invited_users"],
            "ref_clients_active": stats["invited_active_users"],
            "ref_masters_active": stats["invited_masters"]}
    return resp


@router.patch("/update", response_model=StatusResponse)
async def update_master_profile(
    update_data: MasterUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление профиля мастера"""
    status = await miniapp_db_fcn.update_master(
        update_data=update_data,
        session=session
    )
    return {"status": status}