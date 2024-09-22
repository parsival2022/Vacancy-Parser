from dataclasses import dataclass
from clusters import *
from .callbacks import Callbacks
from .utils import btn   

back_to_main_btn = btn("Back to main menu", Callbacks.TO_MAIN_MENU_CB)

main_menu_kb = [
        btn("Get statistic for cluster", Callbacks.CHOOSE_CLUSTER_CB),
        btn("Get statistic for all clusters", Callbacks.F_ALL_CLUSTERS_CB)
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