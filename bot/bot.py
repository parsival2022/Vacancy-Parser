import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from db_manager.mongo_manager import MongoManager
from statistic_manager.statistic_manager import StatisticManager
from .utils import create_markup
from .keyboards import Keyboards
from .handlers import *
from .messages import Messages
from .session import Session

TOKEN = os.getenv("BOT_TOKEN")
COLLECTION = os.getenv("MONGO_DB_NAME")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
db = MongoManager(COLLECTION)
sm = StatisticManager(db)

@dp.message(CommandStart())
async def commandStartHandler(message: Message) -> None:
    user_session = Session(message)
    if not user_session.exists():
        Session.register_user(message)
        await message.answer(Messages.greet_msg, reply_markup=create_markup(Keyboards.choose_lang_kb, 1))
    if not user_session.lang:
        msg = Messages.greet_msg
        kb = Keyboards.choose_lang_kb
        await message.answer(msg, reply_markup=create_markup(kb, 2))
    else:
        msg = Messages.get_msg("start_cmd", user_session.lang)
        kb = Keyboards.get_keyboard("main_menu_kb", user_session.lang)
        await message.answer(msg, reply_markup=create_markup(kb, 2))
    
@dp.callback_query(lambda c: c.data )
async def CallbacksHandler(callback_query:CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query.id)
    options = callback_query.data.split("&")
    current_session = Session(callback_query)
    if not current_session.exists():
        msg = Messages.no_session_msg
        kb = Keyboards.choose_lang_kb
        await bot.edit_message_text(msg, chat_id=callback_query.from_user.id, 
                                    message_id=callback_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
        return
    lang = current_session.lang
    match options:
        case options if len(options) == 1 and options[0] in Callbacks.LANGS:
            current_session.change_lang(*options)
            await ToMainMenuHandler(bot, callback_query, *options)
        case options if len(options) == 1 and options[0] == Callbacks.CHOOSE_LANG_CB:
            await ReturnLangsKb(bot, callback_query, lang)
        case options if len(options) == 1 and options[0] == Callbacks.TO_MAIN_MENU_CB:
            current_session.clear()
            await ToMainMenuHandler(bot, callback_query, lang)
        case options if len(options) == 1 and options[0] == Callbacks.CHOOSE_COMPARATIVE_CB:
            await ReturnComparTermsMenu(bot, callback_query, lang, current_session)
        case options if len(options) == 1 and options[0] == Callbacks.CHOOSE_CLUSTER_CB:
            await ReturnClustersKb(bot, callback_query, lang)
        case options if len(options) == 1 and options[0] in Callbacks.CLUSTERS:
            await ReturnTermsKb(bot, callback_query, lang, *options)
        case options if len(options) == 2 and options[0] in Callbacks.CLUSTERS and options[1] in Callbacks.TERMS:
            await ReturnOptionsKb(bot, callback_query, lang, *options)
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and (options[1] in Callbacks.TERMS or options[1] == Callbacks.CH_LOCATIONS_CB):
            await ReturnComparLocationsMenu(bot, callback_query, lang, current_session, options[1])
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and options[1] in Callbacks.LOCATIONS:
            await HandleComparLocationsMenu(bot, callback_query, lang, current_session, options[1])
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and options[1] == Callbacks.CHOOSE_CLUSTER_CB:
            await ReturnComparClustersKb(bot, callback_query, lang)
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and options[1] in Callbacks.CLUSTERS:
            await HandleComparClustersMenu(bot, callback_query, lang, current_session, options[1])
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and options[1] == Callbacks.CHOOSE_OPTION_CB:
            await ReturnComparOptionsKb(bot, callback_query, lang, current_session)
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and options[1] in Callbacks.OPTIONS:
            await HandleComparOptionsMenu(bot, callback_query, lang, current_session, options[1])
        case options if len(options) == 2 and options[0] == Callbacks.COMPARATIVE_CB and options[1] == Callbacks.GET_STATS_CB:
            await ReturnComparGraph(bot, callback_query, lang, current_session)
        case options if len(options) == 3 and options[0] in Callbacks.CLUSTERS and options[1] in Callbacks.TERMS and options[2] in Callbacks.OPTIONS:
            await ReturnGraphHandler(bot, sm, callback_query, lang, *options)

async def main() -> None:
    await dp.start_polling(bot)
