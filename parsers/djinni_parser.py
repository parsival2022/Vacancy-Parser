import os, re
from datetime import datetime
from bs4 import BeautifulSoup
from db_manager.mongo_manager import MongoManager
from pydantic import BaseModel, Field, field_validator
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from .decorators import repeat_if_fail
from .constants import *
from .parser import Parser

class DjinniBasicVacancy(BaseModel):
    url:str = Field(min_length=10, pattern=r'https?:\/\/[^\s/$.?#].[^\s]*')
    extr_date:str = Field(default_factory=lambda: datetime.now().strftime(os.environ.get("TIMEFORMAT")))
    title:str = Field(min_length=2)
    location:str = Field(min_length=5, default="Ukraine")
    keyword:str = Field(min_length=1)
    company:str = Field(default=NOT_DEFINED, min_length=2)
    eng_level:str|list = Field(default=NOT_DEFINED, min_length=5)
    workplace_type:str = Field(default=NOT_DEFINED)
    source:str = Field(min_length=2)
    description:str = Field(min_length=10)
    completed:bool = Field(default=False)

class DjinniParser(Parser):
    source_name = "Djinni"
    base_url = "https://djinni.co"
    login_url = base_url + "/login"
    jobs_url = base_url + "/jobs/"
    headers = DJINNI_HEADERS

    english_btn = (By.XPATH, '//a[contains(@href, "/set_lang?code=en&next=%2Flogin")]')
    username_input = (By.ID, "email")
    password_input = (By.ID, "password")
    login_btn = (By.XPATH, '//button[contains(@class, "btn btn-primary btn-lg js-send-btn")]')
    login_fails = [(By.XPATH, '//div[contains(@class, "form-group has-error")]')]
    jobs_btn = (By.XPATH, '//a[contains(@href, "/my/dashboard/")]')
    all_jobs_btn = (By.XPATH, '//a[contains(@href, "/jobs/")]')
    next_page_btn = lambda self, keyword: (By.XPATH, f'//a[contains(@href, "?primary_keyword={keyword}&page={self.current_page + 1}")]')
    next_page_w_cur_btn = lambda self, keyword: (By.XPATH, f'//a[contains(@href, "?primary_keyword={keyword}&page={self.current_page}&page={self.current_page + 1}")]')
    job_upper_details = ("div", {"class": "d-flex flex-wrap align-items-center gap-1 fs-5 mb-2 text-secondary"})
    job_lower_details = ("div", {"class": "fw-medium d-flex flex-wrap align-items-center gap-1"})
    job_descr = ("span", {"class": "js-original-text d-none"})

    @repeat_if_fail(NoSuchElementException, 5)
    def perform_login(self):
        self.driver.get(self.login_url)
        self.wait(DELAY_3_6)
        self.click_on_element(*self.english_btn)
        super().perform_login()

    @repeat_if_fail(AttributeError, 5)
    def extract_job_details(self, job:BeautifulSoup):
        data = {}
        eng_levels = ['Advanced', 'Fluent', 'Beginner', 'Elementary', 'Intermediate']
        workplaces = ['Remote', 'Full Remote', 'Part-time', 'Office']
        title = job.find("a", {"class": "job-item__title-link"})
        data["url"] = self.base_url + title.get("href")
        data["title"] = title.get_text(strip=True)
        data["company"] = job.find(*self.job_upper_details).find("a").get_text(strip=True)
        data["description"] = job.find(*self.job_descr).get_text(strip=True)
        job_details =[d.get_text(strip=True) for d in job.find(*self.job_lower_details).find_all("span")] 
        for d in job_details:
            if "experience" in d:
                data["experience"] = d
            if any(d in level for level in eng_levels):
                data["eng_level"] = d
            if any(d in workplace for workplace in workplaces):
                data["workplace_type"] = d
        return data

    def perform_jobs_search(self, keywords):
        for keyword in keywords:
            self.click_on_element(*self.jobs_btn)
            self.wait(DELAY_5_10)
            self.current_page = 1
            j_url = self.base_url + f"/jobs/?primary_keyword={keyword}"
            self.driver.get(j_url)
            while self.current_page:
                try:
                    self.wait(DELAY_5_10)
                    j_soup = self.parse_page()
                    jobs = j_soup.find("main").find_all("ul")[0].find_all("li", {"class": "mb-5"})
                    for job in jobs:
                        data = {"keyword": keyword, "source": self.source_name}
                        data.update(self.extract_job_details(job))
                        if not self.db_manager.check_if_exist({"url": data["url"]}):
                            self.db_manager.create_document(data, DJ_BASE_VACANCY)
                    self.wait(DELAY_5_10)
                    try:
                        self.wait(3)
                        self.click_on_element(*self.next_page_btn(keyword))
                        self.current_page += 1
                    except NoSuchElementException:
                        self.click_on_element(*self.next_page_w_cur_btn(keyword))
                        self.current_page += 1
                except (NoSuchElementException, ElementNotInteractableException):
                    self.current_page = None

    @repeat_if_fail(NoSuchElementException, 5)
    def parsing_suite(self, keywords):
        self.perform_login()
        self.perform_jobs_search(keywords)
        self.driver.quit()

PYTHON = "Python"
JAVA = "Java"
JS = "JavaScript"
CPP = "CPP"

DJ_BASE_VACANCY = "base_vacancy"

DJ_MODELS = {DJ_BASE_VACANCY: DjinniBasicVacancy}
DJ_COLLECTION = "Vacancies"
DJ_KEYWORDS = (PYTHON, JAVA, JS, CPP)
                

if __name__ == "__main__":
    db_manager = MongoManager(DJ_COLLECTION, DJ_MODELS)
    djinni = DjinniParser(db_manager=db_manager)
    djinni.parsing_suite(DJ_KEYWORDS)