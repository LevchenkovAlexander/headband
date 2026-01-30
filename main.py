import logging
import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import date

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from fastapi import FastAPI

import database as db
from headband.database import db_functions
from headband.database.requests import MasterUpdateRequest, AppointmentCreateRequest, MasterCreateRequest, \
    AdminCreateRequest, OrganizationCreateRequest
from headband.database.responses import PossibleTimesResponse, StatusResponse, \
    AppointmentListResponse, WeekTimetableResponse

BOT_TOKEN = "6676444574:AAEr9TBoYWGlAGnChuD3OP14k0_dX7qGdhs"
bot_task = None
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)

"""жизненный цикл приложения"""
async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
async def start_db():
    if await db.setup_database():
        logging.info("БД запущена")
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

"""команды бота"""
@dp.message_handler(commands=['start'])
async def handle_start(message: Message):
    logging.info(f"recieved start command from user")
    args = message.get_args()
    if args:
        answer = await handle_deeplink(message, args)
    else:
        logging.info(f"no deeplink")
        answer = "нужна ссылка с параметрами, попросите у своей организации"
    await message.answer(answer)

async def handle_deeplink(message: Message, args: str):
    user = message.from_user
    chat = message.chat
    logging.info(args)
    if int(args[-1]) == 1:
        status = await db_functions.create_master(user, chat, args)
        logging.info(f"{status} master with id {chat.id}")
        if status.__eq__("error"):
            return "Создать мастера не получилось"
        return "Мастер добавлен в организацию, добро пожаловать!"
    elif int(args[-1]) == 2:
        status = await db_functions.create_user(user, chat, args)
        logging.info(f"{status} user with id {chat.id}")
        return "Добро пожаловать, для ознакомления с ассортиментом зайдите в tg mini app"
    else:
        status, unique_code = await db_functions.create_organization(chat)
        logging.info(f"{status} organization with admin_id {chat.id}")
        if unique_code == 0:
            return "организация не создана"
        return f"Ваш master_tg_bot = t.me/perviyfogovskiybot?start={unique_code}{1} \n user_tg_bot = t.me/perviyfogovskiybot?start={unique_code}{2}"


"""rest запросы"""
@app.post("/appointments/", tags=["User"], response_model=StatusResponse)
async def create_appointment(appointment: AppointmentCreateRequest):
    status = await db_functions.create_appointment(appointment)
    return {"status": status}

@app.post("/admins/create_admin/", tags=["Admin"], response_model=StatusResponse)
async def create_admin(adm_request: AdminCreateRequest):
    status = await db_functions.create_admin(adm_request)
    return {"status": status}

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

@app.post("/admins/create_organization", tags=["Admin"], response_model=StatusResponse)
async def create_organization(org_info: OrganizationCreateRequest):
    status = await db_functions.create_organization(org_info)
    return {"status": status}

async def main():
    try:
        if await db.setup_database():
            logging.info("База данных инициализирована")
        #await start_bot()
        uvicorn.run(
            "main:app",
            reload=True
        )
    except Exception as e:
        logging.error(f"Ошибка запуска: {e}")
    finally:
        await db.close_connection()

if __name__ == "__main__":
   asyncio.run(main())

