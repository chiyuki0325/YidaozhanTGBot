from os import getenv
from yaml import safe_load
from pydantic import BaseModel


class Config(BaseModel):
    class Bot(BaseModel):
        token: str
        debug: bool

    class Modules(BaseModel):
        class SMM2(BaseModel):
            api: str

        class GengShuang(BaseModel):
            api: str

        class DingZhen(BaseModel):
            api: str

        smm2: SMM2
        gengshuang: GengShuang
        dingzhen: DingZhen

    bot: Bot
    modules: Modules


config_path: str = getenv('YIDAOZHAN_TGBOT_CONFIG_PATH', 'config.yml')
_config: dict = safe_load(open(config_path, 'r'))
config: Config = Config(**_config)
