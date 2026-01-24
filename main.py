import datetime
import logging
import asyncio
import os

import uvicorn

import database as db
from aiogram import Bot, Dispatcher
from aiogram.types import Message

from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from fastapi import FastAPI

from headband.database import db_functions
from headband.database.data_transfer_objects import AppointmentTO, MasterTO

BOT_TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

app = FastAPI()



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def handle_start(message: Message):
    logging.info(f"recieved start command from user")
    await message.answer("here's gonna be a welcome message")


logging.basicConfig(level=logging.INFO)

@app.post("/create_appointment/{appointment}", tags=["User"])
async def create_appointment(appointment: AppointmentTO):
    status = db_functions.create_appointment(appointment)
    return {"status": status}

@app.get("/check_appointments/{appointment}", tags=["User"])
async def get_list_of_possible_appointments(appointment: AppointmentTO):
    poss_start, status = db_functions.get_possible_start_time(appointment)
    if poss_start:
        return {"status": status, "times": poss_start}
    else:
        return {"status": status}

@app.delete("/cancel_appointment/{appointment_id}", tags=["User"])
async def cancel_appointment(id: int):
    status = db_functions.cancel_appointment(id)
    return {"status": status}

@app.get("/todays_timetable/{master_id}", tags=["Master"])
async def get_today_appointments(id: int):
    date = datetime.date.today()
    appointments, num, status = db_functions.get_appointments_by_date(id, date)
    if num!=0:
        return appointments, status
    return status

@app.get("/date_timetable/{appointment}", tags=["Master"])
async def get_date_appointments(appointment: AppointmentTO):
    date = appointment.date
    master_id = appointment.master_id
    appointments, num, status = db_functions.get_appointments_by_date(master_id, date)
    if num!=0:
        return appointments, status
    return status

@app.get("/week_timetable/{appointment}", tags=["Master"])
async def get_week_appointments(appointment: AppointmentTO):
    date = appointment.date
    master_id = appointment.master_id
    return db_functions.get_week_timetable(master_id, date)

@app.patch("/update_profile_info/{master}", tags=["Master"])
async def update_profile_info(master: MasterTO):
    return db_functions.update_master(master)


async def main():
    try:
        if await db.setup_database():
            logging.info("БД инициализирована")
        uvicorn.run("main.app", reload=True)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        await db.close_connection()




if __name__ == "__main__":
    asyncio.run(main())



