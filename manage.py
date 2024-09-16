import click, logging, asyncio, sys
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
from statistic_manager.statistic_manager import StatisticManager as SM
from bot.bot import main


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

@cli.command()
def get_chart():
    db_m = MongoManager(LN_COLLECTION)
    sm = SM(db_manager=db_m)
    stats = sm.get_levels_for_clusters()
    print(stats)
    sm.generate_pie_chart(stats)

@cli.command()
def start_bot():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

if __name__ == "__main__":
    cli()
