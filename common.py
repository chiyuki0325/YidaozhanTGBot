from aiogram.utils import markdown as md


async def error_message(message, command_name: str, args: list):
    await message.reply(
        '❌ 用法: ' + md.code(f'/{command_name} {" ".join(args)}'),
        parse_mode='MarkdownV2'
    )
