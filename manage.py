import click, logging, asyncio, sys, os
from db_manager.mongo_manager import MongoManager
from parsers.linkedin_parser import (LinkedinParser,  
                                     LN_MODELS, 
                                     LN_LOCATIONS,
                                     LN_KEYWORDS)
from parsers.djinni_parser import (DjinniParser,
                                   DJ_MODELS,
                                   DJ_KEYWORDS)
from clusters import *
from statistic_manager.statistic_manager import StatisticManager as SM
from bot.bot import main

COLLECTION = os.getenv("MONGO_DB_NAME")

@click.group()
def cli():
    pass

@cli.command()
def launch_linkedin_parsing():
    db_manager = MongoManager(COLLECTION, LN_MODELS)
    linkedin = LinkedinParser(db_manager=db_manager)
    linkedin.parsing_suite(LN_LOCATIONS, LN_KEYWORDS)

@cli.command()
def launch_djinni_parsing():
    db_manager = MongoManager(COLLECTION, DJ_MODELS)
    djinni = DjinniParser(db_manager=db_manager)
    djinni.parsing_suite(DJ_KEYWORDS)

@cli.command
def get_chart():
    db_manager = MongoManager(COLLECTION)
    sm = SM(db_manager)
    sm.get_stats_chart("technologies", PYTHON, y_label="Technologies")

@cli.command()
def start_bot():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

if __name__ == "__main__":
    cli()
