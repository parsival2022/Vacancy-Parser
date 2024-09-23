from aiogram.types import FSInputFile, InputMediaPhoto
from clusters import CLUSTERS
from .callbacks import Callbacks
from .keyboards import Keyboards
from .messages import Messages
from .session import Session
from .utils import *


async def ToMainMenuHandler(bot, cb_query, lang):
    kb = Keyboards.get_keyboard("main_menu_kb", lang)
    msg = Messages.get_msg("start_cmd", lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def ReturnLangsKb(bot, cb_query, lang):
    kb = Keyboards.get_keyboard("choose_lang_kb", lang, add=["back_to_main_btn"])
    msg = Messages.get_msg("choose_lang", lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))

async def ReturnTermsKb(bot, cb_query, lang, cb):
    msg = Messages.get_msg("choose_terms", lang)
    if cb == Callbacks.F_ALL_CLUSTERS_CB:
        msg = Messages.add_to_msg(msg, "choose_terms_add_all_cl", lang)
    else:
        cl_key = cb.split("_")[0]
        cl_name = CLUSTERS[cl_key]["name"]
        msg = Messages.add_to_msg(msg, "choose_terms_add_one_cl", lang, cl_name)
    kb = Keyboards.get_keyboard("terms_kb", lang)
    compile_callbacks(kb, cb)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def ReturnClustersKb(bot, cb_query, lang):
    kb = Keyboards.get_keyboard("clusters_kb", lang)
    msg = Messages.get_msg("choose_cluster", lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))

async def ReturnOptionsKb(bot, cb_query, lang, cluster, term):
    msg = Messages.get_msg("choose_option", lang)
    term_name = [b["text"] for b in Keyboards.get_keyboard("terms_kb", lang) if b["callback_data"] == term][0]
    try:
        cluster_name = [b["text"] for b in Keyboards.clusters_kb if b["callback_data"] == cluster][0]
        msg = Messages.add_to_msg(msg, "choose_option_add", lang, cluster_name, term_name)
    except IndexError:
        msg = Messages.add_to_msg(msg, "choose_option_add", lang, term_name=term_name)
    kb = Keyboards.get_keyboard("stats_options_kb", lang)
    compile_callbacks(kb, cluster, term)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                        message_id=cb_query.message.message_id, 
                                        reply_markup=create_markup(kb, 1))
    
async def ReturnGraphHandler(bot, st_manager, cb_query, lang, cluster, term, option, chart="bar"):
    cl_key = None if cluster == Callbacks.F_ALL_CLUSTERS_CB else cluster.split("_")[0]
    term = int(term)
    key = Callbacks.MAPPING.get(option)
    filenames, stats = st_manager.get_stats_chart(key, cl_key=cl_key, term=term, chart=chart)
    charts = [FSInputFile(f"charts/{filename}") for filename in filenames]
    await bot.send_media_group(chat_id=cb_query.from_user.id,
                                media=[InputMediaPhoto(media=chart) for chart in charts])
    kb = Keyboards.get_keyboard("after_graph_menu", lang)
    msg = Messages.get_msg("after_graph", lang)
    await bot.send_message(text=msg, chat_id=cb_query.from_user.id,
                           reply_markup=create_markup(kb, 1))
    clear_charts(filenames)