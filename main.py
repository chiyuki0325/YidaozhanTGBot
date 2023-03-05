import logging
from aiogram import Bot, Dispatcher, executor, types
from config import config
from commands import (
    arch,
    smm2_level,
    yiyan
)
from inline import inline_handler

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot.token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['arch'])
async def arch_handler(message: types.Message):
    try:
        await arch.handler(message)
    except Exception as e:
        logging.error(e)
        await message.reply('❌ 发生了未知错误: ' + str(e))


@dp.message_handler(commands=['smm2_level'])
async def smm2_level_handler(message: types.Message):
    try:
        await smm2_level.handler(message)
    except Exception as e:
        logging.error(e)
        await message.reply('❌ 发生了未知错误: ' + str(e))


@dp.message_handler(commands=['yiyan'])
async def yiyan_handler(message: types.Message):
    try:
        await yiyan.handler(message)
    except Exception as e:
        logging.error(e)
        await message.reply('❌ 发生了未知错误: ' + str(e))


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    await inline_handler(inline_query, bot)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
