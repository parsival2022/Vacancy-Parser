from dataclasses import dataclass
from clusters import *

@dataclass
class Callbacks:
    TO_MAIN_MENU_CB = "t_main_mn"
    CHOOSE_CLUSTER_CB = "ch_clstr"
    CHOOSE_PERIOD_CB = "ch_prd"
    CHOOSE_COMPARATIVE_CB = "ch_cmprt"
    CHOOSE_PLAIN_STAT_CB = "ch_plst"
    CHOOSE_LANG_CB = "ch_lng"
    CHOOSE_OTHER_OPTION = "ch_othopt"
    CHOOSE_OTHER_TERM = "ch_othtrm"

    LNG_UA_CB = "ua"
    LNG_ENG_CB = "eng"

    F_ALL_CLUSTERS_CB = "all_cl"
    F_PYTHON_CLUSTER_CB = f"{PYTHON}_cl"
    F_JAVA_CLUSTER_CB = f"{JAVA}_cl"
    F_JS_CLUSTER_CB = f"{JS}_cl"
    F_CPP_CLUSTER_CB = f"{CPP}_cl"

    TERM_10D_CB = "10"
    TERM_20D_CB = "20"
    TERM_30D_CB = "30"
    TERM_60D_CB = "60"
    TERM_180D_CB = "180"
    TERM_365D_CB = "365"

    CH_TECHS_CB = "tech"
    CH_LEVELS_CB = "levels"
    CH_SKILLS_CB = "skls"
    CH_EMPL_CB = "emplty"
    CH_WORKPLACE_CB = "workplty"
    CH_LOCATIONS_CB = "locs"

    CLUSTERS = (F_ALL_CLUSTERS_CB,
                F_PYTHON_CLUSTER_CB,
                F_JAVA_CLUSTER_CB,
                F_JS_CLUSTER_CB,
                F_CPP_CLUSTER_CB)
    
    OPTIONS = (CH_TECHS_CB, 
               CH_LEVELS_CB, 
               CH_SKILLS_CB, 
               CH_EMPL_CB, 
               CH_WORKPLACE_CB, 
               CH_LOCATIONS_CB)

    TERMS = (TERM_10D_CB,
             TERM_20D_CB,
             TERM_30D_CB,
             TERM_60D_CB,
             TERM_180D_CB,
             TERM_365D_CB)
    
    LANGS = (LNG_UA_CB,
             LNG_ENG_CB)
    
    MAPPING = {
        CH_TECHS_CB: "technologies",
        CH_LEVELS_CB: "level",
        CH_SKILLS_CB: "skills",
        CH_EMPL_CB: "employment_type", 
        CH_WORKPLACE_CB: "workplace_type",
        CH_LOCATIONS_CB: "location"
    }