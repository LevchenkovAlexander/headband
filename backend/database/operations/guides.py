import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import MasterCategoryModel, GuidesModel


async def get_guides(master_id: uuid.UUID, session: AsyncSession):
    """Получение гайдов по категориям мастера"""
    category_ids = await MasterCategoryModel.get_categories_by_master(id = master_id, session = session)

    g_fitable = await GuidesModel.get_by_categories(categories=category_ids, session=session)
    g_all = await GuidesModel.get_all(session=session)

    g_fit_resp = []
    g_all_resp = []

    for g in g_fitable:
        g_fit_resp.append({
            "id": str(g.id),
            "steps": g.steps,
            "author": str(g.author)
        })

    for g in g_all:
        g_all_resp.append({
            "id": str(g.id),
            "steps": g.steps,
            "author": str(g.author)
        })

    return "success", g_fit_resp, g_all_resp


async def get_steps(guide_id: uuid.UUID, session: AsyncSession):
    """Получение шагов гайда по ID"""
    return await GuidesModel.get_by_id(guide_id=guide_id, session=session)


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