import os
import uuid
from datetime import date, datetime
from typing import List

import aiofiles
from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import db_functions, get_db_session
from backend.database.requests import MasterUpdateRequest, AddressCreateRequest, AddressUpdateRequest, WeekTemplate, \
    TemplateCreateRequest, TemplateUpdateRequest, WorkingDayUpdateRequest, AbsenceCreateRequest, AbsenceUpdateRequest, \
    GuideCreateRequest, GuideUpdateRequest, EarningDateRangeRequest, EarningCreateRequest, EarningUpdateRequest, \
    PrepayCreateRequest, PrepayUpdateRequest, PriceCreateRequest, PriceUpdateRequest, MasterNotificationUpdateRequest
from backend.database.responses import AppointmentResponse, AppointmentListResponse, StatusResponse, \
    WeekTimetableResponse, GuidePageResponse, IDResponse, AddressListResponse, WeekTemplateResponse, \
    AbsenceCreateResponse, AbsenceListResponse, PriceListResponseFile, EarningListResponse, PrepayListResponse, \
    PriceListResponse
from backend.model import pricelist

UPLOAD_DIR = "temps"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/masters",
    tags=["Master"]
)


@router.get("/appointments/week/", response_model=WeekTimetableResponse)
async def get_week_timetable(
        master_id: uuid.UUID,
        start_date: datetime,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение расписания мастера на неделю"""
    week_appointments, status = await db_functions.get_week_timetable(
        master_id=master_id,
        start_date=start_date,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {
        "status": status,
        "week_appointments": week_appointments
    }



@router.get("/appointments/", response_model=AppointmentListResponse)
async def get_appointments_by_date(
        master_id: uuid.UUID,
        date: date,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение записей мастера на дату"""
    appointments, count, status, addresses, names = await db_functions.get_appointments_by_date(
        master_id=master_id,
        app_date=date,
        session=session
    )

    a = []
    for i, appointment in enumerate(appointments):
        aresponse = AppointmentResponse.model_validate(appointment).model_dump()
        aresponse["address"] = addresses[i] if i < len(addresses) else None
        aresponse["service_name"] = names[i] if i < len(names) else None
        a.append(aresponse)

    return {
        "status": status,
        "count": count,
        "appointments": a
    }

@router.patch("/profile", response_model=StatusResponse)
async def update_master_profile(
    update_data: MasterUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление профиля мастера"""
    status = await db_functions.update_master(
        update_data=update_data,
        session=session
    )
    return {"status": status}

@router.get("/guides", response_model=GuidePageResponse)
async def get_guides(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение списка гайдов для мастера"""
    status, g_fitable, g_all = await db_functions.get_guides(
        master_id=master_id,
        session=session
    )
    return {
        "status": status,
        "guides_fit": g_fitable,
        "guides_all": g_all
    }

@router.get("/guides/{guide_id}", response_model=dict)
async def get_steps(
    guide_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение шагов конкретного гайда"""
    status, steps = await db_functions.get_steps(
        guide_id=guide_id,
        session=session
    )
    return {
        "status": status,
        "steps": steps
    }

@router.post("/guides", response_model=IDResponse)
async def create_guide(
    request: GuideCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        guide_id = await db_functions.create_guide(
            session=session,
            request=request
        )
        return {"status": "success", "id": guide_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/guides", response_model=StatusResponse)
async def update_guide(
    request: GuideUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    status = db_functions.update_guide(session=session,
        update_data=request)
    if status != "success":
        raise HTTPException(status_code=404, detail=status)
    return {"status": status}


@router.get("/categories", response_model=dict)
async def get_master_categories(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение категорий мастера"""
    categories = await db_functions.get_master_categories(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "categories": [{"id": str(cat.id), "name": cat.name} for cat in categories]
    }


@router.get("/prices", response_model=dict)
async def get_master_prices(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение прайс-листа мастера"""
    prices = await db_functions.get_prices_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "prices": prices
    }

@router.get("/addresses", response_model=AddressListResponse)
async def get_master_addresses(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех адресов мастера"""
    addresses = await db_functions.get_addresses_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "addresses": addresses
    }


@router.post("/addresses", response_model=IDResponse)
async def create_address(
    request: AddressCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Создание нового адреса"""
    address_id = await db_functions.create_address(
        master_id=request.master_id,
        address=request.address,
        session=session
    )
    return {
        "status": "success",
        "id": address_id
    }


@router.delete("/addresses/{address_id}", response_model=StatusResponse)
async def delete_address(
    address_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление адреса"""
    status = await db_functions.delete_address(
        address_id=address_id,
        session=session
    )
    return {"status": status}


@router.patch("/addresses/update", response_model=StatusResponse)
async def update_address(
    request: AddressUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление адреса"""
    status = await db_functions.update_address(
        address_id=request.id,
        address=request.address,
        session=session
    )
    return {"status": status}

@router.post("/week_template", response_model=StatusResponse)
async def set_template(
        request: TemplateCreateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Создание шаблона недели"""
    status = await db_functions.set_week_template_full(
        master_id=request.master_id,
        templates=request.days,
        session=session
    )
    return {"status": status}

@router.get("/week-template", response_model=WeekTemplateResponse)
async def get_week_template(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение текущего шаблона недели"""
    templates = await db_functions.get_week_template_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "templates": templates
    }

@router.patch("/week_template", response_model=StatusResponse)
async def update_week_template(
    request: TemplateUpdateRequest,
    session: AsyncSession = Depends(get_db_session)):
    """Обновление конкретного дня в шаблоне"""
    status = await db_functions.update_week_template(req=request, session=session)
    return {"status": status}

@router.delete("/week_template", response_model=StatusResponse)
async def delete_day_week_template(
    master_id: uuid.UUID,
    weekday: int,
    session: AsyncSession = Depends(get_db_session)):
    """Удаление дня (добавление выходного)"""
    status = await db_functions.delete_day(id=master_id, weekday=weekday, session=session)
    return {"status": status}

@router.patch("/working_day/update", response_model=StatusResponse)
async def update_working_day(
        request: WorkingDayUpdateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Обновление конкретной даты"""
    status = await db_functions.update_working_day(request=request, session=session)
    return {"status": status}

@router.post("/upload_price_file/{master_id}")
async def upload_file(master_id: uuid.UUID,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_db_session)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="Invalid file type")

    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"image_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # читаем по 1 МБ
            await f.write(chunk)

    data = await pricelist.get_price_list(file_path)
    res = await db_functions.create_pricelist(data=data, master_id=master_id, session=session)
    return {"status": "success",
            "prices": res}

@router.post("/prices", response_model=IDResponse)
async def create_price(
    request: PriceCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Создание позиции прайса"""
    status, price_id = await db_functions.create_price(
        master_id=request.master_id,
        category_id=request.category_id,
        name=request.name,
        price=request.price,
        approximate_time=request.approximate_time,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=400, detail=status)
    return {"status": status, "id": price_id}

@router.post("/prices/bulk", response_model=dict)
async def create_prices_bulk(
    request: PriceBulkCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Массовое создание позиций прайса"""
    prices_data = [p.model_dump() for p in request.prices]
    status, created_ids, errors = await db_functions.create_prices_bulk(
        master_id=request.master_id,
        prices_data=prices_data,
        session=session
    )
    if status != "success" and status != "success with errors":
        raise HTTPException(status_code=400, detail=status)
    return {
        "status": status,
        "created_ids": [str(id) for id in created_ids],
        "errors": errors
    }

@router.patch("/prices", response_model=StatusResponse)
async def update_price(
    request: PriceUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление позиции прайса"""
    status = await db_functions.update_price(
        update_data=request,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=400, detail=status)
    return {"status": status}

@router.delete("/prices/{price_id}", response_model=StatusResponse)
async def delete_price(
    price_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление позиции прайса"""
    status = await db_functions.delete_price(
        price_id=price_id,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=404, detail=status)
    return {"status": status}

@router.get("/prices", response_model=PriceListResponse)
async def get_master_prices(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех позиций прайса мастера"""
    prices = await db_functions.get_prices_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "prices": prices,
    }

@router.get("/prices/category", response_model=PriceListResponse)
async def get_prices_by_category(
    master_id: uuid.UUID,
    category_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение позиций прайса по категории"""
    status, prices = await db_functions.get_prices_by_category(
        master_id=master_id,
        category_id=category_id,
        session=session
    )
    return {
        "status": status,
        "prices": prices
    }


@router.post("/absences", response_model=AbsenceCreateResponse)
async def create_absence(
        request: AbsenceCreateRequest,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Добавить период отсутствия мастера.
    Все записи в этот период будут автоматически отменены.
    """
    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    if request.start_date < date.today():
        raise HTTPException(status_code=400, detail="start_date cannot be in the past")

    status, absence_id, cancelled = await db_functions.create_absence(
        master_id=request.master_id,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=400, detail=status)

    return {
        "status": status,
        "absence_id": absence_id,
        "cancelled_appointments": cancelled
    }


@router.get("/absences", response_model=AbsenceListResponse)
async def get_absences(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получить список периодов отсутствия мастера"""
    absences, status = await db_functions.get_absences_by_master(
        master_id=master_id,
        session=session
    )

    return {
        "status": status,
        "absences": absences
    }


@router.delete("/absences/{absence_id}", response_model=StatusResponse)
async def delete_absence(
        absence_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Удалить период отсутствия.
    Записи, которые были отменены, НЕ восстанавливаются.
    """
    status = await db_functions.delete_absence(
        absence_id=absence_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}

@router.patch("/absence", response_model=StatusResponse)
async def update_absence(absence: AbsenceUpdateRequest,
                        session: AsyncSession = Depends(get_db_session)
):
    """
    Изменить период отсутствия.
    Записи, которые были отменены, НЕ восстанавливаются.
    """
    status = await db_functions.update_absence(
        update_data=absence,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}


@router.get("/earnings", response_model=EarningListResponse)
async def get_master_earnings(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех доходов мастера"""
    status, earnings, total = await db_functions.get_earnings_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": status,
        "earnings": earnings,
        "total": total
    }

@router.get("/earnings/range", response_model=EarningListResponse)
async def get_earnings_by_range(
    request: EarningDateRangeRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение доходов за период"""
    status, earnings, total = await db_functions.get_earnings_by_date_range(
        master_id=request.master_id,
        start_date=request.start_date,
        end_date=request.end_date,
        session=session
    )
    return {
        "status": status,
        "earnings": earnings,
        "total": total
    }

@router.post("/earnings", response_model=IDResponse)
async def create_earning(
    request: EarningCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Создание записи о доходе"""
    status, earning_id = await db_functions.create_earning(
        master_id=request.master_id,
        price=request.price,
        date=request.date,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=400, detail=status)
    return {"status": status, "id": earning_id}


@router.patch("/earnings", response_model=StatusResponse)
async def update_earning(
    request: EarningUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление записи о доходе"""
    update_data = request.model_dump(exclude_unset=True)
    status = await db_functions.update_earning(
        earning_id=request.id,
        update_data=update_data,
        session=session
    )
    return {"status": status}

@router.delete("/earnings/{earning_id}", response_model=StatusResponse)
async def delete_earning(
    earning_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление записи о доходе"""
    status = await db_functions.delete_earning(
        earning_id=earning_id,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=404, detail=status)
    return {"status": status}

@router.get("/prepayments", response_model=PrepayListResponse)
async def get_master_prepayments(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех периодов предоплаты мастера"""
    status, prepayments = await db_functions.get_prepayments_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": status,
        "prepayments": prepayments
    }

@router.post("/prepayments", response_model=IDResponse)
async def create_prepayment(
    request: PrepayCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Создание периода предоплаты"""
    status, prepay_id = await db_functions.create_prepayment(
        master_id=request.master_id,
        percent=request.percent,
        start_date=request.start_date,
        end_date=request.end_date,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=400, detail=status)
    return {"status": status, "id": prepay_id}

@router.patch("/prepayments", response_model=StatusResponse)
async def update_prepayment(
    request: PrepayUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление периода предоплаты"""
    update_data = request.model_dump(exclude_unset=True)
    status = await db_functions.update_prepayment(
        prepay_id=request.id,
        update_data=update_data,
        session=session
    )
    return {"status": status}

@router.delete("/prepayments/{prepay_id}", response_model=StatusResponse)
async def delete_prepayment(
    prepay_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление периода предоплаты"""
    status = await db_functions.delete_prepayment(
        prepay_id=prepay_id,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=404, detail=status)
    return {"status": status}


@router.get("/notifications", response_model=MasterNotificationGetResponse)
async def get_master_notifications(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение настроек уведомлений мастера"""
    status, notification = await db_functions.get_master_notification(
        master_id=master_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {
        "status": status,
        "notification": notification
    }


@router.patch("/notifications", response_model=StatusResponse)
async def update_master_notification(
        request: MasterNotificationUpdateRequest,
        session: AsyncSession = Depends(get_db_session)
):
    """Обновление настроек уведомлений мастера (можно обновлять отдельные поля)"""
    update_data = request.model_dump(exclude_unset=True)
    update_data.pop("master_id", None)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    status = await db_functions.update_master_notification(
        master_id=request.master_id,
        update_data=update_data,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}
