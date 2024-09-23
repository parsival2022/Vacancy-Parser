from db_manager.mongo_manager import MongoManager
from pydantic import BaseModel, Field

SESSION = "Session"

class SessionModel(BaseModel):
    user_id:int
    lang:str|None = Field(default=None)

class Session:
    session_manager = MongoManager(SESSION, {SESSION: SessionModel})

    def __init__(self, extractable):
        self._session = self.get_session(extractable)
        if self._session:
            self.lang = self._session.get("lang")
            self.user_id = self._session.get("user_id")

    def exists(self):
        return self._session is not None

    def get_session(self, extractable) -> dict | None:
        user_id = extractable.from_user.id
        user_session = self.session_manager.get_one({"user_id": user_id})
        return user_session
    
    def change_lang(self, lang):
        self.session_manager.update_one({"user_id": self.user_id}, {"$set": {"lang": lang}})

    def start_query(self):
        self.session_manager.update_one({"user_id": self.user_id}, {"$set": {"query": {}}})

    def get_query(self):
        query = self._session.get("query")
        return query
    
    def add_to_query(self, k, v):
        self.session_manager.update_one({"user_id": self.user_id}, {"$set": {f"query.{k}": v}})
    
    def push_to_query(self, k, v):
        self.session_manager.update_one({"user_id": self.user_id}, {"$push": {f"query.{k}": v}})

    def clear(self):
        self.session_manager.update_one({"user_id": self.user_id}, {"$unset": {"query": ""}})

    @classmethod
    def register_user(cls, extractable, data={}):
        data["user_id"] = extractable.from_user.id
        if not cls.session_manager.check_if_exist({"user_id": data["user_id"]}):
            cls.session_manager.create_one(data, SESSION)
        return True