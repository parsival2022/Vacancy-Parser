import os, time, json, random, requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.chrome.options import Options
from typing import Callable, Iterable
from webdriver_manager.chrome import ChromeDriverManager
from .decorators import repeat_if_fail
from .constants import *
from .errors import ModeUnacceptableMethod, NoRequiredParameterProvided

load_dotenv()
HTTPS = "https"
HTTP = "http"

class Parser:
    source_name = "base_parser"
    prefixes = {HTTPS: "https://",
                HTTP: "http://"}
    headers = {}
    cache = []
    current_page = None

    base_url = "https://www.example.com"
    login_url = None
    
    # elements that are used in default perform_login method
    username_input = (By.ID, "email")
    password_input = (By.ID, "password")
    login_btn = (By.XPATH, '//button[text()="Log In"]')
    login_fails = ((By.XPATH, '//div[contains(@class, "form-group has-error")]'))



    def __init__(self, init_url=None, db_manager=None, use_driver=True, use_request=False, proxies=[]) -> None:
        self.init_url = init_url if init_url else self.login_url
        self.db_manager = db_manager
        self.data_file = f"{self.source_name}_data.json"
        self.urls_file = f"{self.source_name}_urls.json"
        self.username = os.environ.get(self.source_name.upper().replace(" ", "_") + "_USERNAME") or None
        self.password = os.environ.get(self.source_name.upper().replace(" ", "_") + "_PASSWORD") or None
        self.proxies = proxies
        self.use_driver = use_driver
        self.use_request = use_request
        if self.use_request:
            self.session = requests.Session()
        if self.use_driver:
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
        # options.add_argument("--headless")
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
        
    def add_prefix(self, url:str, mode:str) -> str:
        if not "://" in url:
            url = self.prefixes[mode] + url
        return url
    
    def remove_double_urls(self):
        data = []
        for url in self.urls:
            if not url in data:
                data.append(url)
        self.urls = data
    
    def urls_normalisation(self) -> None:
        urls = [self.add_prefix(url) for url in self.urls]
        self.urls = urls

    def urls_normalisation_file(self, filepath:str, mode) -> None:
        with open(filepath, 'r') as file:
            urls = json.load(file)
        checked_urls = [self.add_prefix(url, mode) for url in urls]
        self.write_to_file(f'normalised_{self.source_name}_data.json', checked_urls)
    
    def combine_cookies(self):
        cookies = '; '.join(['%s=%s'%(key,value) for key,value in self.session.cookies.get_dict().items()]) 
        return cookies
    
    def update_cookies(self):
        cookies = self.combine_cookies()
        self.headers.update({"Cookies": cookies})
    
    def make_get_request(self, url=None, soup=False, **kwargs):
        url = self.init_url if not url else url
        res = self.session.get(url, **kwargs)
        res.raise_for_status()
        if soup:
           soup = BeautifulSoup(res.text, "html.parser")
           return soup
        return res
    
    def make_post_request(self, url, soup=False, *args, **kwargs):
        if not url:
            raise NoRequiredParameterProvided
        res = self.session.post(url, *args, **kwargs)
        if soup:
           soup = BeautifulSoup(res.text, "html.parser")
           return soup
        return res
    
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
    
    def soup_extract_text_suite(self, soup:BeautifulSoup=None, *args) -> dict:
        if not soup:
            soup = self.parse_page()
        data = {}
        for creds in args:
            data[creds[0]] = soup.find(*creds[1]).get_text(strip=True)
        return data
    
    @repeat_if_fail(NoSuchElementException, 7)
    def click_on_element(self, by, value):
        self.driver.find_element(by, value).click()

    @repeat_if_fail(NoSuchElementException, 5)
    def wait_and_click_on_element(self, by, value):
        element = WebDriverWait(self.driver, 10).until(
                  EC.element_to_be_clickable((by, value)))
        element.click()

    @repeat_if_fail(NoSuchElementException, 5)
    def fill_input_element(self, by, input, keys):
        input = self.driver.find_element(by, input)
        input.clear()
        input.send_keys(keys)
            
    def write_to_file(self, data, filename='parser_data.json'):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def append_to_file(self, filename, data:Iterable[str]|str):
        with open(filename, 'a') as file:
            if isinstance(data, (tuple, set, list)):
                for url in data:
                    file.write(url + '\n')
            else: file.write(data + '\n')

    @repeat_if_fail(NoSuchElementException, 5)
    def perform_login(self):
        lu = self.login_url if self.login_url else self.init_url
        self.driver.get(lu)
        self.wait(DELAY_10_15)
        self.fill_input_element(*self.username_input, self.username)
        self.fill_input_element(*self.password_input, self.password)
        self.wait(DELAY_4_8)
        self.click_on_element(*self.login_btn)
        try:
            for fail in self.login_fails:
                self.driver.find_element(*fail)
            self.driver.quit()
        except NoSuchElementException: 
            pass
        self.wait(15)