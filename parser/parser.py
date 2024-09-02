import time
import json
import random
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.chrome.options import Options
from typing import Callable, Type, Union, Tuple, Any


options = Options()
options.add_argument("enable-automation")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")

HTTPS = "https"
HTTP = "http"

class Parser:
    prefixes = {HTTPS: "https://",
                HTTP: "http://"}

    def __init__(self, db_manager, source_name) -> None:
        self.db = db_manager
        self.source_name = source_name
        self.data_file = f"{self.source_name}_data.json"
        self.urls_file = f"{self.source_name}_urls.json"
        self.cache = []
        self.urls = []
        self.driver = webdriver.Chrome(options=options)
    
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

    def open_page(self, url=None) -> webdriver:
        url = self.url if not url else url
        return self.driver.get(url)

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
        return {'date_of_extraction': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.update(d)
        
    def remove_double_urls(self):
        data = []
        for url in self.urls:
            if not url in data:
                data.append(url)
        self.urls = data

    def insert_to_db(self, data:dict, model_type):
        return self.db_manager.create_document(data, model_type)
            
    def write_to_file(self, data, filename='extracted_data.json', mode='w'):
        with open(filename, mode, encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data has been written to {filename}")


