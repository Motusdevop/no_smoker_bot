import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.markdown import hbold


from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

from config import settings, data_timer, change


# Bot token can be obtained via https://t.me/BotFather
TOKEN = "YOUR_TOKEN"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


# Add middleware Scheduler
class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # add apscheduler to data
        data["apscheduler"] = self.scheduler
        return await handler(event, data)


async def send_message_scheduler(bot: Bot, message: str, user_id: int):
    await bot.send_message(chat_id=int(user_id), text=message)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", parse_mode=ParseMode.HTML)

@dp.message(Command('set'))
async def command_set(message: Message, command: CommandObject):
    try:
        global data_timer

        args = command.args
        list_args = args.split(':')
        hours = int(list_args[0])
        minutes = int(list_args[1])

        data_timer = {
            "minutes": minutes,
            "hours": hours
        }

        change(data_timer)

        await message.answer('Таймаут изменён')
    except:
        await message.answer('что-то не так')



@dp.message(Command('reload'))
async def echo_handler(
    message: types.Message, bot: Bot, apscheduler: AsyncIOScheduler
) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        dt = datetime.now() + timedelta(**data_timer)
        print(dt, bot, message.chat.id, message.text)
        apscheduler.add_job(
            send_message_scheduler,
            trigger="date",
            run_date=dt,
            kwargs={
                "bot": bot,
                "message": 'Можно сделать тягу!!!',
                "user_id": message.chat.id,
            },
        )
        await message.answer(f'Сообщение будет отправлено через: {data_timer.__str__()}')
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(settings.bot_token.get_secret_value())
    # And the run events dispatching
    scheduler = AsyncIOScheduler()
    timezone="Europe/Moscow"

    dp.update.middleware(
        SchedulerMiddleware(scheduler=scheduler),
    )
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
