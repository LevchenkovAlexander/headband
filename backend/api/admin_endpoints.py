import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from headband.backend import get_db_session
from headband.backend.api import app
from headband.backend.database import db_functions
from headband.backend.database.requests import OrganizationCreateRequest, OrganizationUpdateRequest, PriceCreateRequest, \
    AdminCreateRequest, AdminUpdateRequest, OfferCreateRequest, OfferUpdateRequest
from headband.backend.database.responses import OrganizationResponse, StatusResponse, IDResponse, AdminResponseInfo
from headband.backend.telegram_bot import BOT_URL


@app.post("/admins/create_organization", tags=["Admin"], response_model=OrganizationResponse)
async def create_organization(org_info: OrganizationCreateRequest,
                                   session: AsyncSession = Depends(get_db_session)):
    status, master, user, org_id = await db_functions.create_organization(org_request=org_info, session=session)
    tg_master_link = BOT_URL + master
    tg_user_link = BOT_URL + user
    return {"status": status,
            "tg_master": tg_master_link,
            "tg_user": tg_user_link,
            "id": org_id}

@app.patch("/admins/update_organization", tags=["Admin"], response_model=StatusResponse)
async def update_organization(update_data: OrganizationUpdateRequest,
                                   session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.update_organization(update_data=update_data, session=session)
    return {"status": status}

@app.delete("/admins/delete_organization", tags=["Admin"], response_model=StatusResponse)
async def delete_organization(id: uuid.UUID,
                                session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.delete_organization(delete_id=id, session=session)
    return {"status": status}

@app.post("/admins/create_price_position", tags=["Admin"], response_model=IDResponse)
async def create_price(price_position: PriceCreateRequest,
                                session: AsyncSession = Depends(get_db_session)):
    status, id = await db_functions.create_price_position(price_position=price_position, session=session)
    return {"status": status,
            "id": id}

@app.delete("/admins/delete_price_position", tags=["Admin"], response_model=StatusResponse)
async def delete_price(id: uuid.UUID,
                              session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.delete_price(delete_id=id, session=session)
    return {"status": status}

@app.post("/admins/create_admin/", tags=["Admin"], response_model=IDResponse)
async def create_admin(adm_request: AdminCreateRequest,
                              session: AsyncSession = Depends(get_db_session)):
    status, adm_id = await db_functions.create_admin(adm_request=adm_request, session=session)
    return {"status": status,
            "id": adm_id}

@app.patch("/admins/update_admin", tags=["Admin"], response_model=StatusResponse)
async def update_admin(update_data: AdminUpdateRequest,
                              session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.update_admin(update_data=update_data, session=session)
    return {"status": status}

@app.get("/admins/cabinet", tags=["Admin"], response_model=AdminResponseInfo)
async def get_admin_info(admin_id: uuid.UUID,
                              session: AsyncSession = Depends(get_db_session)):
    response = await db_functions.get_admin_info(id = admin_id, session=session)
    return response

@app.post("/admins/create_offer/", tags=["Admin"], response_model=IDResponse)
async def create_offer(off_request: OfferCreateRequest,
                              session: AsyncSession = Depends(get_db_session)):
    status, offer_id = await db_functions.create_offer(offer=off_request, session=session)
    return {"status": status,
            "id": offer_id}

@app.patch("/admins/update_offer", tags=["Admin"], response_model=StatusResponse)
async def update_offer(update_data: OfferUpdateRequest,
                              session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.update_offer(update_data=update_data, session=session)
    return {"status": status}

@app.delete("/admins/delete_offer", tags=["Admin"], response_model=StatusResponse)
async def delete_offer(id: uuid.UUID,
                              session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.delete_offer(delete_id=id, session=session)
    return {"status": status}