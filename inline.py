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

    # 发病


def fabing(dickman) -> str:
    return f"{dickman}……🤤嘿嘿………🤤……好可爱……嘿嘿……{dickman}🤤……{dickman}……我的🤤……嘿嘿……🤤………亲爱的……赶紧让我抱一抱……啊啊啊{dickman}软软的脸蛋🤤还有软软的小手手……🤤…{dickman}……不会有人来伤害你的…🤤你就让我保护你吧嘿嘿嘿嘿嘿嘿嘿嘿🤤……太可爱了……🤤……美丽可爱的{dickman}……像珍珠一样……🤤嘿嘿……{dickman}……🤤嘿嘿……🤤……好想一口吞掉……🤤……但是舍不得啊……我的{dickman}🤤……嘿嘿……🤤我的宝贝……我最可爱的{dickman}……🤤没有{dickman}……我就要死掉了呢……🤤我的……🤤嘿嘿……可爱的{dickman}……嘿嘿🤤……可爱的{dickman}……嘿嘿🤤🤤……可爱的{dickman}……🤤……嘿嘿🤤……可爱的{dickman}…（吸）身上的味道……好好闻～🤤…嘿嘿🤤……摸摸～……可爱的{dickman}……再贴近我一点嘛……（蹭蹭）嘿嘿🤤……可爱的{dickman}……嘿嘿🤤……～亲一口～……可爱的{dickman}……嘿嘿🤤……抱抱你～可爱的{dickman}～（舔）喜欢～真的好喜欢～……（蹭蹭）脑袋要融化了呢～已经……除了{dickman}以外～什么都不会想了呢～🤤嘿嘿🤤……可爱的{dickman}……嘿嘿🤤……可爱的{dickman}……我的～……嘿嘿🤤……"


def america_stone(america) -> str:
    return f"{america}不肯承认自己错误的做法，反而使用控制舆论等方式试图掩盖自己的行为。{america}这种卑劣行径，恰恰暴露了{america}做贼心虚的心理。{america}这种认不清自己情况，糊弄民众，透支未来的行为，到最后一定是搬起石头砸自己的脚！{america}的这种错误行为，只会在错误的道路上越走越远！"


async def inline_handler(inline_query: InlineQuery, bot: Bot):
    input_text = inline_query.query.strip()
    results: list[InlineQueryResultArticle] = []
    if input_text:
        # Base114514 解码
        if re.match('^[145\n]+$', input_text):
            base114514_decode_result_id: str = md5((input_text + 'base114514decode').encode('utf-8')).hexdigest()
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
                    id=base114514_decode_result_id,
                    title='Base114514 解码',
                    input_message_content=input_content,
                    description=excerpt_description(decoded_text)
                )
            )

        # Base114514 编码
        base114514_encode_result_id: str = md5((input_text + 'base114514encode').encode('utf-8')).hexdigest()
        base114514_encoded_text: str = b114514encode(input_text.encode('utf-8')).decode('ascii')
        results.append(
            InlineQueryResultArticle(
                id=base114514_encode_result_id,
                title='Base114514 编码',
                input_message_content=InputTextMessageContent(
                    md.code(base114514_encoded_text),
                    parse_mode='MarkdownV2'
                ),
                description='来自下北泽的恶臭编码'
            )
        )

        # 发病
        fabing_result_id: str = md5((input_text + 'fabing').encode('utf-8')).hexdigest()
        results.append(
            InlineQueryResultArticle(
                id=fabing_result_id,
                title='发病',
                input_message_content=InputTextMessageContent(
                    fabing(input_text)
                ),
                description=f'{input_text}……🤤嘿嘿………🤤……好可爱……嘿嘿……'
            )
        )

        # 搬石砸脚
        america_stone_result_id: str = md5((input_text + 'america_stone').encode('utf-8')).hexdigest()
        results.append(
            InlineQueryResultArticle(
                id=america_stone_result_id,
                title='搬石砸脚',
                input_message_content=InputTextMessageContent(
                    america_stone(input_text)
                ),
                description=f'{input_text}这是搬起石头砸自己的脚！'
            )
        )
    else:
        results.append(
            InlineQueryResultArticle(
                id=md5('yidaozhan_meow'.encode('utf-8')).hexdigest(),
                title='喵呜 ...?',
                input_message_content=InputTextMessageContent('喵呜 ...?'),
                description='请输入文本！'
            )
        )

    await bot.answer_inline_query(
        inline_query.id,
        results=results,
        cache_time=1 if config.bot.debug else 1800,
    )
    return
