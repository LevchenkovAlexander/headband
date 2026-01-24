import logging
import asyncio
import os
from typing import Dict, Any
from datetime import date
import uvicorn

import database as db
from aiogram import Bot, Dispatcher
from aiogram.types import Message

#from aiogram.filters import Command
#from aiogram.utils.keyboard import ReplyKeyboardBuilder

from fastapi import FastAPI

from headband.database import db_functions
from headband.database.db_validator import MasterUpdate, AppointmentTO
from headband.database.responses import PossibleTimesResponse, StatusResponse, \
    AppointmentListResponse, WeekTimetableResponse

#BOT_TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

app = FastAPI()



#bot = Bot(token=BOT_TOKEN)
#dp = Dispatcher()

#@dp.message(Command("start"))
#async def handle_start(message: Message):
    #logging.info(f"recieved start command from user")
    #await message.answer("here's gonna be a welcome message")


logging.basicConfig(level=logging.INFO)

@app.post("/appointments/", tags=["User"], response_model=StatusResponse)
async def create_appointment(appointment: AppointmentTO):
    status = await db_functions.create_appointment(appointment)
    return {"status": status}


@app.get("/possible-times/", tags=["User"], response_model=PossibleTimesResponse)
async def get_possible_start_times(
    master_id: int,
    date: date,
    service_id: int):

    poss_start, status = await db_functions.get_possible_start_time(
        master_id=master_id,
        date=date,
        service_id=service_id)
    return {
        "status": status,
        "times": poss_start or []
    }


@app.delete("/appointments/{appointment_id}", tags=["User"], response_model=StatusResponse)
async def cancel_appointment(
    appointment_id: int ):
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
async def get_appointments_by_date(
    master_id: int,
    date: date):
    appointments, count, status = await db_functions.get_appointments_by_date(master_id, date)

    return {
        "status": status,
        "count": count,
        "appointments": [a.to_dict() for a in appointments] if appointments else []
    }


@app.get("/masters/{master_id}/week/", tags=["Master"], response_model=WeekTimetableResponse)
async def get_week_timetable(
    master_id: int ,
    start_date: date):
    week_appointments, status = await db_functions.get_week_timetable(master_id, start_date)
    return {
        "status": status,
        "week_appointments": week_appointments
    }


@app.patch("/masters/{master_id}/profile", tags=["Master"], response_model=Dict[str, Any])
async def update_master_profile(
    master_id: int,
    update_data: MasterUpdate):
    updated_master, status = await db_functions.update_master(
        master_id=master_id,
        update_data=update_data
    )

    return {
        "status": status,
        "master": updated_master.to_dict() if updated_master else None
    }


async def main():
    try:
        if await db.setup_database():
            logging.info("База данных инициализирована")
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


