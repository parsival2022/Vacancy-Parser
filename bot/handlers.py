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
        msg = Messages.get_msg(msg, "choose_option_add", lang, cluster_name, term_name)
    except IndexError:
        msg = Messages.get_msg(msg, "choose_option_add", lang, term_name=term_name)
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

async def ReturnComparTermsMenu(bot, cb_query, lang, session):
    session.start_query()
    msg = Messages.get_msg("choose_terms_compar", lang)
    kb = Keyboards.get_keyboard("terms_kb", lang)
    compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                        message_id=cb_query.message.message_id, 
                                        reply_markup=create_markup(kb, 1))
    
async def ReturnComparLocationsMenu(bot, cb_query, lang, session, term):
    try:
        term = int(term)
        session.add_to_query("term", term)
    except ValueError:
        pass
    msg = Messages.get_msg("choose_location_compar", lang)
    kb = Keyboards.get_keyboard("locations_kb", lang)
    compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def HandleComparLocationsMenu(bot, cb_query, lang, session, loc):
    query = session.get_query()
    locations = query.get("locations")
    location = Callbacks.MAPPING.get(loc)
    kb = Keyboards.get_keyboard("compar_loc_or_cluster_kb", lang)
    compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
    if locations and location in locations:
        msg = Messages.get_msg("already_chosen_loc", lang)
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
        return
    if not locations: 
        session.add_to_query("locations", [location])
    elif locations and not location in locations:
        session.push_to_query("locations", location)
    loc_name = [b["text"] for b in Keyboards.get_keyboard("locations_kb", lang) if b["callback_data"] == loc][0]
    msg = Messages.get_msg("location_saved", lang, loc_name)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
                                
async def ReturnComparClustersKb(bot, cb_query, lang):
    kb = Keyboards.get_keyboard("clusters_kb", lang)
    compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
    msg = Messages.get_msg("choose_compar_cluster", lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def HandleComparClustersMenu(bot, cb_query, lang, session, cluster):
    filter_func = lambda btn: btn["callback_data"] != Callbacks.CHOOSE_OPTION_CB
    query = session.get_query()
    locations = query.get("locations")
    clusters = query.get("clusters")
    cl_key = cluster.split("_")[0]
    if len(locations) > 1:
        session.add_to_query("clusters", [cl_key])
        msg = Messages.get_msg("compar_only_one_cluster", lang)
        kb = Keyboards.get_keyboard("stats_options_kb", lang)
        compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
        return
    kb = Keyboards.get_keyboard("compar_cluster_or_option_kb", lang)
    if len(locations) == 1 and clusters and cl_key in clusters:
        msg = Messages.get_msg("compar_already_chosen_cluster", lang)
    if len(locations) == 1 and not clusters:
        session.add_to_query("clusters", [cl_key])
        kb = [btn for btn in filter(filter_func, kb)]
        msg = Messages.get_msg("compar_choose_another_cluster", lang)
    if len(locations) == 1 and clusters and not cl_key in clusters:
        session.push_to_query("clusters", cl_key)
        cl_name = CLUSTERS.get(cl_key)["name"]
        msg = Messages.get_msg("compar_cluster_added", lang, cl_name)
    compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))

async def ReturnComparOptionsKb(bot, cb_query, lang, session:Session):
    filter_func = lambda btn: btn["callback_data"] not in [Callbacks.CH_TECHS_CB, Callbacks.CH_SKILLS_CB] 
    query = session.get_query()
    locations = query.get("locations")
    kb = Keyboards.get_keyboard("stats_options_kb", lang)
    msg = Messages.get_msg("choose_option", lang)
    if len(locations) == 1:
        kb = [btn for btn in filter(filter_func, kb)]
    compile_callbacks(kb, Callbacks.COMPARATIVE_CB)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def HandleComparOptionsMenu(bot, cb_query, lang, session, opt):
    query = session.get_query()
    options = query.get("options")
    option = Callbacks.MAPPING.get(opt)
    kb = Keyboards.get_keyboard("compar_option_or_graph_kb", lang)
    if options and option in options:
        msg = Messages.get_msg("already_chosen_opt", lang)
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
        return
    if not options: 
        session.add_to_query("locations", [option])
    elif options and not option in options:
        session.push_to_query("locations", option)
    opt_name = [b["text"] for b in Keyboards.get_keyboard("stats_options_kb", lang) if b["callback_data"] == opt][0]
    msg = Messages.get_msg("location_saved", lang, opt_name)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
    
async def ReturnComparGraph(bot, cb_query, lang, session):
    pass