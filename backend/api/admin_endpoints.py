import uuid

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import db_functions, get_db_session
from backend.database.requests import OrganizationCreateRequest, OrganizationUpdateRequest, PriceCreateRequest, \
    AdminCreateRequest, AdminUpdateRequest, OfferCreateRequest, OfferUpdateRequest, PriceUpdateRequest, AdminAuthRequest
from backend.database.responses import OrganizationResponse, StatusResponse, IDResponse, AdminResponseInfo
from backend.telegram_bot import BOT_URL

router = APIRouter(
    prefix="/admins",
    tags=["Admin"]
)

