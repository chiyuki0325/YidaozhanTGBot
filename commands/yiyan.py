"""
yiyan.py - 一眼丁真
"""

from aiogram import types
from aiogram.utils import markdown as md
import aiohttp
import logging
from io import BytesIO

from common import error_message
from config import config


async def handler(message: types.Message):
    logging.info('yiyan')
    msg = await message.reply('⏰ 正在获取图片 ...')
    async with aiohttp.request(
            method='GET',
            url=f'{config.modules.dingzhen.api}/randomdj',
            params={
                "r": "0", "g": "1"
            }
    ) as resp:
        if resp.status != 200:
            await message.reply('❌ 都什么年代，还在连传统网络？')
            return
        data = await resp.json()
        if config.bot.debug:
            logging.info(data)
        await msg.delete()
        await message.reply_photo(
            photo=data['url'],
        )
