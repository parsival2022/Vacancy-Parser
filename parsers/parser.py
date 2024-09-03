import os
import time
import json
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.chrome.options import Options
from typing import Callable, Type, Union, Tuple, Any


HTTPS = "https"
HTTP = "http"

class Parser:
    prefixes = {HTTPS: "https://",
                HTTP: "http://"}

    def __init__(self, init_url, db_manager, source_name, use_driver=True) -> None:
        load_dotenv()
        self.init_url = init_url
        self.db_manager = db_manager
        self.source_name = source_name
        self.data_file = f"{self.source_name}_data.json"
        self.urls_file = f"{self.source_name}_urls.json"
        self.username = os.environ.get('USERNAME')
        self.password = os.environ.get('PASSWORD')
        self.cache = []
        self.urls = []
        self.use_driver = use_driver
        if self.use_driver:
            self.driver = webdriver.Chrome
            self.service = Service
            self.options = Options()
            self.options.add_argument("enable-automation")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-extensions")
            self.options.add_argument("--dns-prefetch-disable")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--disable-gpu-compositing")
            # self.options.add_argument("--headless")
            # self.options.add_argument("--disable-software-rasterizer")
            # self.options.add_argument("--window-size=1920,1080")
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("--disable-webrtc")
            
    
    def get_time(self, t:int|tuple) -> int:
        if isinstance(t, int): 
            return t
        return random.randint(*t)
   
    def wait(self, t):
        time.sleep(self.get_time(t))

    def add_prefix(self, url, mode):
        if not "://" in url:
            url = self.prefixes[mode] + url
        return url
    
    def urls_normalisation(self) -> None:
        urls = [self.add_prefix(url) for url in self.urls]
        self.urls = urls

    def urls_normalisation_file(self, filepath:str) -> None:
        with open(filepath, 'r') as file:
            urls = json.load(file)
        checked_urls = [self.add_prefix(url) for url in urls]
        self.write_to_file('normalised_data.json', checked_urls)

    def open_page(self, url=None) -> webdriver.Chrome:
        url = self.init_url if not url else url
        driver = webdriver.Chrome(service=Service(), options=self.options)
        page = driver.get(url)
        return page
    
    def make_get_request(self, url=None, soup=False, **kwargs):
        url = self.init_url if not url else url
        res = requests.get(url, **kwargs)
        print(res.text)
        res.raise_for_status()
        if soup:
           soup = BeautifulSoup(res.text, "html.parser")
           return soup
        return res

    def parse_page(self, page:webdriver.Chrome) -> BeautifulSoup:
        self.wait((4, 10))
        return BeautifulSoup(page.page_source, 'html.parser')
        
    def find_many(self, tag:str, filter:dict, page:BeautifulSoup, **kwargs) -> list:
        return page.find_all(tag, attrs=filter, **kwargs)
        
    def extract_attribute(self, el, attr):
        return el[attr]

    def extract_attributes(self, el:list, attr:str):
        res = []
        for _ in el:
            extracted = self.extract_attribute(_, attr)
            res.append(extracted)
        return res

    def combined_extraction(self, tag, filter, attr, page, **kwargs) -> list:
        list_of_tags = self.find_many(tag, filter, page, **kwargs)
        list_of_attributes = self.extract_attributes(list_of_tags, attr)
        return list_of_attributes
    
    def repeat_if_fail(self, exception:Type[Exception], wait:Union[int, Tuple[int, int]] = None) -> Any:

        def decorator(func:Callable):
            def wrapper(*args, **kwargs):
                try:
                    if wait: self.wait(wait)
                    return func(*args, **kwargs)
                except exception:
                    if wait: self.wait(wait)
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def data_formatter(self, d:dict) -> dict:
        res = {'date_of_extraction': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': self.source_name}
        res.update(d)
        return res
        
    def remove_double_urls(self):
        data = []
        for url in self.urls:
            if not url in data:
                data.append(url)
        self.urls = data

    def insert_to_db(self, data:dict, model_type):
        d = self.data_formatter(data)
        return self.db_manager.create_document(d, model_type)
            
    def write_to_file(self, data, filename='extracted_data.json', mode='w'):
        with open(filename, mode, encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data has been written to {filename}")

    def login(self):
        pass

    def parsing_suite(self):
        pass