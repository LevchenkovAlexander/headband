import logging

from aiogram import types
from aiogram.dispatcher.filters import Command

from headband.backend.telegram_bot import dp, handle_deeplink, bot


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    logging.info(f"recieved start command from user")
    args = message.get_args()
    if args:
        answer = await handle_deeplink(message, args)
    else:
        logging.info(f"no deeplink")
        answer = "нужна ссылка с параметрами, попросите у своей организации"
    await message.answer(answer)

async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)