import json
import os
from datetime import datetime
from enum import Enum

import aiohttp
import asyncio
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet

import settings
from logger import logger
from validation import catalog_validator


class UploadStatus(Enum):
    SUCCESS = "success"
    LOCKED = "locked"
    ERROR = "error"


def is_resource_locked(status: int, text: str) -> bool:
    if status == 423:
        return True
    try:
        return json.loads(text).get('error') == 'DiskResourceLockedError'
    except (ValueError, AttributeError):
        return False


class YandexManager:
    yandex_locker = asyncio.Lock()
    # Прокси используется только для запросов к Яндекс-диску
    proxy = settings.YA_REQUEST_PROXY

    @staticmethod
    def _session() -> aiohttp.ClientSession:
        # trust_env=True — как и requests, учитываем прокси из переменных окружения
        return aiohttp.ClientSession(trust_env=True)

    @classmethod
    async def download_excel_from_yandex(cls) -> bool:
        async with cls.yandex_locker:
            url = 'https://cloud-api.yandex.net/v1/disk/resources/download'
            headers = {'Authorization': f'OAuth {settings.YA_TOKEN}'}
            params = {'path': settings.YA_FILE_PATH}

            async with cls._session() as session:
                async with session.get(url, headers=headers, params=params, proxy=cls.proxy) as response:
                    if response.status != 200:
                        raise Exception(f'Ошибка при получении файла: {await response.text()}')
                    download_url = (await response.json(content_type=None)).get('href')

                async with session.get(download_url, proxy=cls.proxy) as file_response:
                    content = await file_response.read()

            with open(settings.FILE_SAVE_PATH, 'wb') as f:
                f.write(content)

    @classmethod
    async def upload_excel_to_yandex(cls) -> UploadStatus:
        async with cls.yandex_locker:
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {'Authorization': f'OAuth {settings.YA_TOKEN}'}
            params = {'path': settings.YA_FILE_PATH, 'overwrite': 'true'}

            async with cls._session() as session:
                # Запрос для получения ссылки для загрузки
                async with session.get(url, headers=headers, params=params, proxy=cls.proxy) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error(f'Не удалось получить ссылку для загрузки: {text}')
                        return UploadStatus.LOCKED if is_resource_locked(response.status, text) else UploadStatus.ERROR
                    upload_url = (await response.json(content_type=None)).get('href')

                # Загружаем файл
                with open(settings.FILE_SAVE_PATH, 'rb') as file:
                    content = file.read()
                form = aiohttp.FormData()
                form.add_field('file', content, filename=os.path.basename(settings.FILE_SAVE_PATH))

                async with session.put(upload_url, data=form, proxy=cls.proxy) as response:
                    if response.status == 201:
                        return UploadStatus.SUCCESS
                    text = await response.text()
                    logger.error(f'Не удалось загрузить файл: {text}')
                    return UploadStatus.LOCKED if is_resource_locked(response.status, text) else UploadStatus.ERROR


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
    ) -> UploadStatus:
        logger.info(f"Начинается выполнение запроса добавления статье в Excel-таблицу")
        async with cls.data_locker:
            await YandexManager.download_excel_from_yandex()
            book = await ExcelManager.get_excel_book()
            await ExcelManager.add_new_article_in_excel(book, title, date, thesis, authors, keywords)
            upload_status = await YandexManager.upload_excel_to_yandex()
            os.remove(settings.FILE_SAVE_PATH)
        if upload_status == UploadStatus.SUCCESS:
            logger.info(f"Статья успешно добавлена в Excel-таблицу")
        return upload_status
