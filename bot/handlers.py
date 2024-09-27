from aiogram.types import FSInputFile, InputMediaPhoto
from clusters import CLUSTERS
from .callbacks import Callbacks
from .keyboards import Keyboards
from .messages import Messages
from .session import Session
from .utils import *


async def ToMainMenuHandler(bot, cb_query, session, lang):
    session.clear()
    msg, kb = get_msg_and_kb("start_cmd", "main_menu_kb",  lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def ReturnLangsKb(bot, cb_query, lang):
    msg, kb = get_msg_and_kb("choose_lang", "choose_lang_kb", lang, msg_args=["back_to_main_btn"])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def ReturnClustersKb(bot, cb_query, lang):
    msg, kb = get_msg_and_kb("choose_cluster", "clusters_kb",  lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))

async def ReturnTermsKb(bot, cb_query, lang, session, cluster):
    session.combine_title(cb_query, cluster)
    if cluster == Callbacks.F_ALL_CLUSTERS_CB:
        msg, kb = get_msg_and_kb("choose_terms_all_cl", "terms_kb", lang, compile=[cluster])
    else:
        cl_key = cluster.split("_")[0]
        msg, kb = get_msg_and_kb("choose_terms_one_cl", "terms_kb", lang, msg_args=[CLUSTERS[cl_key]["name"]], compile=[cluster])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def ReturnLocationsKb(bot, cb_query, lang, session, cluster, term):
    session.combine_title(cb_query, term)
    msg, kb = get_msg_and_kb("choose_location", "locations_kb", lang, compile=[cluster, term])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))

async def ReturnOptionsKb(bot, cb_query, lang, session, cluster, term, location):
    session.combine_title(cb_query, location)
    term_name = [b["text"] for b in Keyboards.get_keyboard("terms_kb", lang) if b["callback_data"] == term][0]
    try:
        cluster_name = [b["text"] for b in Keyboards.clusters_kb if b["callback_data"] == cluster][0]
        msg_args = [cluster_name, term_name]
    except IndexError:
        msg_args = [term_name]
    msg, kb = get_msg_and_kb("choose_option_add", "stats_options_kb", lang, compile=[cluster, term, location], msg_args=msg_args,)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                     message_id=cb_query.message.message_id, 
                                     reply_markup=create_markup(kb, 1))
    
async def ReturnGraphHandler(bot, st_manager, cb_query, lang, session, cluster, term, location, option, chart="pie"):
    session.combine_title(cb_query, option)
    session.refresh()
    title_data = session.get_title()
    msg = Messages.get_msg("stat_is_calculating", lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=None)
    cl_key, term, location, key = prepare_args(cluster, term, location, option)
    filenames, stats = st_manager.get_stats_chart(key, term, location, title_data, cl_key=cl_key, chart=chart)
    charts = [FSInputFile(f"charts/{filename}") for filename in filenames]
    await bot.delete_message(chat_id=cb_query.from_user.id, 
                             message_id=cb_query.message.message_id,)
    await bot.send_media_group(chat_id=cb_query.from_user.id,
                                media=[InputMediaPhoto(media=chart) for chart in charts])
    msg, kb = get_msg_and_kb("start_cmd", "main_menu_kb", lang)
    await bot.send_message(chat_id=cb_query.from_user.id,
                           text=msg, 
                           reply_markup=create_markup(kb, 1))
    session.clear()
    clear_charts(filenames)

async def ReturnComparTermsMenu(bot, cb_query, lang, session):
    session.start_query()
    msg, kb = get_msg_and_kb("choose_terms_compar", "terms_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                        message_id=cb_query.message.message_id, 
                                        reply_markup=create_markup(kb, 1))
    
