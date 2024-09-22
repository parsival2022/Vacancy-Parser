import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from db_manager.mongo_manager import MongoManager
from statistic_manager.statistic_manager import StatisticManager
from .utils import create_markup
from .keyboards import *
from .handlers import *

TOKEN = os.getenv("BOT_TOKEN")
COLLECTION = os.getenv("MONGO_DB_NAME")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
db = MongoManager(COLLECTION)
sm = StatisticManager(db)

@dp.message(CommandStart())
async def commandStartHandler(message: Message) -> None:
    msg = "Please choose the option:"
    await message.answer(msg, reply_markup=create_markup(main_menu_kb, 2))
    
@dp.callback_query(lambda c: c.data )
async def CallbacksHandler(callback_query:CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query.id)
    options = callback_query.data.split("&")
    print(options)
    match options:
        case options if len(options) == 1 and options[0] == Callbacks.TO_MAIN_MENU_CB:
            msg = "Please choose the option:"
            await ToMainMenuHandler(bot, callback_query, msg)
        case options if len(options) == 1 and options[0] == Callbacks.CHOOSE_CLUSTER_CB:
            msg = "Please choose the cluster you want to get statistics for. Remember, that statistic will be shown only for that cluster."
            await ReturnClustersKb(bot, callback_query, msg)
        case options if len(options) == 1 and options[0] in Callbacks.CLUSTERS:
            msg = "Please choose the period of time for which you want to get statistics for."
            await ReturnTermsKb(bot, callback_query, msg, *options)
        case options if len(options) == 2 and options[0] in Callbacks.CLUSTERS and options[1] in Callbacks.TERMS:
            msg = "Please choose the option you want to get statistics for."
            await ReturnOptionsKb(bot, callback_query, msg, *options)
        case options if len(options) == 2 and options[0] in Callbacks.CLUSTERS and options[1] in Callbacks.TERMS and options[2] in Callbacks.OPTIONS:
            await ReturnGraphHandler(bot, sm, callback_query, *options)

async def main() -> None:
    await dp.start_polling(bot)
