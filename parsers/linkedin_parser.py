import os
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, ValidationError
from selenium.common.exceptions import (NoSuchElementException, 
                                        ElementNotInteractableException, 
                                        ElementClickInterceptedException,
                                        WebDriverException,
                                        InvalidSessionIdException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from clusters import *
from .decorators import repeat_if_fail, execute_if_fail
from .models import BasicVacancyModel
from .parser import Parser

load_dotenv()

class BasicVacancy(BaseModel):
    url:str = Field(min_length=10, pattern=r'https?:\/\/[^\s/$.?#].[^\s]*')
    extr_date:str = Field(default_factory=lambda: datetime.now().strftime(os.environ.get("TIMEFORMAT")))
    location:str = Field(min_length=5)
    keyword:str = Field(min_length=1)
    source:str = Field(min_length=2)
    completed:bool = Field(default=False)
    
    @field_validator('location')
    def validate_location(cls, value):
        choices = {EU, UA, USA, UK}
        if value not in choices:
            raise ValueError(f"Invalid value for location. Allowed values are {choices}.")
        return value

    
class Vacancy(BasicVacancyModel):
    completed:bool = Field(default=True)
    exact_location:str = Field(min_length=2)

    @field_validator('completed')
    def validate_completed(cls, completed):
        if not completed:
            return True

class LinkedinParser(Parser):
    source_name = "Linkedin"
    base_url = "https://www.linkedin.com"
    login_url = "https://www.linkedin.com/login/uk"
    current_page = None
    
    username_input = (By.ID, "username")
    password_input = (By.ID, "password")
    login_btn = (By.XPATH, '//button[contains(@data-litms-control-urn, "login-submit")]')
    login_fails = ((By.ID, "error-for-username"), (By.ID, "error-for-password"))
    jobs_button = (By.CSS_SELECTOR, '[href="https://www.linkedin.com/jobs/?"]')
    search_loc_input = (By.XPATH, "//input[contains(@id, 'jobs-search-box-location-id-ember')]")
    search_kw_input = (By.XPATH, "//input[contains(@id, 'jobs-search-box-keyword-id-ember')]")
    search_btn = (By.XPATH, "//button[contains(@class, 'jobs-search-box__submit-button')]")
    next_page_numbered = lambda self: (By.CSS_SELECTOR, f'[data-test-pagination-page-btn="{self.current_page + 1}"]')
    next_page_dots = (By.XPATH, '//li[contains(@class, "artdeco-pagination__indicator")]/button/span[text()="…"]')
    skills_btn = (By.XPATH, '//span[text()="Show qualification details"]')
    job_company = (By.XPATH, '//div[contains(@class, "company-name")]')
    job_title = (By.XPATH, '//div[contains(@class, "top-card__job-title")]')
    job_description = (By.ID, 'job-details')
    job_primary = (By.XPATH, '//div[contains(@class,"unified-top-card__primary-description-container")]')
    job_skills = (By.XPATH, '//ul[contains(@class, "job-details-skill-match-status-list")]')
    job_insights = (By.XPATH, '//li[contains(@class, "job-insight--highlight")]')

    @repeat_if_fail(NoSuchElementException, 5)
    def insert_search_params(self, kw, lc):
        self.click_on_element(*self.jobs_button)
        self.wait((10, 15))
        self.fill_input_element(*self.search_loc_input, lc)
        self.wait((5, 10))
        self.fill_input_element(*self.search_kw_input, kw)
        self.wait((8, 10))
        try:
            self.click_on_element(*self.search_btn)
        except ElementNotInteractableException:
            self.fill_input_element(*self.search_kw_input, Keys.ENTER)
        self.wait((8, 10))
        location_txt = self.driver.find_element(*self.search_loc_input).get_attribute("data-job-search-box-location-input-trigger")
        if not lc == location_txt:
            self.fill_input_element(*self.search_loc_input, lc)
            self.wait(3)
            self.fill_input_element(*self.search_loc_input, Keys.ENTER)
            self.wait((8, 10))

    @repeat_if_fail(WebDriverException, 7)
    def perform_jobs_search(self, search_str, loc):
        self.current_page = 1
        self.insert_search_params(search_str, loc)
        while self.current_page:
            try:
                self.wait(15)
                raw_jobs = self.soup_two_level_extr_all('ul', {'class': "scaffold-layout__list-container"}, 'li', {})
                for job in raw_jobs:
                    try:
                        j_id = job['data-occludable-job-id']
                        j_url = f"{self.base_url}/jobs/view/{j_id}/"
                        if not self.db_manager.check_if_exist({"url": j_url}):
                            data = {"url": j_url, "location": loc, "keyword": search_str, "source":self.source_name}
                            self.db_manager.create_document(data, LN_BASIC_VACANCY)
                    except KeyError: continue
                self.wait((4, 8))
                try:
                    self.click_on_element(*self.next_page_numbered())
                    self.current_page += 1
                except NoSuchElementException:
                    self.click_on_element(*self.next_page_dots)
                    self.current_page += 1
            except (NoSuchElementException, ElementNotInteractableException):
                self.current_page = None

    @repeat_if_fail(NoSuchElementException, 5)
    def extract_job_details(self):
        currency_signs = ['$', '€', '£', '¥', '₹', '₴']
        levels = ['Internship', 'Entry level', 'Associate', 'Mid-Senior', 'Director', 'Executive']
        workplaces = ['On-site', 'Hybrid', 'Remote']
        employment_types = ["Full-time", "Contract", "Volunteer", "Part-time", "Temporary", "Internship", "Other"]
        data = {}

        job_primary = self.driver.find_element(*self.job_primary).text.split("·")[0]
        data["exact_location"] = job_primary
        job_insights = self.driver.find_element(*self.job_insights).text.split("·")[0].split(" ")
        for s in job_insights:
            if any(sign in s for sign in currency_signs):
                data["salary"] = s
            if any(_type in s for _type in levels):
                data["level"] = s
            if any(_type in s for _type in workplaces):
                data["workplace_type"] = s
            if any(_type in s for _type in employment_types):
                data["employment_type"] = s
        return data
    
    @repeat_if_fail(ElementClickInterceptedException, 5)
    def extract_job_info(self):
        data = {}
        data["description"] = self.driver.find_element(*self.job_description).text
        data["title"] = self.driver.find_element(*self.job_title).find_element(By.TAG_NAME, 'h1').text
        data["company"] = self.driver.find_element(*self.job_company).text
        return data
    
    @execute_if_fail(ElementClickInterceptedException, lambda: {"skills": []})
    def extract_job_skills(self):
        data = {}
        skills = []
        self.click_on_element(*self.skills_btn)
        self.wait(7)
        job_skills = self.driver_two_level_extr_all(*self.job_skills, By.TAG_NAME, "li") 
        if len(job_skills) > 0:
            for skill in job_skills:
                sk = skill.text
                skills.append(sk.replace("\nAdd", ""))
        data["skills"] = skills
        return data

    @repeat_if_fail(WebDriverException, 7)
    def perform_job_parsing(self, search_str, loc):
        urls:list[dict] = self.db_manager.get_many({"location": loc, "keyword": search_str, "completed": False})
        feed = self.driver.current_window_handle

        for url in urls:
            self.driver.switch_to.new_window('tab')
            self.driver.get(url["url"])
            self.wait(15)
            try:
                el = self.driver.find_element(By.ID, "jobs-feed-discovery-module-0")
                self.driver.close()
                self.driver.switch_to.window(feed)
                return
            except NoSuchElementException:
                pass
            try:
                url.update(self.extract_job_info())
                url.update(self.extract_job_details())
                url.update(self.extract_job_skills())
            except NoSuchElementException:
                pass 
            try: 
                vacancy = self.db_manager.models[LN_VACANCY].model_validate(url)
                self.db_manager.update_one({"url": url["url"]}, {"$set": vacancy.model_dump()})
            except ValidationError:
                pass
            self.driver.close()
            self.driver.switch_to.window(feed)
            self.click_on_element(*self.jobs_button)
            self.wait((3, 6))
            
    @repeat_if_fail(InvalidSessionIdException, 60)
    def parsing_suite(self, locations, keywords):           
        self.perform_login()
        for location in locations:
            for keyword in keywords:
                self.wait((10, 15))
                # self.perform_jobs_search(keyword, location)
                self.perform_job_parsing(keyword, location)
        self.driver.quit()

LN_VACANCY = "vacancy"
LN_BASIC_VACANCY = "basic_vacancy"

PYTHON_KWL = CLUSTERS[PYTHON]["keywords"]["ln_kw"]
JAVA_KWL = CLUSTERS[JAVA]["keywords"]["ln_kw"]
JS_KWL = CLUSTERS[JS]["keywords"]["ln_kw"]
CPP_KWL = CLUSTERS[CPP]["keywords"]["ln_kw"]

EU = "European Union"
USA = "United States"
UA = "Ukraine"
UK = "United Kingdom"

LN_MODELS = {LN_VACANCY: Vacancy, LN_BASIC_VACANCY: BasicVacancy} 
LN_LOCATIONS = (UA, USA, EU, UK) 
LN_KEYWORDS = (PYTHON_KWL, JAVA_KWL, JS_KWL, CPP_KWL)

