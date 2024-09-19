from dataclasses import dataclass
from .utils import btn

def compile_cb( *args):
    res = []
    for arg in args:
        res.append(Callbacks.__getattribute__(arg))
    return "&".join(res)

@dataclass
class Callbacks:
    TO_MAIN_MENU_CB = "t_main_mn"
    CHOOSE_CLUSTER_CB = "ch_clstr"
    STATS_FOR_ALL_CLUSTERS_CB = "sts_f_all_clstrs"

    F_ALL_CLUSTERS_CB = "all_cl"
    F_PYTHON_CLUSTER_CB = "python_cl"
    F_JAVA_CLUSTER_CB = "java_cl"
    F_JS_CLUSTER_CB = "js_cl"
    F_CPP_CLUSTER_CB = "cpp_cl"

    CH_TECHS_CB = "tech"
    CH_LEVELS_CB = "levels"
    CH_SKILLS_CB = "skills"
    CH_EMPL_CB = "emplty"
    CH_WORKPLACE_CB = "workplty"
    CH_LOCATIONS_CB = "locs"

    TECHS_FOR_ALL_CLUSTERS_CB = "tech_f_all_cl"
    LEVELS_FOR_ALL_CLUSTERS_CB = "levels_f_all_cl"
    SKILLS_FOR_ALL_CLUSTERS_CB = "skills_f_all_cl"
    EMPL_TYPES_FOR_ALL_CLUSTERS_CB = "emplty_f_all_cl"
    WORKPLACE_TYPES_FOR_ALL_CLUSTERS_CB = "workplty_f_all_cl"
    LOCATIONS_FOR_ALL_CLUSTERS_CB = "locs_f_all_cl"




CLUSTER_CHOICES = (Callbacks.F_ALL_CLUSTERS_CB,
                   Callbacks.F_PYTHON_CLUSTER_CB,
                   Callbacks.F_JAVA_CLUSTER_CB,
                   Callbacks.F_JS_CLUSTER_CB,
                   Callbacks.F_CPP_CLUSTER_CB)

OPTIONS = (Callbacks.CH_TECHS_CB, 
           Callbacks.CH_LEVELS_CB, 
           Callbacks.CH_SKILLS_CB, 
           Callbacks.CH_EMPL_CB, 
           Callbacks.CH_WORKPLACE_CB, 
           Callbacks.CH_LOCATIONS_CB)

STAT_OPTIONS_FOR_ALL_CLUSTERS = (opt + "&" + Callbacks.F_ALL_CLUSTERS_CB for opt in OPTIONS)

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
    btn("Python", Callbacks.F_PYTHON_CLUSTER_CB),
    btn("Java", Callbacks.F_JAVA_CLUSTER_CB),
    btn("Java Script", Callbacks.F_JS_CLUSTER_CB),
    btn("C++", Callbacks.F_CPP_CLUSTER_CB),
    back_to_main_btn
]