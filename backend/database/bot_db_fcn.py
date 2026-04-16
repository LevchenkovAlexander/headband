from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import MasterModel, UserModel
from backend.database.operations import *


async def check_account_type_tg(
        chat_id: int,
        session: AsyncSession
):
    """Проверка наличия аккаунтов мастера и пользователя"""
    master = await MasterModel.get_by_chat_id(session=session, chat_id=chat_id)
    user = await UserModel.get_by_chat_id(session=session, chat_id=chat_id)

    master_id = master.id if master else None
    user_id = user.id if user else None

    return master_id, user_id
