import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message


from headband.backend.telegram_bot import dp, handle_deeplink, bot, Form
from headband.backend.telegram_bot.bot_helpers import get_multi_select_keyboard, ServiceSelector

service_selector = ServiceSelector()

@dp.message_handler(Command('start'))
async def cmd_start(message: Message):
    logging.info(f"recieved start command from user")
    args = message.get_args()
    if args:
        answer = await handle_deeplink(message, args)
    else:
        logging.info(f"no deeplink")
        answer = "нужна ссылка с параметрами, попросите у своей организации"
    await message.answer(answer)


@dp.message_handler(Command('choose_category'))
async def cmd_choose_category(message: Message, state: FSMContext):
    await state.set_state(Form.choosing_categories)
    await state.update_data(selected_categories=[], selected_subcategories=[])

    await message.answer(
        "🎯 <b>Выберите категории услуг</b>",
        parse_mode="HTML",
        reply_markup=get_multi_select_keyboard(
            service_selector.categories,
            [],
            prefix="cat"
        )
    )


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)