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
from headband.database.data_transfer_objects import AppointmentTO

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

@app.post("/create_appointment/{appoin}", tags=["Users"])
async def create_appointment(appoin: AppointmentTO):
    status = db_functions.create_appointment(appoin)
    return {"status": status}

@app.get("/check_appointments/{appoin}", tags=["Users"])
async def get_list_of_possible_appointments(appoin: AppointmentTO):
    master_id = appoin.master_id
    date = appoin.date
    service_id = appoin.service_id
    poss_start, status = db_functions.get_possible_start_time(master_id=master_id, app_date=date, service_id=service_id)
    if poss_start:
        return {"status": status, "times": poss_start}
    else:
        return {"status": status}

@app.delete("/cancel_appointment/{appointment_id}", tags=["Users"])
async def cancel_appointment(id: int):
    status = db_functions.cancel_appointment(appointment_id=id)
    return {"status": status}

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



