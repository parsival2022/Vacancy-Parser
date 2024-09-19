from abc import ABC

class DatabaseManager(ABC):
    @classmethod
    def __init_database__(cls, *args, **kwargs) -> None:
        """Performig connection to database."""  
    
    def aggregate(self, *args, **kwargs):
        """Performing pipeline of operations"""

    def check_if_exist(self, *args, **kwargs):
        """Checking if the record exists"""
    
    def count(self, *args, **kwargs):
        """Counts records in the database"""

    def get_one(self, *args, **kwargs):
        """Gets single record"""

    def get_many(self, *args, **kwargs):
        """Gets multiply records"""

    def get_and_sort_records(self, *args, **kwargs):
        """Gets multiply records and sort it"""

    def create_one(self, *args, **kwargs):
        """Creates single record"""

    def update_one(self, *args, **kwargs):
        """Updates single record"""

    def update_many(self, *args, **kwargs):
        """Updates multiply record"""

    def delete_one(self, *args, **kwargs):
        """Deletes one record"""
    
    def delete_many(self, *args, **kwargs):
        """Deletes multiply records"""