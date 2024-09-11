import click
from db_manager.mongo_manager import MongoManager
from parsers.linkedin_parser import (LinkedinParser, 
                                     LN_COLLECTION, 
                                     LN_MODELS, 
                                     LN_LOCATIONS,
                                     LN_KEYWORDS)
from parsers.djinni_parser import (DjinniParser,
                                   DJ_COLLECTION,
                                   DJ_MODELS,
                                   DJ_KEYWORDS)
from parsers.constants import *


@click.group()
def cli():
    pass

@cli.command()
def launch_linkedin_parsing():
    db_manager = MongoManager(LN_COLLECTION, LN_MODELS)
    linkedin = LinkedinParser(db_manager=db_manager)
    linkedin.parsing_suite(LN_LOCATIONS, LN_KEYWORDS)

@cli.command()
def launch_djinni_parsing():
    db_manager = MongoManager(DJ_COLLECTION, DJ_MODELS)
    djinni = DjinniParser(db_manager=db_manager)
    djinni.parsing_suite(DJ_KEYWORDS)

if __name__ == "__main__":
    cli()
