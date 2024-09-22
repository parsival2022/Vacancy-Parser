import os
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callbacks import Callbacks

btn = lambda t, cb_d: {"text": t, "callback_data": cb_d}

def create_markup(buttons, sizes):
    builder = InlineKeyboardBuilder()
    for b in buttons: 
        builder.button(**b)
    builder.adjust(sizes, repeat=True)
    return builder.as_markup()

def compile_callbacks(kb, *args):
    new_kb = [bt.update({"callback_data": "&".join([*args, bt["callback_data"]])}) for bt in kb if bt["callback_data"] is not Callbacks.TO_MAIN_MENU_CB]
    new_kb.append(kb[-1])
    print(new_kb)
    return new_kb

def clear_charts(charts):
    for chartname in charts:
        path = f"charts/{chartname}"
        if os.path.exists(path):
            os.remove(path)