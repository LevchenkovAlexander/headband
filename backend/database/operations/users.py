
#TODO юзер
'''async def create_user(
        user: User,
        chat: Chat,
        session: AsyncSession
) -> str:
    """Создание пользователя"""
    user_data = UserCreateRequest(
        chat_id=chat.id,
        username=user.username
    )

    created = await UserModel.create(session=session, data=user_data.model_dump())
    if created:
        return "success"
    return "unable to create"'''


"""async def create_user_from_deeplink(
        chat_id: int,
        username: str,
        referrer_master_id: Optional[uuid.UUID],
        session: AsyncSession
):
    try:
        user_data = UserCreateRequest(
            chat_id=chat_id,
            username=username
        )
        user_id = await UserModel.create(session=session, data=user_data.model_dump())

        # Для пользователей реферал засчитывается сразу (если нужно)
        if referrer_master_id:
            referrer = await MasterModel.get_by_id(session=session, master_id=referrer_master_id)
            if referrer:
                await MasterReferralModel.increment_users(
                    session=session,
                    master_id=referrer_master_id
                )

        return "success", user_id
    except Exception as e:
        logging.error(f"Ошибка создания пользователя: {e}")
        return f"error: {str(e)}", uuid.UUID(int=0)"""