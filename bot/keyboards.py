import copy
from clusters import *
from .callbacks import Callbacks
from .utils import btn   

L_ENG = "eng"
L_UA = "ua"

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
        btn("Skills", Callbacks.CH_SKILLS_CB),
        btn("Employment types", Callbacks.CH_EMPL_CB),
        btn("Workplace type", Callbacks.CH_WORKPLACE_CB),
        btn("Locations", Callbacks.CH_LOCATIONS_CB),
        btn("Salary", Callbacks.CH_LOCATIONS_CB),
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
    locations_kb = [
        btn(UA, Callbacks.LOC_UA_CB),
        btn(EU, Callbacks.LOC_EU_CB),
        btn(UK, Callbacks.LOC_UK_CB),
        btn(USA, Callbacks.LOC_USA_CB),
        back_to_main_btn
    ]
    compar_loc_or_cluster_kb = [
        btn("Choose another location", Callbacks.CH_LOCATIONS_CB),
        btn("Choose cluster", Callbacks.CHOOSE_CLUSTER_CB),
        back_to_main_btn
    ]
    compar_cluster_or_option_kb = [
        btn("Choose another cluster", Callbacks.CHOOSE_CLUSTER_CB),
        btn("Choose option", Callbacks.CHOOSE_OPTION_CB),
        back_to_main_btn
    ]
    compar_option_or_graph_kb = [
        btn("Choose another option", Callbacks.CHOOSE_OPTION_CB),
        btn("Get statistic", Callbacks.GET_STATS_CB),
        back_to_main_btn
    ]
    after_graph_menu = [
        btn("Choose other option", Callbacks.CHOOSE_OTHER_OPTION),
        btn("Choose other period of time", Callbacks.CHOOSE_OTHER_TERM),
        back_to_main_btn
    ]

    LANGS = {
        L_UA: {
            UA: "Україна",
            EU: "Європейський Союз",
            UK: "Сполучене Королівство",
            USA: "Сполучені Штати Америки",
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
            "Change language": "Змінити мову",
            "Choose cluster": "Обрати кластер",
            "Choose another location": "Обрати ще один регіон",
            "Choose another option": "Додати ще одне поле",
            "Get statistic": "Отримати статистику",
            "Choose other period of time": "Обрати інший період часу",
            "Choose another cluster": "Обрати ще один кластер",
            "Choose option": "Обрати поле"
        }
    }

    @classmethod
    def create_keyboard(cls, kb, lang):
        copied_kb = kb[:]
        if lang != L_ENG:
            mapping = cls.LANGS.get(lang)
            for btn in copied_kb:
                new_text = mapping.get(btn["text"])
                if new_text:
                    btn["text"] = new_text
        return copied_kb

    @classmethod
    def get_keyboard(cls, kb_name, lang, add=[]):
        kb = getattr(cls, str(kb_name))[:]
        if add:
            for s in add:
                el = getattr(cls, str(s))
                kb.extend(el) if isinstance(el, list) else kb.append(el)
        kb = copy.deepcopy(kb)
        return cls.create_keyboard(kb, lang)