async def ReturnComparLocationsMenu(bot, cb_query, lang, session, term):
    try:
        term = int(term)
        session.add_to_query("term", term)
    except ValueError:
        pass
    msg, kb = get_msg_and_kb("choose_location_compar", "locations_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
                                
async def ReturnComparClustersMenu(bot, cb_query, lang):
    msg, kb = get_msg_and_kb("choose_compar_cluster", "clusters_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))

async def ReturnComparOptionsMenu(bot, cb_query, lang, session:Session):
    query = session.get_query()
    locations = query.get("locations")
    filter_func = lambda btn: btn["callback_data"] not in [Callbacks.CH_TECHS_CB, Callbacks.CH_SKILLS_CB] if len(locations) == 1 else None                                                      
    msg, kb = get_msg_and_kb("choose_option", "stats_options_kb", lang, compile=[Callbacks.COMPARATIVE_CB], filter_func=filter_func)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    
async def HandleComparLocationsMenu(bot, cb_query, lang, session, loc):
    query = session.get_query()
    locations = query.get("locations")
    location = Callbacks.MAPPING.get(loc)
    if locations and location in locations:
        msg, kb = get_msg_and_kb("already_chosen_loc", "compar_loc_or_cluster_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
        return
    if not locations: 
        session.add_to_query("locations", [location])
    elif locations and not location in locations:
        session.push_to_query("locations", location)
    loc_name = [b["text"] for b in Keyboards.get_keyboard("locations_kb", lang) if b["callback_data"] == loc][0]
    msg, kb = get_msg_and_kb("location_saved", "compar_loc_or_cluster_kb", lang, compile=[Callbacks.COMPARATIVE_CB], msg_args=[loc_name])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
    
async def HandleComparClustersMenu(bot, cb_query, lang, session, cluster):
    query = session.get_query()
    locations = query.get("locations")
    clusters = query.get("clusters")
    cl_key = cluster.split("_")[0]
    if len(locations) > 1 and not clusters:
        session.add_to_query("clusters", [cl_key])
        filter_func = lambda btn: btn["callback_data"] != Callbacks.CHOOSE_OPTION_CB
        msg, kb = get_msg_and_kb("compar_only_one_cluster", "stats_options_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                message_id=cb_query.message.message_id, 
                                reply_markup=create_markup(kb, 1))
    elif len(locations) == 1:
        if clusters and cl_key in clusters:
            msg, kb = get_msg_and_kb("compar_already_chosen_cluster", "compar_cluster_or_option_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
        if not clusters:
            session.add_to_query("clusters", [cl_key])
            filter_func = lambda btn: btn["callback_data"] != Callbacks.CHOOSE_OPTION_CB
            msg, kb = get_msg_and_kb("compar_choose_another_cluster", "compar_cluster_or_option_kb", lang, compile=[Callbacks.COMPARATIVE_CB], filter_func=filter_func)
        if clusters and not cl_key in clusters:
            session.push_to_query("clusters", cl_key)
            cl_name = CLUSTERS.get(cl_key)["name"]
            msg, kb = get_msg_and_kb("compar_cluster_added", "compar_cluster_or_option_kb", lang, compile=[Callbacks.COMPARATIVE_CB], msg_args=[cl_name])
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1)) 
        
async def HandleComparOptionsMenu(bot, cb_query, lang, session, opt):
    query = session.get_query()
    options = query.get("options")
    option = Callbacks.MAPPING.get(opt) or None
    if options and option in options:
        msg, kb = get_msg_and_kb("compar_already_chosen_opt", "compar_option_or_graph_kb", lang, compile=[Callbacks.COMPARATIVE_CB])
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
        return
    if not options: 
        session.add_to_query("options", [option])
    elif options and not option in options:
        session.push_to_query("options", option)
    if opt == Callbacks.CH_COUNT_CB:
        f_f = lambda btn: btn["callback_data"] != Callbacks.CHOOSE_OPTION_CB
        msg, kb = get_msg_and_kb("count_option", "compar_option_or_graph_kb", lang, compile=[Callbacks.COMPARATIVE_CB], filter_func=f_f)
    else:
        opt_name = [b["text"] for b in Keyboards.get_keyboard("stats_options_kb", lang) if b["callback_data"] == opt][0]
        msg, kb = get_msg_and_kb("option_saved", "compar_option_or_graph_kb", lang, compile=[Callbacks.COMPARATIVE_CB], msg_args=[opt_name])
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=create_markup(kb, 1))
    
async def ReturnComparGraphHandler(bot, cb_query, lang, session, s_m):
    msg = Messages.get_msg("stat_is_calculating", lang)
    await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=None)
    query = session.get_query()
    if len(query["locations"]) == 1:
        title = Messages.get_msg("compar_stat_for_location", lang, query["locations"][0], query["clusters"])
    else:
        title = Messages.get_msg("compar_stat_for_cluster", lang, query["clusters"][0], query["locations"])
    filenames, stats = s_m.get_comparative_stats_chart(query, title)
    if not filenames:
        msg = Messages.get_msg("no_data", lang)
        await bot.edit_message_text(msg, chat_id=cb_query.from_user.id, 
                                    message_id=cb_query.message.message_id, 
                                    reply_markup=None)
        msg, kb = get_msg_and_kb("start_cmd", "main_menu_kb",  lang)
        await bot.send_message(chat_id=cb_query.from_user.id,
                           text=msg, 
                           reply_markup=create_markup(kb, 1))
        return
    charts = [FSInputFile(f"charts/{filename}") for filename in filenames]
    await bot.delete_message(chat_id=cb_query.from_user.id, 
                             message_id=cb_query.message.message_id,)
    await bot.send_media_group(chat_id=cb_query.from_user.id,
                                media=[InputMediaPhoto(media=chart) for chart in charts])
    msg, kb = get_msg_and_kb("start_cmd", "main_menu_kb",  lang)
    await bot.send_message(chat_id=cb_query.from_user.id,
                           text=msg, 
                           reply_markup=create_markup(kb, 1))
    clear_charts(filenames)

