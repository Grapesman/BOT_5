import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path

import aiohttp
import asyncio
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet

import settings
from logger import logger
from notifications import notify_admins
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
    async def download_excel_from_yandex(cls, path: Path):
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
                    file_response.raise_for_status()
                    content = await file_response.read()

            with open(path, 'wb') as f:
                f.write(content)

    @classmethod
    async def upload_excel_to_yandex(cls, path: Path) -> UploadStatus:
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
                with open(path, 'rb') as file:
                    content = file.read()
                form = aiohttp.FormData()
                form.add_field('file', content, filename=path.name)

                async with session.put(upload_url, data=form, proxy=cls.proxy) as response:
                    if response.status == 201:
                        return UploadStatus.SUCCESS
                    text = await response.text()
                    logger.error(f'Не удалось загрузить файл: {text}')
                    return UploadStatus.LOCKED if is_resource_locked(response.status, text) else UploadStatus.ERROR


class ExcelManager:
    excel_locker = asyncio.Lock()

    @classmethod
    async def get_excel_book(cls, path: Path) -> Workbook:
        async with cls.excel_locker:
            book = load_workbook(path)
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

            book.save(settings.WRITE_TABLE_PATH)

    @staticmethod
    def _next_article_id(sheet: Worksheet) -> int:
        ids = [int(cell.value) for cell in sheet['A'][1:] if str(cell.value).strip().isdigit()]
        return max(ids, default=0) + 1


class DataManager:
    data_locker = asyncio.Lock()

    @classmethod
    async def update_read_table(cls):
        """Скачивает таблицу с Яндекс-диска и перезаписывает ею таблицу для чтения"""
        try:
            await YandexManager.download_excel_from_yandex(settings.READ_TABLE_PATH)
        except Exception as e:
            logger.error(f"Не удалось обновить таблицу для чтения: {e!r}")
            await notify_admins(message=f"Не удалось обновить таблицу для чтения: {e!r}")
            raise
        logger.info(f"Таблица для чтения обновлена")

    @classmethod
    async def refresh_read_table(cls):
        """Обновление по расписанию: при ошибке итерация пропускается, об ошибке уже сообщено в лог и админам"""
        try:
            await cls.update_read_table()
        except Exception:
            pass

    @classmethod
    async def get_excel_from_yandex(cls) -> Workbook:
        logger.info(f"Начинается выполнение запроса данных Excel-таблицы")
        book = await ExcelManager.get_excel_book(settings.READ_TABLE_PATH)

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
            await YandexManager.download_excel_from_yandex(settings.WRITE_TABLE_PATH)
            book = await ExcelManager.get_excel_book(settings.WRITE_TABLE_PATH)
            await ExcelManager.add_new_article_in_excel(book, title, date, thesis, authors, keywords)
            upload_status = await YandexManager.upload_excel_to_yandex(settings.WRITE_TABLE_PATH)
            os.remove(settings.WRITE_TABLE_PATH)
        if upload_status == UploadStatus.SUCCESS:
            logger.info(f"Статья успешно добавлена в Excel-таблицу")
        return upload_status
