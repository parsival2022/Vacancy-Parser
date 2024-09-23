from typing import Callable
class Messages:
    eng_start_cmd = "Let's begin! First, choose a statistics option:"
    ua_start_cmd = "Почнімо! Спочатку оберіть опцію статистики:"
    eng_choose_lang = "Choose a language for communication!"
    ua_choose_lang = "Оберіть мову спілкування:"
    eng_choose_cluster = "Please choose the cluster you want to get statistics for. Remember, that statistic will be shown only for that cluster."
    ua_choose_cluster = "Будь ласка оберіть кластер, для якого ви хотіли б отримати статистику. Майте на увазі, що статистика буде показана тільки для цього кластера."
    eng_choose_terms = "Please choose the period of time for which you want to get statistics for."
    ua_choose_terms = "Будь ласка оберіть період часу, за який ви хочете отримати статистику."
    eng_choose_terms_add_all_cl = "Remember, that statistic will be shown for all clusters."
    ua_choose_terms_add_all_cl = "Майте на увазі, що статистика буде показана для всіх кластерів."
    eng_choose_terms_add_one_cl = lambda cl_name: f"Remember, that statistic will be shown only for {cl_name} cluster."
    ua_choose_terms_add_one_cl = lambda cl_name: f"Статистика буде показана тільки для кластера {cl_name}."
    eng_choose_option = "Please choose the option you want to get statistics for."
    ua_choose_option = "Будь ласка оберіть опцію, для якої ви хочете отримати статистику."
    eng_choose_option_add = lambda cluster_name="every", term_name="10 days": f"Statistics will be shown for {cluster_name} cluster and {term_name} period of time."
    ua_choose_option_add = lambda cluster_name="кожного", term_name="10 днів": f"Статистика буде показана для {cluster_name} кластера за період у {term_name}."
    eng_after_graph = "Choose following action"
    ua_after_graph = "Оберіть подальші дії"
    greet_msg = "Привіт! Почнемо роботу? Для початку оберіть мову спілкування:\nHello! Let`s begin, shall we? First, choose a language for communication: "
    no_session_msg = "It looks like you did not choose a language yet. Please choose your language!\nСхоже ви ще не обрали мову спілкування. Будь ласка, зробіть це зараз!"

    @classmethod
    def get_msg(cls, core_name, lang):
        attribute_name = f"{lang}_{core_name}"
        return getattr(cls, attribute_name)
    
    @classmethod
    def add_to_msg(cls, msg, core_name, lang, *args, **kwargs):
        msg_to_add = cls.get_msg(core_name, lang)
        if args and isinstance(msg_to_add, Callable) or kwargs and isinstance(msg_to_add, Callable):
            msg_to_add = msg_to_add(*args, **kwargs)
        return msg + " " + msg_to_add
