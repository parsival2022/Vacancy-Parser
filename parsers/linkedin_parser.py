import re
from .parser import Parser
from bs4 import BeautifulSoup
from db_manager.mongo_manager import MongoManager
from db_manager.models import BasicVacancy, Vacancy
from pydantic import ValidationError
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from .decorators import repeat_if_fail
from .constants import *

VACANCY = "vacancy"
BASIC_VACANCY = "vacancy_url"

class LinkedinParser(Parser):
    base_url = "https://www.linkedin.com"
    login_url = base_url + "/checkpoint/lg/login-submit"
    current_page = None

    jobs_button = (By.CSS_SELECTOR, '[href="https://www.linkedin.com/jobs/?"]')
    search_loc_input = (By.XPATH, "//input[contains(@id, 'jobs-search-box-location-id-ember')]")
    search_kw_input = (By.XPATH, "//input[contains(@id, 'jobs-search-box-keyword-id-ember')]")
    search_btn = (By.XPATH, "//button[contains(@class, 'jobs-search-box__submit-button')]")
    next_page_numbered = lambda self: (By.CSS_SELECTOR, f'[data-test-pagination-page-btn="{self.current_page + 1}"]')
    next_page_dots = (By.XPATH, '//li[contains(@class, "artdeco-pagination__indicator")]/button/span[text()="…"]')
    skills_btn = (By.XPATH, '//span[text()="Show qualification details"]')
    job_company = ("company", ("div", {"class": re.compile(r"company-name")}))
    job_title = ("title", ("div", {"class": re.compile(r"job-title")}))
    job_description = ("description", ("div", {"class": re.compile(r"jobs-description-content__text")}))
    job_primary = (By.XPATH, '//div[contains(@class,"unified-top-card__primary-description-container")]')
    job_skills = (By.XPATH, '//ul[contains(@class, "job-details-skill-match-status-list")]')
    job_insights = (By.XPATH, '//li[contains(@class, "job-insight--highlight")]')


    @repeat_if_fail(NoSuchElementException, DELAY_5)
    def perform_login(self):
        self.driver.get(self.init_url)
        self.wait(DELAY_10_15)
        self.fill_input_element(By.ID, "username", self.username)
        self.fill_input_element(By.ID, "password", self.password)
        self.wait(DELAY_4_8)
        self.driver.find_element(By.CSS_SELECTOR, '[data-litms-control-urn="login-submit"]').click()
        try:
            fail_usn = self.driver.find_element(By.ID, "error-for-username")
            fail_psw = self.driver.find_element(By.ID, "error-for-password")
            self.driver.quit()
        except NoSuchElementException: 
            pass
        self.wait(DELAY_15)

    @repeat_if_fail(NoSuchElementException, DELAY_5)
    def insert_search_params(self, kw, lc):
        self.click_on_element(*self.jobs_button)
        self.wait(DELAY_10_15)
        self.fill_input_element(*self.search_loc_input, lc)
        self.wait(DELAY_5_10)
        self.fill_input_element(*self.search_kw_input, kw)
        self.wait(DELAY_8_10)
        try:
            self.click_on_element(*self.search_btn)
        except ElementNotInteractableException:
            self.fill_input_element(*self.search_kw_input, Keys.ENTER)
        self.wait(DELAY_8_10)
        location_txt = self.driver.find_element(*self.search_loc_input).get_attribute("data-job-search-box-location-input-trigger")
        if not lc == location_txt:
            self.fill_input_element(*self.search_loc_input, lc)
            self.wait(DELAY_3)
            self.fill_input_element(*self.search_loc_input, Keys.ENTER)
            self.wait(DELAY_8_10)

    @repeat_if_fail(NoSuchElementException, DELAY_10)
    def perform_jobs_search(self, search_str, loc):
        self.current_page = 1
        self.insert_search_params(search_str, loc)
        while self.current_page:
            try:
                self.wait(DELAY_15)
                raw_jobs = self.soup_two_level_extr_all('ul', {'class': "scaffold-layout__list-container"}, 'li', {})
                for job in raw_jobs:
                    try:
                        j_id = job['data-occludable-job-id']
                        j_url = f"{self.base_url}/jobs/view/{j_id}/"
                        self.append_to_file(f"{self.source_name}_{loc}_{search_str}_urls.txt", j_url)
                        if not self.db_manager.check_if_exist({"url": j_url}):
                            data = {"url": j_url, "location": loc, "keyword": search_str, "source":self.source_name}
                            self.db_manager.create_document(data, BASIC_VACANCY)
                    except KeyError: continue
                self.wait(DELAY_4_8)
                try:
                    self.click_on_element(*self.next_page_numbered())
                    self.current_page += 1
                except NoSuchElementException:
                    self.click_on_element(*self.next_page_dots)
                    self.current_page += 1
            except (NoSuchElementException, ElementNotInteractableException):
                self.current_page = None

    def perform_job_parsing(self, search_str, loc):
        def create_key(k, v, i):
            try:
                data[k] = v[i]
            except IndexError:
                pass
        
        urls = self.db_manager.get_documents({"location": loc, "keyword": search_str})
        feed = self.driver.current_window_handle
        for url in urls:
            self.driver.switch_to.new_window('tab')
            self.driver.get(url["url"])
            self.wait(DELAY_15)
            soup:BeautifulSoup = self.parse_page()
            data = self.soup_extract_text_suite(soup, 
                                            self.job_title, 
                                            self.job_company,
                                            self.job_description)
            job_primary = self.driver.find_element(*self.job_primary).text.split("·")
            job_insights = self.driver.find_element(*self.job_insights).text.split("·")
            create_key("exact_location", job_primary, 0)
            create_key("workplace_type", job_insights, 0)
            create_key("employment_type", job_insights, 1)
            create_key("level", job_insights, 2)
            self.click_on_element(*self.skills_btn)
            self.wait(DELAY_7)
            try:
                job_skills = self.driver_two_level_extr_all(*self.job_skills, By.TAG_NAME, "li")
                skills = []
                for skill in job_skills:
                    sk = skill.text.split(" ")[0]
                    skills.append(sk.replace("\nAdd", ""))
                data["skills"] = skills
            except NoSuchElementException:
                pass
            print(data)
            try:
                vacancy = self.db_manager.models[VACANCY].model_validate(data)
                self.db_manager.update_document({"url": url}, {"$set": vacancy.model_dump()})
            except ValidationError:
                pass
            self.driver.close()
            self.driver.switch_to.window(feed)
            
            
    def parsing_suite(self, locations, keywords):           
        self.perform_login()
        
        for location in locations:
            for keyword in keywords:
                self.wait(DELAY_10_15)
                # self.perform_jobs_search(keyword, location)
                self.perform_job_parsing(keyword, location)
                
            

if __name__ == "__main__":
    locations = (USA, EU)
    keywords = (PYTHON, JAVA, JS) 
    db_manager = MongoManager("Vacancies", {VACANCY: Vacancy, BASIC_VACANCY: BasicVacancy})
    linkedin = LinkedinParser("https://www.linkedin.com/login/uk", 
                              db_manager, 
                              "Linkedin", 
                              use_driver=True,
                              use_request=True)
    linkedin.parsing_suite(locations, keywords)
