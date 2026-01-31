import logging
import asyncio
from multiprocessing import Process
from typing import Dict, Any
from datetime import date

import uvicorn
import uuid
from fastapi import FastAPI

from headband.backend import database as db
from headband.backend.database import db_functions
from headband.backend.database.requests import MasterUpdateRequest, AppointmentCreateRequest, \
    AdminCreateRequest, OrganizationCreateRequest, OrganizationUpdateRequest
from headband.backend.database.responses import PossibleTimesResponse, StatusResponse, \
    AppointmentListResponse, WeekTimetableResponse, OrganizationResponse, IDResponse, \
    OrganizationUpdateResponse
from headband.backend.telegram_bot import BOT_URL, bot_main

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)

async def start_db():
    if await db.setup_database():
        logging.info("БД запущена")
        return True
    return False


"""@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_task
    bot_task = asyncio.create_task(start_bot())
    logging.info("Бот запущен")
    yield
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    logging.info("Бот остановлен")
"""
app = FastAPI()


"""rest запросы"""
@app.post("/appointments/", tags=["User"], response_model=StatusResponse)
async def create_appointment(appointment: AppointmentCreateRequest):
    status = await db_functions.create_appointment(appointment)
    return {"status": status}

@app.post("/admins/create_admin/", tags=["Admin"], response_model=IDResponse)
async def create_admin(adm_request: AdminCreateRequest):
    status, adm_id = await db_functions.create_admin(adm_request)
    return {"status": status,
            "id": adm_id}

@app.get("/possible-times/", tags=["User"], response_model=PossibleTimesResponse)
async def get_possible_start_times(master_id: int, date: date, service_id: int):
    poss_start, status = await db_functions.get_possible_start_time(
        master_id=master_id,
        date=date,
        service_id=service_id)
    return {
        "status": status,
        "times": poss_start or []
    }

@app.delete("/appointments/{appointment_id}", tags=["User"], response_model=StatusResponse)
async def cancel_appointment(appointment_id: int):
    status = await db_functions.cancel_appointment(appointment_id)
    return {"status": status}

@app.get("/masters/{master_id}/today/", tags=["Master"], response_model=AppointmentListResponse)
async def get_today_appointments(master_id: int):
    today = date.today()
    appointments, count, status = await db_functions.get_appointments_by_date(master_id, today)
    return {
        "status": status,
        "count": count,
        "appointments": [a.to_dict() for a in appointments] if appointments else []
    }

@app.get("/masters/{master_id}/date/{date_str}", tags=["Master"], response_model=AppointmentListResponse)
async def get_appointments_by_date(master_id: int, date: date):
    appointments, count, status = await db_functions.get_appointments_by_date(master_id, date)

    return {
        "status": status,
        "count": count,
        "appointments": [a.to_dict() for a in appointments] if appointments else []
    }

@app.get("/masters/{master_id}/week/{date_str}", tags=["Master"], response_model=WeekTimetableResponse)
async def get_week_timetable(master_id: int, start_date: date):
    week_appointments, status = await db_functions.get_week_timetable(master_id, start_date)
    return {
        "status": status,
        "week_appointments": week_appointments
    }

@app.patch("/masters/{master_id}/profile", tags=["Master"], response_model=Dict[str, Any])
async def update_master_profile(master_id: int, update_data: MasterUpdateRequest):
    updated_master, status = await db_functions.update_master(
        master_id=master_id,
        update_data=update_data
    )

    return {
        "status": status,
        "master": updated_master.to_dict() if updated_master else None
    }

@app.post("/admins/create_organization", tags=["Admin"], response_model=OrganizationResponse)
async def create_organization(org_info: OrganizationCreateRequest):
    status, master, user, org_id = await db_functions.create_organization(org_info)
    tg_master_link = BOT_URL+master
    tg_user_link = BOT_URL + user
    return {"status": status,
            "tg_master": tg_master_link,
            "tg_user": tg_user_link,
            "id": org_id}

@app.patch("/admins/update_organization", tags=["Admin"], response_model=OrganizationUpdateResponse)
async def update_organization(organization_id:  uuid.UUID, update_data: OrganizationUpdateRequest):
    status, updated_fields = db_functions.update_organization();

    return {
        "status": status,
        "updated_fields": updated_fields
    }
@app.post("/admins/create_price_position", tags=["Admin"], response_model=StatusResponse)
async def create_price_position(price_position: PriceCreateRequest):
    status = await db_functions.create_price_position(price_position=price_position)
    return {"status": status}

def run_bot_process():
    """Запуск бота в отдельном процессе"""
    asyncio.run(bot_main.start_bot())

def run_server_process():
    """Запуск сервера в отдельном процессе"""
    async def start_server():
        if await db.setup_database():
            logging.info("База данных инициализирована")
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    asyncio.run(start_server())

"""async def main():
    try:
        if await db.setup_database():
            logging.info("База данных инициализирована")
        #await start_bot()
        uvicorn.run("main:app",reload=True)
    except Exception as e:
        logging.error(f"Ошибка запуска: {e}")
    finally:
        await db.close_connection()"""

if __name__ == "__main__":
    bot_process = Process(target=run_bot_process)
    server_process = Process(target=run_server_process)

    bot_process.start()
    server_process.start()

    bot_process.join()
    server_process.join()

