class NoDatabaseInitialized(Exception):
    message = """
           No database was initialized. Please call method __init_database__ of the Mongo Manager.
           Make sure that parameters MONGO_CONNECTION_STRING and MONGO_DB_NAME exists in your .env file.
              """

class NoDatabaseCredentialsProvided(Exception):
    message = """
               No credentials provided through cli options or defined in .env file. Please provide required credentials
               or define MONGO_CONNECTION_STRING and MONGO_DB_NAME in your .env file.
              """
    
class NoModelsRegistered(Exception):
        message = """
               No models were registered in class inctanse. Please call 
              """