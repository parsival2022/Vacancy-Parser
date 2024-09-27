from typing import Callable
from .keyboards import Keyboards

class Messages:
    eng_start_cmd = "Let's begin! Choose the option for statistic:"
    ua_start_cmd = "Почнімо! Оберіть опцію статистики:"
    eng_choose_lang = "Choose a language for communication:"
    ua_choose_lang = "Оберіть мову спілкування:"
    eng_choose_cluster = "Please choose the cluster you want to get statistics for. Remember, that statistic will be shown only for that cluster."
    ua_choose_cluster = "Будь ласка оберіть кластер, для якого ви хотіли б отримати статистику. Майте на увазі, що статистика буде показана тільки для цього кластера."
    eng_choose_terms = "Please choose the period of time for which you want to get statistics for."
    ua_choose_terms = "Будь ласка оберіть період часу, за який ви хочете отримати статистику."
    eng_no_data = "No data has been found for your request. Probably, still parsing! Call it later."
    ua_no_data = "Для обрахування вашого запиту недостатньо даних. Мабуть, досі збираються! Спробуйте пізніше."
    eng_choose_terms_all_cl = eng_choose_terms + " " + "Remember, that statistic will be shown for all clusters."
    ua_choose_terms_all_cl = ua_choose_terms + " " + "Майте на увазі, що статистика буде показана для всіх кластерів."
    eng_choose_terms_one_cl = lambda cl_name, msg=eng_choose_terms : f"{msg} Remember, that statistic will be shown only for {cl_name} cluster."
    ua_choose_terms_one_cl = lambda cl_name, msg=ua_choose_terms: f"{msg} Статистика буде показана тільки для кластера {cl_name}."
    eng_choose_option = "Please choose the option you want to get statistics for."
    ua_choose_option = "Будь ласка оберіть опцію, для якої ви хочете отримати статистику."
    eng_choose_option_add = lambda cluster_name="every", term_name="10 days", msg=eng_choose_option: f"{msg} Statistics will be shown for {cluster_name} cluster and {term_name} period of time."
    ua_choose_option_add = lambda cluster_name="кожного", term_name="10 днів", msg=ua_choose_option: f"{msg} Статистика буде показана для {cluster_name} кластера за період у {term_name}."
    eng_choose_terms_compar = "Choose period of time for which comparative statistic will be calculated."
    ua_choose_terms_compar = "Оберіть період, за який буде обрахована порівняльна статистика."
    eng_choose_location = "Choose location for which you want to get statistic for."
    ua_choose_location = "Оберіть регіон, по якому ви хочете отримати статистику."
    eng_choose_location_compar = f"{eng_choose_location} If you choose multiple locations, only one cluster is available to get statistic for."
    ua_choose_location_compar = f"{ua_choose_location} Якщо ви оберете кілька регіонів, то подальша статистика буде доступна тільки для одного кластеру."
    eng_already_chosen_loc = "You have chosen this location already. Choose another location or move on to choose clusters to compare."
    ua_already_chosen_loc = "Ви вже обрали цей регіон. Оберіть інший регіон або перейдіть до вибору кластерів до порівняння."
    eng_location_saved = lambda location: f"You succefully have chosen {location}. You can choose another location to compare or go to cluster choices."
    ua_location_saved = lambda location: f"Ви успішно обрали регіон {location}. Можете обрати ще один регіон або перейти до вибору кластерів"
    eng_choose_compar_cluster = "Please choose cluster or clusters to calculate statistics for."
    ua_choose_compar_cluster = "Будь ласка оберіть кластер або кластери, для яких потрібно обрахувати статистику."
    eng_compar_only_one_cluster = "You have chosen more then one locations, therefore comparative statistic could be calculated for one cluster. Please choose option in cluster to get statistic for."
    ua_compar_only_one_cluster = "Ви обрали більше одного регіону, тож порівняльна статистика може бути обрахована тільки для одного кластеру. Будь ласка оберіть поле, для якого буде обрахована статистика."
    eng_compar_choose_another_cluster = "You have chosen only one location. You have to choose another cluster to calculate comparative statistics."
    ua_compar_choose_another_cluster = "Ви обрали лише один регіон. Оберіть додаткові кластери, щоб обрахувати для них порівняльну статистику."
    eng_compar_already_chosen_cluster = "You have chosen this cluster already. Choose another cluster or move on to choose option of the cluster."
    ua_compar_already_chosen_cluster = "Ви вже обрали цей кластер. Оберіть інший кластер або перейдіть до вибору поля кластеру."
    eng_compar_cluster_added = lambda cl_name: f"Cluster {cl_name} has been added. Choose another cluster or move on to choose option of the cluster."
    ua_compar_cluster_added = lambda cl_name: f"Кластер {cl_name} було додано. Оберіть інший кластер або перейдіть до вибору поля кластеру."
    eng_compar_already_chosen_opt = "You have chosen this option already. Choose another option or get statistic."
    ua_compar_already_chosen_opt = "Ви вже додали це поле. Оберіть інше поле або отримайте статистику."
    eng_option_saved = lambda option: f"You succefully have chosen {option}. You can choose another option to get statistic for or move to getting statistic."
    ua_option_saved = lambda option: f"Ви успішно обрали поле {option}. Можете обрати ще одну опцію або перейти до отримання статистики."
    greet_msg = "Привіт! Почнемо роботу? Для початку оберіть мову спілкування:\nHello! Let`s begin, shall we? First, choose a language for communication: "
    no_session_msg = "It looks like you did not choose a language yet. Please choose your language!\nСхоже ви ще не обрали мову спілкування. Будь ласка, зробіть це зараз!"
    eng_stat_is_calculating = "Wait a minute, statistic is calculating..."
    ua_stat_is_calculating = "Зачекайте хвилинку, статистика обраховується..."
    eng_compar_stat_for_location = lambda location, clusters: f"Comparative statistic for location {location} and clusters {', '.join(cluster.capitalize() for cluster in clusters)}"
    ua_compar_stat_for_location = lambda location, clusters: f"Порівняльна статистика для регіону {location} і кластерів {', '.join(cluster.capitalize() for cluster in clusters)}"
    eng_compar_stat_for_cluster = lambda cluster, locations: f"Comparative statistic for cluster {cluster.capitalize()} and locations {', '.join(location for location in locations)}"
    ua_compar_stat_for_cluster = lambda cluster, locations: f"Порівняльна статистика для кластеру {cluster.capitalize()} і регіонів {', '.join(location for location in locations)}"
    eng_stat_title = lambda cluster, term, location, option: f"{option.title()} statistic for cluster {cluster}, location {location} and {term} period of time"
    ua_stat_title = lambda cluster, term, location, option: f"Статистика поля {option.title()} кластеру {cluster} для регіону {location} і за період {term}."
    eng_count_option = "Comparative statistics will be calculated based on the number of vacancies for the parameters you have selected."
    ua_count_option = "Порівняльна статистика буде підрахована за кількістю вакансій за обраними вами параметрами."

    @classmethod
    def get_msg(cls, core_name, lang, *args, **kwargs):
        attribute_name = f"{lang}_{core_name}"
        msg = getattr(cls, attribute_name)
        if (args or kwargs) and isinstance(msg, Callable):
            _msg = msg(*args, **kwargs)
            return _msg
        else:
            return msg
        
    @classmethod
    def generate_title(cls, lang, cluster, term, location, option):
        title = cls.get_msg("stat_title", lang, cluster, term, location, option)
        return title

