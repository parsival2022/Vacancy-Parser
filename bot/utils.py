import os
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callbacks import Callbacks
from .keyboards import Keyboards
from .messages import Messages

def create_markup(buttons, sizes):
    builder = InlineKeyboardBuilder()
    for b in buttons: 
        builder.button(**b)
    builder.adjust(sizes, repeat=True)
    return builder.as_markup()

def compile_callbacks(kb, *args):
    new_kb = [bt.update({"callback_data": "&".join([*args, bt["callback_data"]])}) for bt in kb if bt["callback_data"] is not Callbacks.TO_MAIN_MENU_CB]
    new_kb.append(kb[-1])
    return new_kb

def clear_charts(charts):
    for chartname in charts:
        path = f"charts/{chartname}"
        if os.path.exists(path):
            os.remove(path)

def prepare_args(cluster, term, location, option):
    cl_k = None if cluster == Callbacks.F_ALL_CLUSTERS_CB else cluster.split("_")[0]
    t = int(term)
    lc = Callbacks.MAPPING.get(location)
    key = Callbacks.MAPPING.get(option)
    return cl_k, t, lc, key

def get_msg_and_kb(msg_name, kb_name, lang, compile=[], msg_args=[], kb_add=[], filter_func=None):
    msg = Messages.get_msg(msg_name, lang, *msg_args)
    kb = Keyboards.get_keyboard(kb_name, lang, add=kb_add)
    if filter_func:
        kb = [btn for btn in filter(filter_func, kb)]
    if compile:
        compile_callbacks(kb, *compile)
    return msg, kb

def create_text_version(stats, indent=0):
    result = ""
    try:
        title = stats.pop("title")
        result = f"<b><i>{title}:</i></b>\n"
        indent += 1
    except (KeyError, AttributeError):
        pass
    indents = "   " * indent
    for k, v in stats.items():
        try:
            k = v.pop("title")
        except (KeyError, AttributeError):
            pass
        if isinstance(v, dict) and not v.get("None"):
            result += f"{indents}<b><i>{k[0].upper() + k[1:]}:</i></b>\n{create_text_version(v, indent + 1)}"
        elif isinstance(v, dict) and v.get("None"):
            result += f"{indents}<b>{k[0].upper() + k[1:]}:</b> {v.get('None')}\n"
        else:
            result += f"{indents}<b>{k.title()}:</b> {v}\n"
    return result