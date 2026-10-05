from typing import List

from aiogram.types import Message

from loader import bot


MAX_MESSAGE_LENGTH = 4096
SEPARATORS = "\n "


class MessageSplitter:
    """Делит текст одного сообщения на несколько сообщений, не превышающих допустимую длину"""

    def __init__(self, max_length: int = MAX_MESSAGE_LENGTH):
        self.max_length = max_length

    def split(self, text: str) -> List[str]:
        chunks = []
        while len(text) > self.max_length:
            cut = self._find_cut(text)
            chunks.append(text[:cut])
            text = text[cut + 1:] if text[cut] in SEPARATORS else text[cut:]
        chunks.append(text)
        return [chunk for chunk in chunks if chunk.strip()]

    def _find_cut(self, text: str) -> int:
        window = text[:self.max_length + 1]
        # Делим по строкам
        cut = window.rfind("\n")
        if cut <= 0:
            # Делим по словам
            cut = window.rfind(" ")
        if cut <= 0:
            # Делим по символам
            cut = self.max_length
        return cut


message_splitter = MessageSplitter()


async def send_message(chat_id, text: str, **kwargs) -> List[Message]:
    """Отправляет текст одним или несколькими сообщениями; клавиатура прикрепляется к последнему"""
    reply_markup = kwargs.pop("reply_markup", None)
    chunks = message_splitter.split(text)
    messages = []
    for number, chunk in enumerate(chunks, start=1):
        markup = reply_markup if number == len(chunks) else None
        messages.append(await bot.send_message(chat_id, chunk, reply_markup=markup, **kwargs))
    return messages
