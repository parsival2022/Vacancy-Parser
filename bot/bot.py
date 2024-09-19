import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from db_manager.mongo_manager import MongoManager
from statistic_manager.statistic_manager import StatisticManager
from .keyboards import *
from .utils import clear_charts, create_markup

TOKEN = os.getenv("BOT_TOKEN")
COLLECTION = os.getenv("MONGO_DB_NAME")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
db = MongoManager(COLLECTION)
sm = StatisticManager(db)

async def send_charts(chart_names, callback_query):
    charts = [FSInputFile(f"charts/{filename}") for filename in chart_names]
    await bot.send_media_group(chat_id=callback_query.from_user.id,
                                media=[InputMediaPhoto(media=chart) for chart in charts])
    clear_charts(chart_names)

@dp.message(CommandStart())
async def commandStartHandler(message: Message) -> None:
    msg = "Please choose the option:"
    await message.answer(msg, reply_markup=create_markup(main_menu_kb, 2))
                         
@dp.callback_query(lambda c: c.data and c.data == Callbacks.CHOOSE_CLUSTER_CB)
async def ChooseClusterMenu(callback_query:CallbackQuery) -> None:
   await bot.answer_callback_query(callback_query.id)
   msg = "Please choose the cluster you want to get statistics for. Remember, that statistic will be shown only for that cluster."
   await bot.edit_message_text(msg, chat_id=callback_query.from_user.id, 
                               message_id=callback_query.message.message_id, 
                               reply_markup=create_markup(clusters, 1))
   
@dp.callback_query(lambda c: c.data and c.data in CLUSTER_CHOICES)
async def OptionsForOneClusterMenu(callback_query:CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query.id)
    stats_options_for_one_cluster = []
    for button in stats_options_for_all_clusters:
        cb = button.get("callback_data").replace("all_cl", callback_query.data)
        stats_options_for_one_cluster.append(btn(button.get("text"), cb))
    msg = "Please choose the cluster you want to get statistics for. Remember, that statistic will be shown only for that cluster."
    await bot.edit_message_text(msg, chat_id=callback_query.from_user.id, 
                               message_id=callback_query.message.message_id, 
                               reply_markup=create_markup(stats_options_for_one_cluster, 1))
    
@dp.callback_query(lambda c: c.data )
async def StatForAllClusters(callback_query:CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query.id)
    options = callback_query.data.split("&")
    match callback_query.data:
        case Callbacks.TO_MAIN_MENU_CB:
            msg = "Please choose the option:"
            await bot.edit_message_text(msg, chat_id=callback_query.from_user.id, 
                                        message_id=callback_query.message.message_id, 
                                        reply_markup=create_markup(main_menu_kb, 2))
        case Callbacks.STATS_FOR_ALL_CLUSTERS_CB:
            msg = "Please choose the type you want to get statistics for. Remember, that statistic will be shown for all clusters."
            await bot.edit_message_text(msg, chat_id=callback_query.from_user.id, 
                                        message_id=callback_query.message.message_id, 
                                        reply_markup=create_markup(stats_options_for_all_clusters, 1))
        case Callbacks.CHOOSE_CLUSTER_CB:
            msg = "Please choose the cluster you want to get statistics for. Remember, that statistic will be shown only for that cluster."
            await bot.edit_message_text(msg, chat_id=callback_query.from_user.id, 
                                        message_id=callback_query.message.message_id, 
                                        reply_markup=create_markup(clusters, 1))
        case Callbacks.TECHS_FOR_ALL_CLUSTERS_CB:
            chart_names, stats = sm.get_stats_barchart("technologies")
            await send_charts(chart_names, callback_query)
        case Callbacks.LEVELS_FOR_ALL_CLUSTERS_CB:
            chart_names, stats = sm.get_stats_barchart("level", y_label="Levels")
            await send_charts(chart_names, callback_query)
        case Callbacks.SKILLS_FOR_ALL_CLUSTERS_CB:
            chart_names, stats = sm.get_stats_barchart("skills", y_label="Skills")
            await send_charts(chart_names, callback_query)
        case Callbacks.EMPL_TYPES_FOR_ALL_CLUSTERS_CB:
            chart_names, stats = sm.get_stats_barchart("employment_type", y_label="Employment types")
            await send_charts(chart_names, callback_query)
        case Callbacks.WORKPLACE_TYPES_FOR_ALL_CLUSTERS_CB:
            chart_names, stats = sm.get_stats_barchart("workplace_type", y_label="Workplace types")
            await send_charts(chart_names, callback_query)
        case Callbacks.LOCATIONS_FOR_ALL_CLUSTERS_CB:
            chart_names, stats = sm.get_stats_barchart("location", y_label="Locations")
            await send_charts(chart_names, callback_query)

async def main() -> None:
    await dp.start_polling(bot)
