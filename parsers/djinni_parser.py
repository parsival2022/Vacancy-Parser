import requests, time
from .parser import Parser
from bs4 import BeautifulSoup
from db_manager.mongo_manager import MongoManager
from db_manager.models import Vacancy, VacancyURL
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from .decorators import repeat_if_fail
from .constants import *

class DjinniParsers(Parser):

    def perform_login(self):
        pass