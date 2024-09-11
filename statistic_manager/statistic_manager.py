from db_manager.mongo_manager import MongoManager

class StatisticManager:
    def __init__(self, db_manager) -> None:
        self.db_manager = db_manager

    def count_langs(self, *args):
        pass