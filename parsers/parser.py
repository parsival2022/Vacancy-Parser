import os, time, json, random, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from .decorators import repeat_if_fail

load_dotenv()
HTTPS = "https"
HTTP = "http"

class Parser:
    source_name = "base_parser"
    prefixes = {HTTPS: "https://",
                HTTP: "http://"}
    headers = {}
    current_page = None
    base_url = "https://www.example.com"
    login_url = None
    
    # elements that are used in default perform_login method
    username_input = (By.ID, "email")
    password_input = (By.ID, "password")
    login_btn = (By.XPATH, '//button[text()="Log In"]')
    login_fails = ((By.XPATH, '//div[contains(@class, "form-group has-error")]'))

    def __init__(self, db_manager, keywords, locations=None, init_url=None, use_driver=True, use_request=False) -> None:
        self.init_url = init_url if init_url else self.login_url
        self.db_manager = db_manager
        self.username = os.environ.get(self.source_name.upper().replace(" ", "_") + "_USERNAME") or None
        self.password = os.environ.get(self.source_name.upper().replace(" ", "_") + "_PASSWORD") or None
        self.keywords: list[str] = keywords
        self.locations: list[str] = locations
        #self.proxies = proxies
        if use_request:
            self.session = requests.Session()
        if use_driver:
            self.driver:webdriver.Chrome = self.create_driver()

    @repeat_if_fail(requests.exceptions.ChunkedEncodingError, 6)
    def create_driver(self) -> webdriver.Chrome: 
        options = Options()
        options.add_argument("enable-automation")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-gpu-compositing")
        options.add_argument("--headless")
        # options.add_argument("--disable-software-rasterizer")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webrtc")
        # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        return webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="128.0.6613.114").install()), options=options)
   
    def wait(self, t):
        try:
            _t = random.randint(*t)
        except TypeError:
            _t = t
        time.sleep(_t)
    
    @repeat_if_fail([TypeError, AttributeError], 5)
    def parse_page(self) -> BeautifulSoup:
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup
    
    @repeat_if_fail([TypeError, AttributeError], 5)
    def soup_two_level_extr_all(self, f_lvl_tag, f_lvl_attrs, s_lvl_tag, s_lvl_attrs, page=None) -> list:
        soup:BeautifulSoup = self.parse_page() if not page else page
        first_level = soup.findChild(f_lvl_tag, f_lvl_attrs)
        second_level = first_level.find_all(s_lvl_tag, s_lvl_attrs)
        return second_level
    
    @repeat_if_fail(NoSuchElementException, 5)
    def driver_two_level_extr_all(self, f_lvl_by, f_lvl_attrs, s_lvl_by, s_lvl_attrs):
        res = self.driver.find_element(f_lvl_by, f_lvl_attrs).find_elements(s_lvl_by, s_lvl_attrs)
        return res
    
    @repeat_if_fail(NoSuchElementException, 7)
    def click_on_element(self, by, value):
        self.driver.find_element(by, value).click()

    @repeat_if_fail(NoSuchElementException, 5)
    def fill_input_element(self, by, input, keys):
        input = self.driver.find_element(by, input)
        input.clear()
        input.send_keys(keys)

    @repeat_if_fail(NoSuchElementException, 5)
    def perform_login(self):
        lu = self.login_url if self.login_url else self.init_url
        self.driver.get(lu)
        self.wait((10, 15))
        self.fill_input_element(*self.username_input, self.username)
        self.fill_input_element(*self.password_input, self.password)
        self.wait((4, 8))
        self.click_on_element(*self.login_btn)
        try:
            for fail in self.login_fails:
                self.driver.find_element(*fail)
            self.driver.quit()
        except NoSuchElementException: 
            pass
        self.wait(15)

    def parsing_suite(self):
        raise NotImplementedError

    def perform_jobs_search(self):
        raise NotImplementedError

    def perform_jobs_parsing(self):
        raise NotImplementedError

    def extract_job_skills(self, *args):
        raise NotImplementedError

    def extract_job_details(self, *args):
        raise NotImplementedError


