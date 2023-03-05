"""
arch.py - 查询 Arch Linux 软件包
"""
from datetime import datetime
from aiogram import types
from aiogram.utils import markdown as md
import aiohttp
import logging
import deepl
from pydantic import BaseModel
from typing import Optional

from common import error_message
from config import config


class OfficialPackage(BaseModel):
    pkgname: str
    pkgbase: str
    repo: str
    arch: str
    pkgver: str
    pkgrel: str
    epoch: int
    pkgdesc: str
    url: str
    filename: str
    compressed_size: int
    installed_size: int
    build_date: datetime
    last_update: datetime
    flag_date: Optional[datetime | None]
    maintainers: list[str]
    packager: str
    groups: list[str]
    licenses: list[str]
    conflicts: list[str]
    provides: list[str]
    replaces: list[str]
    depends: list[str]
    optdepends: list[str]
    makedepends: list[str]
    checkdepends: list[str]


class OfficialResponse(BaseModel):
    version: int
    limit: int
    valid: bool
    results: list[OfficialPackage]
    num_pages: int
    page: int


class AURPackage(BaseModel):
    ID: int
    Name: str
    PackageBaseID: int
    PackageBase: str
    Version: str
    Description: str
    URL: str
    NumVotes: int
    Popularity: float
    OutOfDate: Optional[datetime | None]
    Maintainer: str
    FirstSubmitted: datetime
    LastModified: datetime
    URLPath: str
    Depends: Optional[list[str]]
    MakeDepends: Optional[list[str]]
    CheckDepends: Optional[list[str]]
    OptDepends: Optional[list[str]]
    Conflicts: Optional[list[str]]
    Provides: Optional[list[str]]
    Replaces: Optional[list[str]]
    Groups: Optional[list[str]]
    Licenses: Optional[list[str]]
    Keywords: Optional[list[str]]


class AURResponse(BaseModel):
    version: int
    type: str
    resultcount: int
    results: list[AURPackage]


class AURPackageSearch(BaseModel):
    Description: str
    FirstSubmitted: datetime
    ID: int
    LastModified: datetime
    Maintainer: str
    Name: str
    NumVotes: int
    OutOfDate: Optional[datetime | None]
    PackageBase: str
    PackageBaseID: int
    Popularity: float
    URL: str
    URLPath: str
    Version: str


class AURResponseSearch(BaseModel):
    version: int
    type: str
    resultcount: int
    results: list[AURPackageSearch]


