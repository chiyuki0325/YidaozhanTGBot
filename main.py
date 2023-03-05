import logging
from aiogram import Bot, Dispatcher, executor, types
from config import config
from commands import (
    arch,
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


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    await inline_handler(inline_query, bot)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
