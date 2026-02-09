from multiprocessing import Process

from dotenv import load_dotenv


load_dotenv()
from headband.backend.api import admin_endpoints, master_endpoints, user_endpoints

from headband.backend import run_bot_process, run_server_process, app
app.include_router(user_endpoints.router)
app.include_router(master_endpoints.router)
app.include_router(admin_endpoints.router)

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

