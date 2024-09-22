import copy
from clusters import *
from .callbacks import Callbacks
from .utils import btn   

ENG = "eng"
UA = "ua"

class Keyboards:
    back_to_main_btn = btn("Back to main menu", Callbacks.TO_MAIN_MENU_CB)

    main_menu_kb = [
        btn("Get statistic for cluster", Callbacks.CHOOSE_CLUSTER_CB),
        btn("Get statistic for all clusters", Callbacks.F_ALL_CLUSTERS_CB),
        btn("Get comparative statistic", Callbacks.CHOOSE_COMPARATIVE_CB),
        btn("Change language", Callbacks.CHOOSE_LANG_CB)
    ]

    choose_lang_kb = [
        btn("English", Callbacks.LNG_ENG_CB),
        btn("Українська", Callbacks.LNG_UA_CB),
    ]

    stats_options_kb = [
        btn("Technologies", Callbacks.CH_TECHS_CB),
        btn("Levels", Callbacks.CH_LEVELS_CB),
        btn("Skills", Callbacks.CH_LEVELS_CB),
        btn("Employment types", Callbacks.CH_EMPL_CB),
        btn("Workplace type", Callbacks.CH_WORKPLACE_CB),
        btn("Locations", Callbacks.CH_LOCATIONS_CB),
        back_to_main_btn
    ]

    clusters_kb = [
        btn("Python", Callbacks.F_PYTHON_CLUSTER_CB),
        btn("Java", Callbacks.F_JAVA_CLUSTER_CB),
        btn("Java Script", Callbacks.F_JS_CLUSTER_CB),
        btn("C++", Callbacks.F_CPP_CLUSTER_CB),
        back_to_main_btn
    ]

    terms_kb = [
        btn("10 days", Callbacks.TERM_10D_CB),
        btn("20 days", Callbacks.TERM_20D_CB),
        btn("30 days", Callbacks.TERM_30D_CB),
        btn("60 days", Callbacks.TERM_60D_CB),
        btn("180 days", Callbacks.TERM_180D_CB),
        btn("365 days", Callbacks.TERM_365D_CB),
        back_to_main_btn
    ]

    LANGS = {
        UA: {
            "10 days": "10 днів",
            "20 days": "20 днів",
            "30 days": "30 днів",
            "60 days": "60 днів",
            "180 days": "180 днів",
            "365 days": "365 днів",
            "Get statistic for cluster": "Отримати статистику для кластеру",
            "Get statistic for all clusters": "Отримати статистику для всіх кластерів",
            "Get comparative statistic": "Отримати порівняльну статистику",
            "Back to main menu": "До головного меню",
            "Change language": "Змінити мову"
        }
    }

    @classmethod
    def create_keyboard(cls, kb, lang):
        copied_kb = kb[:]
        if lang != ENG:
            mapping = cls.LANGS.get(lang)
            for btn in copied_kb:
                new_text = mapping.get(btn["text"])
                if new_text:
                    btn["text"] = new_text
        print(copied_kb)
        return copied_kb

    @classmethod
    def get_keyboard(cls, kb_name, lang=ENG, add=[]):
        kb = getattr(cls, str(kb_name))[:]
        if add:
            for s in add:
                el = getattr(cls, str(s))
                kb.extend(el) if isinstance(el, list) else kb.append(el)
        kb = copy.deepcopy(kb)
        return cls.create_keyboard(kb, lang)