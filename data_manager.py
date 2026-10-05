import os
from datetime import datetime

import asyncio
import requests
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet

import settings
from logger import logger
from validation import catalog_validator


class YandexManager:
    yandex_locker = asyncio.Lock()

    @classmethod
    async def download_excel_from_yandex(cls) -> bool:
        async with cls.yandex_locker:
            url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path={settings.YA_FILE_PATH}'
            headers = {'Authorization': f'OAuth {settings.YA_TOKEN}'}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                download_url = response.json().get('href')
                file_response = requests.get(download_url)
                with open(settings.FILE_SAVE_PATH, 'wb') as f:
                    f.write(file_response.content)

            else:
                raise Exception(f'Ошибка при получении файла: {response.text}')

    @classmethod
    async def upload_excel_to_yandex(cls) -> bool:
        async with cls.yandex_locker:
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {'Authorization': f'OAuth {settings.YA_TOKEN}'}
            params = {'path': settings.YA_FILE_PATH, 'overwrite': 'true'}

            # Запрос для получения ссылки для загрузки
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                logger.error(f'Не удалось получить ссылку для загрузки: {response.json()}')
                return False

            upload_url = response.json().get('href')

            # Загружаем файл
            with open(settings.FILE_SAVE_PATH, 'rb') as file:
                response = requests.put(upload_url, files={'file': file})
            if response.status_code == 201:
                return True
            else:
                logger.error(f'Не удалось загрузить файл: {response.json()}')
                return False


class ExcelManager:
    excel_locker = asyncio.Lock()

    @classmethod
    async def get_excel_book(cls) -> Workbook:
        async with cls.excel_locker:
            book = load_workbook(settings.FILE_SAVE_PATH)
            return book

    @classmethod
    async def add_new_article_in_excel(
            cls,
            book: Workbook,
            title: str,
            date: str,
            thesis: str,
            authors: str,
            keywords: str
    ):
        async with cls.excel_locker:
            sheet = book[catalog_validator.sheet_name]
            row = catalog_validator.last_data_row(sheet) + 1

            sheet[f'A{row}'].value = cls._next_article_id(sheet)
            sheet[f'B{row}'].value = title
            sheet[f'C{row}'].value = datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            sheet[f'D{row}'].value = date
            sheet[f'F{row}'].value = thesis
            sheet[f'H{row}'].value = authors
            sheet[f'J{row}'].value = keywords

            book.save(settings.FILE_SAVE_PATH)

    @staticmethod
    def _next_article_id(sheet: Worksheet) -> int:
        ids = [int(cell.value) for cell in sheet['A'][1:] if str(cell.value).strip().isdigit()]
        return max(ids, default=0) + 1


class DataManager:
    data_locker = asyncio.Lock()

    @classmethod
    async def get_excel_from_yandex(cls) -> Workbook:
        logger.info(f"Начинается выполнение запроса данных Excel-таблицы")
        async with cls.data_locker:
            await YandexManager.download_excel_from_yandex()
            book = await ExcelManager.get_excel_book()
            os.remove(settings.FILE_SAVE_PATH)
        
        # Валидация производит очистку строк,
        # Не соответствующих условиям валидации
        catalog_validator.validate(book)
        
        logger.info(f"Данные Excel-файла получены")
        return book

    @classmethod
    async def add_new_article_in_yandex(
            cls,
            title: str,
            date: str,
            thesis: str,
            authors: str,
            keywords: str
    ):
        logger.info(f"Начинается выполнение запроса добавления статье в Excel-таблицу")
        async with cls.data_locker:
            await YandexManager.download_excel_from_yandex()
            book = await ExcelManager.get_excel_book()
            await ExcelManager.add_new_article_in_excel(book, title, date, thesis, authors, keywords)
            uploaded: bool = await YandexManager.upload_excel_to_yandex()
            os.remove(settings.FILE_SAVE_PATH)
        logger.info(f"Статья успешно добавлена в Excel-таблицу")
        return uploaded
