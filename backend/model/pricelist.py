import json
import logging

import pytesseract
import re
import ollama

CATEGORIES_FILE = 'model\categories.txt'

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def load_categories():
    """Загружает список категорий из файла"""
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        return f.read()

async def get_price_list(filepath: str):
    text = pytesseract.image_to_string(filepath, lang='rus+eng')

    categories = load_categories()

    prompt = f"""
        Ты помощник, который извлекает данные из прайс-листов. Читай внимательно, внутри строки может быть несколько услуг(например для разной длины волос - разная цена)
        Из текста ниже нужно получить JSON-массив объектов.
        Структура объекта:
        - "name": название услуги (строка)
        - "price": цена в рублях (число, без знака валюты)
        - "approximate_time": время выполнения в минутах (целое число, оцени сам исходя из названия)
        - "category": одна из категорий: {categories}

        Правила:
        1. Игнорируй заголовки, итоги, пустые строки.
        2. Если цена не найдена, поставь 0.
        3. Ответ должен быть ТОЛЬКО валидным JSON массивом. Без маркдауна, без пояснений.

        Текст для анализа:
        {text}
        """

    models_obj = ollama.list()
    models = [x.model for x in models_obj.models]

    try:
        response = ollama.chat(model=models[0], messages=[
            {'role': 'user', 'content': prompt},
        ])
        content = response['message']['content']

        # Очистка от возможных маркдаун блоков ```json ... ```
        clean_json = re.sub(r'```json\s*|\s*```', '', content).strip()

        data = json.loads(clean_json)
        return data
    except Exception as e:
        logging.error(f"Ошибка при обработке LLM: {e}")
        return []






