import cv2
import pytesseract
import re
import sqlite3
import streamlit as st
import ollama

async def get_price_list(filepath: str):
    text = pytesseract.image_to_string(filepath, lang='rus')

    with open('categories.txt', 'r', encoding='utf-8') as f:
        categories_list = f.read()

    prompt = f"""
    Ты помощник, который извлекает данные из прайс-листов.
    Из текста ниже нужно получить JSON-массив объектов с ключами "name" (название услуги), "price" (цена в рублях, число), "quantity" (количество, целое число).
    Также твоя задача оценить время выполнения каждой услуги в минутах(int) и записать ее "approximate_time" и подобрать теги из списка: {categories_list}
    Игнорируй строки, которые не содержат товар (например, "Наименование", "Итого").
    Текст:
    {text}

    Ответ должен быть только JSON, без пояснений.
    """

models_obj = ollama.list()
models = [x.model for x in models_obj.models]



