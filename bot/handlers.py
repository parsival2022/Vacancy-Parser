from aiogram.types import FSInputFile, InputMediaPhoto
from .callbacks import Callbacks
from .keyboards import *
from .utils import *

async def ToMainMenuHandler(bot, cb_query, msg):
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(main_menu_kb, 1))

async def ReturnTermsKb(bot, cb_query, msg, cb):
    if cb == Callbacks.F_ALL_CLUSTERS_CB:
        msg = msg + " Remember, that statistic will be shown for all clusters."
    else: 
        msg = msg + " Remember, that statistic will be shown only for chosen cluster."
    kb = compile_callbacks(terms_kb, cb)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def ReturnClustersKb(bot, cb_query, msg):
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(clusters_kb, 1))

async def ReturnOptionsKb(bot, cb_query, msg, cluster, term):
    cluster_name = [b["text"] for b in clusters_kb if b["callback_data"] == cluster][0]
    term_name = [b["text"] for b in terms_kb if b["callback_data"] == term][0]
    msg = msg + f" Statistics will be shown for {cluster_name} cluster and {term_name} term."
    kb = compile_callbacks(stats_options_kb, cluster, term)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                        message_id=cb_query.message.message_id, 
                                        reply_markup=create_markup(kb, 1))
    
async def ReturnGraphHandler(bot, st_manager, cb_query, cluster, term, option, chart="bar"):
    cl_key = None if cluster == Callbacks.F_ALL_CLUSTERS_CB else cluster.split("_")[0]
    term = int(term)
    key = Callbacks.MAPPING.get(option)
    filenames, stats = st_manager.get_stats_chart(key, cl_key=cl_key, term=term, chart=chart)
    charts = [FSInputFile(f"charts/{filename}") for filename in filenames]
    await bot.send_media_group(chat_id=cb_query.from_user.id,
                                media=[InputMediaPhoto(media=chart) for chart in charts])
    clear_charts(filenames)