from pydantic import Field
from requests.exceptions import ConnectionError
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, WebDriverException
from clusters import *
from models import BasicVacancyModel
from .decorators import repeat_if_fail, ignore_if_fail, execute_if_fail
from .parser import Parser

class DjinniBasicVacancy(BasicVacancyModel):
    location:str = Field(min_length=5, default="Ukraine")

class DjinniParser(Parser):
    source_name = "Djinni"
    base_url = "https://djinni.co"
    login_url = base_url + "/login"
    jobs_url = base_url + "/jobs/"

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
    job_extra_info = ("ul", {"id": "job_extra_info"})

    @repeat_if_fail(NoSuchElementException, 5)
    def perform_login(self):
        self.driver.get(self.login_url)
        self.wait((3, 6))
        self.click_on_element(*self.english_btn)
        super().perform_login()

    @repeat_if_fail(AttributeError, 5)
    def extract_job_details(self, job):
        data = {}
        eng_levels = ['Advanced', 'Fluent', 'Beginner', 'Elementary', 'Intermediate']
        workplaces = ['Remote', 'Full Remote', 'Office', 'Hybrid-Remote']
        employment_types = ['Part-time']
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
            if any(d in emp_type for emp_type in employment_types):
                data["employment_type"] = d
        return data
    
    def perform_jobs_search(self, keywords):
        for keyword in keywords:
            self.click_on_element(*self.jobs_btn)
            self.wait((5, 10))
            self.current_page = 1
            j_url = self.base_url + f"/jobs/?primary_keyword={keyword}"
            self.driver.get(j_url)
            while self.current_page:
                try:
                    self.wait((5, 10))
                    j_soup = self.parse_page()
                    jobs = j_soup.find("main").find_all("ul")[0].find_all("li", {"class": "mb-5"})
                    for job in jobs:
                        data = {"keyword": keyword, "source": self.source_name}
                        data.update(self.extract_job_details(job))
                        if not self.db_manager.check_if_exist({"url": data["url"]}):
                            self.db_manager.create_one(data, DJ_BASE_VACANCY)
                    self.wait((5, 10))
                    try:
                        self.wait(3)
                        self.click_on_element(*self.next_page_btn(keyword))
                        self.current_page += 1
                    except NoSuchElementException:
                        self.click_on_element(*self.next_page_w_cur_btn(keyword))
                        self.current_page += 1
                except (NoSuchElementException, ElementNotInteractableException):
                    self.current_page = None

    @execute_if_fail((IndexError, TypeError, AttributeError), lambda: None)
    def extract_skills(self, soup):
        skills:str = soup.find(*self.job_extra_info).find_all("li", {"class": "mb-1"})[1].get_text(strip=True)
        return [skill.strip() for skill in skills.split(",")]


    @repeat_if_fail((WebDriverException, ElementNotInteractableException), 7)
    @ignore_if_fail(ElementNotInteractableException)
    def perform_job_parsing(self, keywords):
        for keyword in keywords:
            urls = self.db_manager.get_many({"keyword": keyword, "completed": False})
            jobs_pg = self.driver.current_window_handle
            for url in urls:
                self.driver.switch_to.new_window('tab')
                self.driver.get(url["url"])
                self.wait((5, 10))
                soup = self.parse_page()
                skills = self.extract_skills(soup)
                if skills:
                    self.db_manager.update_one({"url": url["url"]}, {"$set": {"skills": skills, "completed": True}})
                self.driver.close()
                self.driver.switch_to.window(jobs_pg)
                # self.click_on_element(*self.all_jobs_btn)
                self.wait((8, 10))

    @repeat_if_fail((NoSuchElementException, ConnectionError), 5)
    def parsing_suite(self, keywords):
        self.perform_login()
        self.perform_jobs_search(keywords)
        self.perform_job_parsing(keywords)
        self.driver.quit()

PYTHON_KWD = CLUSTERS[PYTHON]["keywords"]["dj_kw"]
JAVA_KWD = CLUSTERS[JAVA]["keywords"]["dj_kw"]
JS_KWD = CLUSTERS[JS]["keywords"]["dj_kw"]
CPP_KWD = CLUSTERS[CPP]["keywords"]["dj_kw"]
PHP_KWD = CLUSTERS[PHP]["keywords"]["dj_kw"]
GO_KWD = CLUSTERS[GO]["keywords"]["dj_kw"]

DJ_BASE_VACANCY = "base_vacancy"

DJ_MODELS = {DJ_BASE_VACANCY: DjinniBasicVacancy}
DJ_COLLECTION = "Vacancies"
DJ_KEYWORDS = (PYTHON_KWD, JAVA_KWD, JS_KWD, CPP_KWD, PHP_KWD, GO_KWD)
                