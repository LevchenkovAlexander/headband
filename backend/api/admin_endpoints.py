import uuid

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import miniapp_db_fcn, get_db_session
from backend.database.requests import OrganizationCreateRequest, OrganizationUpdateRequest, PriceCreateRequest, \
    AdminCreateRequest, AdminUpdateRequest, OfferCreateRequest, OfferUpdateRequest, PriceUpdateRequest, \
    AdminAuthRequest, CategoryCreateRequest
from backend.database.responses import OrganizationResponse, StatusResponse, IDResponse, AdminResponseInfo
from backend.telegram_bot import BOT_URL

router = APIRouter(
    prefix="/admins",
    tags=["Admin"]
)

@router.post("/create_caytegory", response_model=StatusResponse)
async def create_category(
        request: CategoryCreateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Создание категории"""
    status = await db_functions.create_category(name=request.name, session=session)
    return {"status": status}

