from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

import json


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr

    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла сразу создастся
# и провалидируется объект конфига,
# который можно далее импортировать из разных мест

import json

data_timer = dict()
# Opening JSON file
try:
    with open('data_timer.json') as json_file:
        data_timer = json.load(json_file)
except:
    data_timer = {'minutes': 1, 'hours': 0}
    with open('data_timer.json', 'w') as file:
        json.dump(data_timer, file)


def change(new_data_timer):
    with open('data_timer.json', 'w') as file:
        json.dump(new_data_timer, file)

settings = Settings()