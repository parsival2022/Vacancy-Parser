import os
import pymongo
from pymongo.errors import PyMongoError
from pydantic import BaseModel
from dotenv import load_dotenv
from db_manager.errors import (NoDatabaseInitialized, 
                               NoDatabaseCredentialsProvided,
                               NoModelsRegistered)

load_dotenv()

class MongoManager:
    DB:pymongo.MongoClient|None = None

    def __init__(self, collection_name:str, models:dict|None=None) -> None:
        if self.DB is not None:
            self.db = self.DB[collection_name]
        else:
            raise NoDatabaseInitialized()
        self.models = models

    @classmethod
    def __init_database__(cls, conn_str:str|None=None, db_name:str|None=None) -> None:
        if cls.DB:
            print("Database already exists")
            return True
        
        connection_string = conn_str or os.environ.get('MONGO_CONNECTION_STRING')
        db_name = db_name or os.environ.get("MONGO_DB_NAME")

        if not connection_string or not db_name:
            raise NoDatabaseCredentialsProvided()
        try:
            CLIENT = pymongo.MongoClient(connection_string, maxPoolSize=400)
            cls.DB = CLIENT[db_name]
        except PyMongoError as e:
            print(e)
        print(f"Connected to MongoDB database: {db_name}")

    def register_models(self, models:dict):
        self.models = models

    def id_to_string(self, document):
        """Changes _id field of returned document from ObjectId to string."""
        try:
            document['_id'] = str(document['_id'])
        except (KeyError, TypeError):
            pass
        return document

    def to_list(self, cursor):
        """Returns the list of objects from the PyMongo cursor."""

        res = []
        for el in cursor:
            res.append(self.id_to_string(el))
        return res

    def check_if_exist(self, query):
        """Checks if the document that matching to the given filter exist."""
        res = self.db.count_documents(query)
        if not res:
            return False
        return True

    def get_document(self, query, **kwargs):
        """Retrieves the document from the database."""
        document = self.db.find_one(query, **kwargs)
        return self.id_to_string(document)

    def get_documents(self, query, **kwargs):
        """Retrieves the multiple documents from the database."""
        document = self.db.find(query, **kwargs)
        return self.to_list(document)

    def get_and_sort_documents(self, query, sort_options=None, **kwargs):
        """Retrieves the multiple documents from the database and sorts it.
           Args for sorting: pass as a list with this args:
               - key_or_list: a single key or a list of (key, direction)
                 pairs specifying the keys to sort on
               - direction (optional): only used if key_or_list is a single key,
                 if not given ASCENDING is assumed
        """
        if sort_options is None:
            sort_options = []
        documents = self.db.find(query, **kwargs).sort(*sort_options)
        return self.to_list(documents)

    def create_document(self, data, type_key) -> str | None:
        """Creates document. Key is needed to use proper model for validation."""
        if not self.models:
            raise NoModelsRegistered
        model:BaseModel = self.models[type_key]
        validated_model = model.model_validate(data)
        res = self.db.insert_one(validated_model.model_dump())
        return str(res.inserted_id) if res.acknowledged else None

    def update_document(self, query, update, **kwargs):
        """Updates the document."""
        document = self.db.find_one_and_update(query, update, return_document=pymongo.ReturnDocument.AFTER, **kwargs)
        return self.id_to_string(document)

    def delete_document(self, query, **kwargs):
        """Delete the document from database."""
        res = self.db.find_one_and_delete(query, **kwargs)
        return self.id_to_string(res)

    def delete_from_document(self, query, delete_part, **kwargs):
        """Deletes the specific part of the document."""
        res = self.db.update_one(query, delete_part, **kwargs)
        if res.modified_count == 0:
            return None
        return res
    
    def delete_documents(self, query, **kwargs):
        try:
            res = self.db.delete_many(query, **kwargs)
            return res.deleted_count
        except PyMongoError:
            return None