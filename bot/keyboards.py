from dataclasses import dataclass
from .utils import btn, create_markup

@dataclass
class Callbacks:
    TO_MAIN_MENU_CB = "t_main_mn"
    CHOOSE_CLUSTER_CB = "ch_clstr"
    STATS_FOR_ALL_CLUSTERS_CB = "sts_f_all_clstrs"

    PYTHON_CLUSTER_CHOICE_CB = "python_cl"
    JAVA_CLUSTER_CHOICE_CB = "java_cl"
    JS_CLUSTER_CHOICE_CB = "js_cl"
    CPP_CLUSTER_CHOICE_CB = "cpp_cl"

    TECHS_FOR_ALL_CLUSTERS_CB = "tech_f_all_cl"
    LEVELS_FOR_ALL_CLUSTERS_CB = "levels_f_all_cl"
    SKILLS_FOR_ALL_CLUSTERS_CB = "skills_f_all_cl"
    EMPL_TYPES_FOR_ALL_CLUSTERS_CB = "emplty_f_all_cl"
    WORKPLACE_TYPES_FOR_ALL_CLUSTERS_CB = "workplty_f_all_cl"
    LOCATIONS_FOR_ALL_CLUSTERS_CB = "locs_f_all_cl"


CLUSTER_CHOICES = (Callbacks.PYTHON_CLUSTER_CHOICE_CB,
                   Callbacks.JAVA_CLUSTER_CHOICE_CB,
                   Callbacks.JS_CLUSTER_CHOICE_CB,
                   Callbacks.CPP_CLUSTER_CHOICE_CB)

STAT_OPTIONS_FOR_ALL_CLUSTERS = (Callbacks.TECHS_FOR_ALL_CLUSTERS_CB,
                                 Callbacks.LEVELS_FOR_ALL_CLUSTERS_CB,
                                 Callbacks.SKILLS_FOR_ALL_CLUSTERS_CB,
                                 Callbacks.EMPL_TYPES_FOR_ALL_CLUSTERS_CB,
                                 Callbacks.WORKPLACE_TYPES_FOR_ALL_CLUSTERS_CB,
                                 Callbacks.LOCATIONS_FOR_ALL_CLUSTERS_CB)

back_to_main_btn = btn("Back to main menu", Callbacks.TO_MAIN_MENU_CB)

main_menu_kb = [
        btn("Get statistic for cluster", Callbacks.CHOOSE_CLUSTER_CB),
        btn("Get statistic for all clusters", Callbacks.STATS_FOR_ALL_CLUSTERS_CB)
    ]

stats_options_for_all_clusters = [
    btn("Technologies", Callbacks.TECHS_FOR_ALL_CLUSTERS_CB),
    btn("Levels", Callbacks.LEVELS_FOR_ALL_CLUSTERS_CB),
    btn("Skills", Callbacks.SKILLS_FOR_ALL_CLUSTERS_CB),
    btn("Employment types", Callbacks.EMPL_TYPES_FOR_ALL_CLUSTERS_CB),
    btn("Workplace type", Callbacks.WORKPLACE_TYPES_FOR_ALL_CLUSTERS_CB),
    btn("Locations", Callbacks.LOCATIONS_FOR_ALL_CLUSTERS_CB),
    back_to_main_btn
]

clusters = [
    btn("Python", Callbacks.PYTHON_CLUSTER_CHOICE_CB),
    btn("Java", Callbacks.JAVA_CLUSTER_CHOICE_CB),
    btn("Java Script", Callbacks.JS_CLUSTER_CHOICE_CB),
    btn("C++", Callbacks.CPP_CLUSTER_CHOICE_CB),
    back_to_main_btn
]