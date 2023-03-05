"""
inline.py - Inline 命令处理
"""
from aiogram.types import (
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
)
from aiogram.utils import markdown as md
from aiogram import Bot
from hashlib import md5
import re

from base114514 import b114514decode, b114514encode
from binascii import Error as BinasciiError

from config import config


def excerpt_description(long_description: str) -> str:
    return long_description[:50] + ('...' if len(long_description) > 50 else '')


async def inline_handler(inline_query: InlineQuery, bot: Bot):
    input_text = inline_query.query.strip()
    result_id: str = md5(input_text.encode('utf-8')).hexdigest()
    results: list[InlineQueryResultArticle] = []
    # Base114514 解码
    if re.match('^[145\n]+$', input_text):
        try:
            decoded_text: str = b114514decode(input_text.replace('\n', '').encode('ascii')).decode('utf-8')
            input_content = InputTextMessageContent(
                'Base114514 解码结果: ' +
                md.code(decoded_text),
                parse_mode='MarkdownV2',

            )
        except BinasciiError:
            decoded_text = 'Base114514 解码失败: 输入不是 Base114514 编码'
            input_content = InputTextMessageContent(
                decoded_text
            )
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title='Base114514 解码',
                input_message_content=input_content,
                description=excerpt_description(decoded_text)
            )
        )

    # Base114514 编码
    base114514_encoded_text: str = b114514encode(input_text.encode('utf-8')).decode('ascii')
    results.append(
        InlineQueryResultArticle(
            id=result_id,
            title='Base114514 编码',
            input_message_content=InputTextMessageContent(
                md.code(base114514_encoded_text),
                parse_mode='MarkdownV2'
            ),
            description=excerpt_description(base114514_encoded_text)
        )
    )

    await bot.answer_inline_query(
        inline_query.id,
        results=results,
        cache_time=1 if config.bot.debug else 500,
    )
    return
