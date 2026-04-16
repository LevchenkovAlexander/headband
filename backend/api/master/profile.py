import uuid

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session, miniapp_db_fcn
from backend.database.responses import StatusResponse

"""Pydantic"""
#Responses
class BaseProfileResponse(StatusResponse):
    name: str
    tg: str
    phone: str


#API
router = APIRouter(
    prefix="/master/profile",
    tags=["Master.Profile"]
)

@router.get("/", response_model=BaseProfileResponse)
async def get_profile(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение первичной информации профиля"""
    master = await miniapp_db_fcn.get_master(master_id=master_id, session=session)
    return {"status": "success",
            "name":  master.full_name,
            "tg": master.username_tg,
            "phone": master.phone}