async def handler(message: types.Message):
    pkgname = message.get_args().strip()
    session = aiohttp.ClientSession()
    logging.info(f'arch: {pkgname}')
    if pkgname == '':
        await error_message(message, 'arch', ['<包名或关键词>'])
        await session.close()
        return
    msg = (  # 回复一条加载中的消息，稍后用于编辑
        await message.reply(
            '🔍 正在查询软件包 ' + md.code(pkgname) + md.escape_md(' ...'),
            parse_mode='MarkdownV2'
        )
    )
    # 从官方仓库查询
    async with session.get(
            url=f'https://archlinux.org/packages/search/json/?name={pkgname}'
    ) as response_official:
        if config.bot.debug:
            logging.debug(await response_official.text())
        official_response: OfficialResponse = OfficialResponse.parse_obj(
            await response_official.json()
        )
    if not official_response.results:
        await msg.edit_text(
            f"⏰ 在官方仓库中找不到以 {md.code(pkgname)} {md.escape_md('为名的软件包，正在 AUR 仓库查询 ...')}",
            parse_mode='MarkdownV2'
        )
        # 官方仓库中没有找到以 pkgname 为名的软件包，从 AUR 仓库查询
        async with session.get(
                url=f'https://aur.archlinux.org/rpc/?v=5&type=info&arg={pkgname}'
        ) as response_aur:
            if config.bot.debug:
                logging.debug(await response_aur.text())
            aur_response: AURResponse = AURResponse.parse_obj(
                await response_aur.json()
            )
        if not aur_response.results:
            # AUR 仓库中也没有找到以 pkgname 为名的软件包，进行关键词模糊搜索
            await msg.edit_text(
                f'⏰ 在 AUR 仓库中找不到以 {md.code(pkgname)} 为名的软件包，正在关键词模糊搜索 {md.escape_md("...")}',
                parse_mode='MarkdownV2'
            )
            async with session.get(
                    url=f'https://archlinux.org/packages/search/json/?q={pkgname}'
            ) as response_search:
                if config.bot.debug:
                    logging.debug(await response_search.text())
                official_packages_response = OfficialResponse.parse_obj(
                    await response_search.json()
                )
            if not official_packages_response.results:
                results_official = f'⚠ 官方仓库中没有找到以 {md.code(pkgname)} 为关键词的软件包。'
            else:
                results_official = md.escape_md('📦 官方仓库搜索结果如下:')
                i = 0
                while i < 8:
                    if len(official_packages_response.results) > i:
                        package: OfficialPackage = official_packages_response.results[i]
                        results_official += (
                            f'\n\\- {md.code(package.repo)}/{md.code(package.pkgname)} '
                            f' \\(v{md.code(package.pkgver)}\\-{md.code(package.pkgrel)}'
                            '\\)'
                        )
                        results_official += '\n  ' + md.bold('简介') + ':' + md.escape_md(package.pkgdesc)
                    i += 1
            if config.bot.debug:
                logging.info(results_official)
            await msg.edit_text(results_official, parse_mode='MarkdownV2')
            async with session.get(
                    url=f'https://aur.archlinux.org/rpc/?v=5&type=search&arg={pkgname}'
            ) as response_search:
                if config.bot.debug:
                    logging.debug(await response_search.text())
                aur_packages_response = AURResponseSearch.parse_obj(
                    await response_search.json()
                )
            if not aur_packages_response.results:
                results_aur = f'⚠ AUR 仓库中没有找到以 {md.code(pkgname)} 为关键词的软件包。'
            else:
                results_aur = md.escape_md('📦 AUR 仓库搜索结果如下:')
                i = 0
                while i < 8:
                    if len(aur_packages_response.results) > i:
                        package: AURPackageSearch = aur_packages_response.results[i]
                        results_aur += (
                            f'\n\\- {md.code(package.Name)} '
                            f' \\(v{md.code(package.Version)}\\)'
                        )
                        results_aur += '\n  ' + md.bold('简介') + ':' + md.escape_md(package.Description)
                    i += 1
            if config.bot.debug:
                logging.info(results_aur)
            await msg.edit_text(
                f'{results_official}\n\n{results_aur}',
                parse_mode='MarkdownV2'
            )
            await session.close()
            return
        else:
            # AUR 仓库中找到了以 pkgname 为名的软件包
            await msg.edit_text('⏰ 查询完毕，正在处理结果 ...')
            package: AURPackage = aur_response.results[0]
            return_message = generate_aur_result(
                package,
                package.Description,
                parse_optdepends(package.OptDepends)
            )
            if config.bot.debug:
                logging.info(return_message)
            await msg.edit_text(
                return_message.strip(),
                parse_mode='MarkdownV2',
                disable_web_page_preview=True)
            translated_description: str = deepl.translate(
                source_language='EN',
                target_language='ZH',
                text=package.Description
            )
            return_message = generate_aur_result(
                package,
                translated_description,
                parse_optdepends_translate(package.OptDepends)
            )
            if config.bot.debug:
                logging.info(return_message)
            await msg.edit_text(
                return_message.strip(),
                parse_mode='MarkdownV2',
                disable_web_page_preview=True
            )
            await session.close()
            return

    else:  # 官方仓库中找到了以 pkgname 为名的软件包
        await msg.edit_text('⏰ 查询完毕，正在处理结果 ...')
        package: OfficialPackage = official_response.results[0]
        return_message = generate_official_result(package, package.pkgdesc)
        if config.bot.debug:
            logging.info(return_message)
        await msg.edit_text(
            return_message.strip(),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        translated_description: str = deepl.translate(
            source_language='EN',
            target_language='ZH',
            text=package.pkgdesc
        )
        return_message = generate_official_result(package, translated_description)
        if config.bot.debug:
            logging.info(return_message)
        await msg.edit_text(
            return_message.strip(),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
    await session.close()
    return


def generate_official_result(package: OfficialPackage, description: str) -> str:
    # 生成官方仓库软件包的查询结果
    retval: str = (f"📦 **官方仓库软件包** {md.code(package.repo)}/{md.code(package.pkgname)}  "
                   f"\\(v{md.code(package.pkgver)}\\-{md.code(package.pkgrel)}\\)"
                   "\n")
    if package.groups:
        retval += f"\\- **属于包组** {parse_pkgname_list(package.groups)}" + '\n'
    retval += f"\\- **简介**: {md.escape_md(description)}" + '\n'
    if package.depends:
        retval += f"\\- **依赖**: {parse_pkgname_list(package.depends)}" + '\n'
    if package.optdepends:
        retval += f"\\- **可选依赖**: {parse_pkgname_list(package.optdepends)}" + '\n'
    if package.provides:
        retval += f"\\- **提供**: {parse_pkgname_list(package.provides)}" + '\n'
    if package.conflicts:
        retval += f"\\- **冲突**: {parse_pkgname_list(package.conflicts)}" + '\n'
    if package.replaces:
        retval += f"\\- **替代**: {parse_pkgname_list(package.replaces)}" + '\n'
    retval += f"\\- **维护者**: {parse_pkgname_list(package.maintainers)}" + '\n'
    retval += '\\- **上次更新**: ' + md.escape_md(package.last_update.strftime('%Y-%m-%d')) + '\n'
    retval += '\\- **安装大小**: ' + md.escape_md(
        str(round(package.installed_size / 1000000, 2)) + 'MB'
    ) + '\n'
    retval += f'[查看上游]({md.escape_md(package.url)}) \\| ' \
              f'[查看详情](https://archlinux.org/packages/{package.pkgname})\n'
    return retval


def generate_aur_result(package: AURPackage, description: str, optdepends_str: str) -> str:
    retval = f"📦 **AUR 软件包** {md.code(package.Name)}  \\(v{md.code(package.Version)}\\)\n"
    if package.Groups:
        retval += '\\- **属于包组** ' + parse_pkgname_list(package.Groups) + '\n'
    retval += '\\- **简介**: ' + md.escape_md(description) + '\n'
    if package.Keywords:
        retval += '\\- **关键词**: ' + parse_pkgname_list(package.Keywords) + '\n'
    if package.Depends:
        retval += '\\- **依赖**: ' + parse_pkgname_list(package.Depends) + '\n'
    if package.OptDepends:
        retval += '\\- **可选依赖**: ' + optdepends_str + '\n'
    if package.MakeDepends:
        retval += '\\- **编译依赖**: ' + parse_pkgname_list(package.MakeDepends) + '\n'
    if package.Provides:
        retval += '\\- **提供**: ' + parse_pkgname_list(package.Provides) + '\n'
    if package.Conflicts:
        retval += '\\- **冲突**: ' + parse_pkgname_list(package.Conflicts) + '\n'
    retval += '\\- **维护者**: ' + md.escape_md(package.Maintainer) + '\n'
    retval += '\\- **上次更新**: ' + md.escape_md(package.LastModified.strftime('%Y-%m-%d'))
    if package.OutOfDate:
        retval += ' **\\(已过期\\)**' + '\n'
    else:
        retval += '\n'
    retval += (
        '\\- 得票数: '
        f'{md.escape_md(str(package.NumVotes))}'
        ', 欢迎度: '
        f'{md.escape_md(str(package.Popularity))}'
        '\n'
    )
    retval += f'[查看上游]({md.escape_md(package.URL)}) \\| ' \
              f'[PKGBUILD](https://aur.archlinux.org{package.URLPath}) \\| ' \
              f'[查看详情](https://aur.archlinux.org/packages/{package.Name})\n'
    return retval


# 处理包名列表和可选依赖列表用

def parse_pkgname_list(pkgnames):
    retval = '`'
    for pkgname in pkgnames:
        retval += md.escape_md(pkgname) + '`, `'
    return retval[:-3]


def parse_optdepends_translate(optdepends) -> str:
    retval = ''
    for optdepend in optdepends:
        try:
            retval += md.code(optdepend.split(':')[0].strip()) + ': ' + md.escape_md(
                deepl.translate(
                    text=optdepend.split(':')[1].strip(), source_language="EN",
                    target_language="ZH"
                )
            ) + '\n  '
        except IndexError:
            retval += md.code(optdepend) + ', '
    return retval.strip('\n ')


def parse_optdepends(optdepends) -> str:
    retval = ''
    for optdepend in optdepends:
        try:
            retval += md.code(optdepend.split(':')[0].strip()) + ': ' + md.escape_md(
                optdepend.split(':')[1].strip()) + '\n  '
        except IndexError:
            retval += md.code(optdepend) + ', '
    return retval.strip('\n ')
