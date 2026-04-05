from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import CategoryModel


'''async def get_all_categories(session: AsyncSession):
    """Получение всех категорий"""
    categories = await CategoryModel.get_all(session=session)
    return [
        {
            "id": cat.id,
            "name": cat.name
        }
        for cat in categories
    ]'''


async def create_category(
        name: str,
        session: AsyncSession
):
    """Создание категории"""
    data = {"name": name}
    return await CategoryModel.create(session=session, data = data)