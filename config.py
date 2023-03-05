from os import getenv
from yaml import safe_load
from pydantic import BaseModel


class Config(BaseModel):
    class Bot(BaseModel):
        token: str
        debug: bool

    bot: Bot


config_path: str = getenv('YIDAOZHAN_TGBOT_CONFIG_PATH', 'config.yml')
_config: dict = safe_load(open(config_path, 'r'))
config: Config = Config(**_config)
