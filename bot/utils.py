import os
from aiogram.utils.keyboard import InlineKeyboardBuilder

def clear_charts(charts):
    for chartname in charts:
        path = f"charts/{chartname}"
        if os.path.exists(path):
            os.remove(path)

btn = lambda t, cb_d: {"text": t, "callback_data": cb_d}

def create_markup(buttons, sizes):
    builder = InlineKeyboardBuilder()
    for b in buttons: 
        builder.button(**b)
    builder.adjust(sizes, repeat=True)
    return builder.as_markup()