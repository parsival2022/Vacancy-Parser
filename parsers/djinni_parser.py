import requests, time
from .parser import Parser
from bs4 import BeautifulSoup
from db_manager.mongo_manager import MongoManager
from db_manager.models import Vacancy, VacancyURL
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, WebDriverException
from selenium.webdriver.common.keys import Keys
from .decorators import repeat_if_fail
from .constants import *

class DjinniParsers(Parser):
    base_url = "https://djinni.co"
    login_url = base_url + "/login?from=frontpage_main"
    headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "content-length": 130,
    "content-type": "application/x-www-form-urlencoded",
    "cookie": "csrftoken=yj3MmtwsJ3VVtncxu7ZHjxWYPLc5Hl28; _pk_ref.1.df23=%5B%22%22%2C%22%22%2C1725714952%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_id.1.df23=98597ef4234fa406.1725714952.; _pk_ses.1.df23=1; intercom-id-cg6zpunb=c516cd9c-fefd-47d7-a544-58278835146c; intercom-session-cg6zpunb=; intercom-device-id-cg6zpunb=e1e52c77-b50e-49d8-aafd-05435aec7fed; sessionid=.eJwVzMEOgjAMBuB32VWFDjexewVvRs9kjjFJYCVjhBjCu1tO7d98fzfhaIk5_RpHrRdGvB9PcRYzLckd8ZvzNJuyXNe1CERh8IWjsWRiI0VhNtG3zBDqT4eI8MFWwU0hSq30VVbaouIre5e8zf7AFVTqAniB-iWvRmqjodA3uCOcAAwA426wYebv-857opFbPGKebPDNaPvIJlBu0jJ4dp0dZr__AYAcPSU:1smvI9:4fPK978aOYghy4KMLtUow9DOXgK6mAZMta3R-M85UI4",
    "host": "djinni.co",
    "origin": "https://djinni.co",
    "referer": "https://djinni.co/login?from=frontpage_main",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
    }


    username_input = (By.ID, "email")
    password_input = (By.ID, "password")
    login_btn = (By.XPATH, '//button[text()="Log In"]')
    login_fail = (By.XPATH, '//div[contains(@class, "form-group has-error")]')
    jobs_btn = (By.XPATH, '//a[contains(@href, "/my/dashboard/")]')
    all_jobs_btn = (By.XPATH, '//a[contains(@href, "/jobs/")]')
    

    @repeat_if_fail(NoSuchElementException, 5)
    def get_jobs(self):
        cookies = self.driver.get_cookies()
        url = self.base_url + "/jobs/"
        jobs = self.make_get_request(url=url, soup=True, cookies=cookies)