import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import MasterCategoryModel, GuidesModel, GuideTextStepModel, GuideVideoStepModel, GuideStatModel


async def get_guides(master_id: uuid.UUID, session: AsyncSession):
    """Получение гайдов по категориям мастера"""
    category_ids = await MasterCategoryModel.get_categories_by_master(id=master_id, session=session)
    g_fitable = await GuidesModel.get_by_categories(categories=category_ids, session=session)
    g_all = await GuidesModel.get_all(session=session)

    g_fit_resp = []
    g_all_resp = []

    for g in g_fitable:
        g_fit_resp.append({
            "id": g.id,
            "name": g.name,
            "category": g.category,
            "video": bool(await GuideVideoStepModel.get_by_guide_id(guide_id=g.id, session=session)),
            "liked": await GuideStatModel.check_like(guide_id=g.id, master_id=master_id, session=session),
            "likes": (await GuideStatModel.get_guide_stats(guide_id=g.id, session=session))["likes"],
            "views": (await GuideStatModel.get_guide_stats(guide_id=g.id, session=session))["views"]
        })

    for g in g_all:
        g_all_resp.append({
            "id": g.id,
            "name": g.name,
            "category": g.category,
            "video": bool(await GuideVideoStepModel.get_by_guide_id(guide_id=g.id, session=session)),
            "liked": await GuideStatModel.check_like(guide_id=g.id, master_id=master_id, session=session),
            "likes": (await GuideStatModel.get_guide_stats(guide_id=g.id, session=session))["likes"],
            "views": (await GuideStatModel.get_guide_stats(guide_id=g.id, session=session))["views"]
        })

    return "success", g_fit_resp, g_all_resp


async def get_steps(guide_id: uuid.UUID, session: AsyncSession):
    """Получение шагов гайда по ID"""
    steps = await GuideTextStepModel.get_by_guide_id(guide_id=guide_id, session=session)
    steps_resp = [{
        "id": s.id,
        "guide_id": s.guide_id,
        "step_num": s.step_num,
        "title": s.title,
        "text": s.text
    } for s in steps]
    return "success", steps_resp

async def create_step(guide_id: uuid.UUID, step_data: dict, session: AsyncSession):
    """Создание шага гайда"""
    step_data["guide_id"] = guide_id
    step_id = await GuideTextStepModel.create(session=session, data=step_data)
    return {"status": "success", "id": step_id}

async def update_step(step_id: uuid.UUID, update_data: dict, session: AsyncSession):
    """Обновление шага гайда"""
    status = await GuideTextStepModel.update(session=session, step_id=step_id, update_data=update_data)
    return {"status": status}

async def delete_step(step_id: uuid.UUID, session: AsyncSession):
    """Удаление шага гайда"""
    status = await GuideTextStepModel.delete(session=session, step_id=step_id)
    return {"status": status}

async def update_guide(update_data, session: AsyncSession):
    """Обновление гайда мастера"""
    data_to_upd = update_data.model_dump(exclude_unset=True)
    return await GuidesModel.update(
        session=session,
        id=update_data.id,
        author=update_data.author,
        update_data=data_to_upd
    )

async def create_guide(request, session: AsyncSession):
    guide_id = await GuidesModel.create(
        session=session,
        data=request.model_dump()
    )
    return {"status": "success", "id": guide_id}


async def get_video_steps(guide_id: uuid.UUID, session: AsyncSession):
    """Получение видео-шагов гайда по ID"""
    steps = await GuideVideoStepModel.get_by_guide_id(guide_id=guide_id, session=session)
    steps_resp = [{
        "id": s.id,
        "guide_id": s.guide_id,
        "step_num": s.step_num,
        "video_name": s.video_name,
        "video_file_path": s.video_file_path,
        "description": s.description
    } for s in steps]
    return "success", steps_resp

async def create_video_step(guide_id: uuid.UUID, step_data: dict, session: AsyncSession):
    """Создание видео-шага гайда"""
    step_data["guide_id"] = guide_id
    step_id = await GuideVideoStepModel.create(session=session, data=step_data)
    return {"status": "success", "id": step_id}

async def update_video_step(step_id: uuid.UUID, update_data: dict, session: AsyncSession):
    """Обновление видео-шага гайда"""
    status = await GuideVideoStepModel.update(session=session, step_id=step_id, update_data=update_data)
    return {"status": status}

async def delete_video_step(step_id: uuid.UUID, session: AsyncSession):
    """Удаление видео-шага гайда"""
    status = await GuideVideoStepModel.delete(session=session, step_id=step_id)
    return {"status": status}

async def get_text_from_step(step_num: int, guide_id: uuid.UUID, session: AsyncSession):
    """Получение текста шага"""
    step = await GuideTextStepModel.get_by_num_id(step_num=step_num, guide_id=guide_id, session=session)
    if step:
        return step.text, ""
    else:
        video = await GuideVideoStepModel.get_by_num_id(step_num=step_num, guide_id=guide_id, session=session)
        return video.description, video.video_name

async def get_content_from_step(step_num: int, guide_id: uuid.UUID, session: AsyncSession):
    """Получение контента шага"""
    video = await GuideVideoStepModel.get_by_num_id(step_num=step_num, guide_id=guide_id, session=session)
    return video.video_file_path

async def add_view(master_id: uuid.UUID, guide_id: uuid.UUID, session: AsyncSession):
    """Добавление записи о просмотре"""
    id = await GuideStatModel.create(data={"master_id": master_id,
                                           "guide_id": guide_id}, session=session)
    return id

async def change_state(master_id: uuid.UUID, guide_id: uuid.UUID, session: AsyncSession):
    """Лайк/дизлайк"""
    id = await GuideStatModel.get_by_guide_master(guide_id=guide_id, master_id=master_id, session=session)
    res = await GuideStatModel.toggle_action(stat_id=id, session=session)
    return res

async def get_liked_guides(master_id: uuid.UUID, session: AsyncSession):
    """Получить отмеченные мастером"""
    return await GuideStatModel.get_by_master_liked(master_id=master_id, session=session)