"""
smm2_level.py - 查询 Super Mario Maker 2 关卡信息
"""

from aiogram import types
from aiogram.utils import markdown as md
import aiohttp
import logging

from common import error_message
from config import config

GAME_STYLES: list[str] = ['超马1', '超马3', '超马世界', '新超马U', '超马3D世界']
DIFFICULTY: list[str] = ['❇ 简单', '✴ 普通', '☢ 困难', '🈲 极难']
THEMES: dict[str, str] = {
    'Castle': '🏰 城堡', 'Airship': '🛸 飞行船', 'Ghost house': '🌃 鬼屋', 'Underground': '🪨 地下', 'Sky': '✈ 天空',
    'Snow': '☃ 雪原', 'Desert': '🏜 沙漠', 'Overworld': '🏞 平原', 'Forest': '🌲 丛林', 'Underwater': '🐳 水中'
}
TAGS: dict[int, str] = {
    1: "🎮 标准",
    2: "🧩 解谜",
    3: "⏰ 计时挑战",
    4: "📨 自动卷轴",
    5: "🎁 自动马力欧",
    6: "☑ 一次通过",
    7: "⚔ 多人对战",
    8: "🖥 机关设计",
    9: "🎹 音乐",
    10: "🖼 美术",
    11: "🕹 技巧",
    12: "🔫 射击",
    13: "🪚 BOSS战",
    14: "👤 单打",
    15: "🏹 林克"
}


def prettify_difficulty(difficulty: str) -> str:
    integer: str = difficulty.split('.')[0]
    decimal: str = difficulty.split('.')[1].strip('%')
    decimal = decimal[:2] if len(decimal) >= 2 else decimal
    return integer + '.' + decimal + '%' if decimal != '0' else integer + '%'


async def handler(message: types.Message):
    # 输入关卡 ID
    level_id: str = message.get_args().strip()
    level_id = level_id.replace(' ', '').replace('-', '').replace('_', '').upper()
    if len(level_id) != 9:
        await error_message(message, 'smm2_level', ['<关卡ID>'])
        return
    logging.info(f'smm2_level {level_id}')
    msg = await message.reply(
        '🔍 正在查询关卡 ' + md.code(level_id) + md.escape_md(' ...'),
        parse_mode='MarkdownV2'
    )
    # 调用 tgrcode api
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{config.modules.smm2.api}/level_info/{level_id}') as resp:
            if resp.status != 200:
                await msg.edit_text('❌ 查询失败: ' + str(resp.status))
                return
            level_info: dict = await resp.json()
            if config.bot.debug:
                logging.info(level_info)
            if 'error' in level_info:
                await msg.edit_text('❌ 查询失败: ' + level_info['error'])
                return
            # 处理结果
            theme_emoji, theme_name = THEMES[level_info['theme_name']].split(' ')
            game_style = GAME_STYLES[level_info['game_style']]
            retval: str = (
                f'🕹 {md.bold(md.escape_md(level_info["name"]))}\n'
                f'🌏 场景: {theme_emoji} {game_style} {theme_name}\n'
                f'🏷 标签: {md.escape_md(", ".join([TAGS[tag] for tag in level_info["tags"]]))}\n'
                f'👤 作者: {md.escape_md(level_info["uploader"]["name"])} {md.code(level_info["uploader"]["code"])}\n'
                f'📤 日期: {md.escape_md(prettify_difficulty(level_info["uploaded_pretty"].split(" ")[0]))}\n'
                f'📄 简介: {md.escape_md(level_info["description"])}\n'
                f'🚩 难度: {DIFFICULTY[level_info["difficulty"]]} {md.escape_md(level_info["clear_rate"])}% '
                f'\\({level_info["clears"]}🚩 / {level_info["attempts"]}🕹️\\)\n'
                f'❤ 赞踩: {level_info["likes"]}❤ / {level_info["boos"]}💔\n'
                f'👤 首插: {md.escape_md(level_info["first_completer"]["name"])} {md.code(level_info["first_completer"]["code"])}\n'
                f'👤 纪录: {md.escape_md(level_info["record_holder"]["name"])} {md.code(level_info["record_holder"]["code"])} '
                f'\\(⏲️ {md.escape_md(level_info["world_record_pretty"])}\\)\n'
            )
            if config.bot.debug:
                logging.info(retval)
            await msg.edit_text(
                retval + md.escape_md('\n正在发送预览图...'),
                parse_mode='MarkdownV2'
            )
            await message.reply_media_group(
                [
                    types.InputMediaPhoto(
                        media=f'{config.modules.smm2.api}/level_thumbnail/{level_id}',
                        caption=f'🔍 {level_id} - 关卡预览图',
                    ),
                    types.InputMediaPhoto(
                        media=f'{config.modules.smm2.api}/level_entire_thumbnail/{level_id}',
                        caption=f'🔍 {level_id} - 关卡全景图',
                    )
                ]
            )
            await msg.edit_text(
                retval,
                parse_mode='MarkdownV2'
            )
