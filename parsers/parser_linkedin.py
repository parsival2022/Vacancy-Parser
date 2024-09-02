import requests
from parsers.parser import Parser
from db_manager.mongo_manager import MongoManager
from db_manager.models import Vacancy
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, WebDriverException

VACANCY = "vacancy"
DELAY_4_8 = (4, 8) 
DELAY_8_10 = (8, 10)
DELAY_10_15 = (10, 15)
DELAY_60 = 60
test_doc = {
    'title': "test title",
    'country': "UA",
    'level': "junior",
    'skills': ['JS', 'Python'],
    'job_type': 'hybrid',
    'employment_type': 'contract',
    'salary': '400$'
}

class LinkedinParser(Parser):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-encoding": "gzip, deflate, br, zstd",
        "Accept-language": "uk-UA,uk;q=0.9",
        "Cache-control": "max-age=0",
        "Cookie": 'JSESSIONID=ajax:2659555701813428027; lang=v=2&lang=uk-ua; bcookie="v=2&3545f150-c339-4c51-8874-b2309ad18a60"; bscookie="v=1&202409020531171a850f0f-8edb-4a8f-826a-ed873920d3d4AQET4B9QBZNdXnR6KCzGD4F57GFhlrg4"; lidc="b=OGST01:s=O:r=O:a=O:p=O:g=3381:u=1:x=1:i=1725255077:t=1725341477:v=2:sig=AQGXaR3L2EqRy270J6lvBaUY1L7TCFG6"; li_rm=AQHILcJ7xK_xMQAAAZGxN1ADH1pKoLsa80KPyG45hUpoJfKcbmLuNppD8BTfV1sgf4QoOrHYApZfbs9hUGZAI9dStnYlT0gczhbSRWlIeyA3KPF8-X4KB_hY; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19969%7CMCMID%7C79849021528006158833348592649415156647%7CMCAAMLH-1725859884%7C6%7CMCAAMB-1725859884%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1725262284s%7CNONE%7CvVersion%7C5.1.1; aam_uuid=79351282031360936963366362077809414252',
        "Priority": "u=0, i",
        "Sec-ch-ua": 'Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "Sec-ch-ua-mobile": "?0",
        "Sec-ch-ua-platform": '"Windows"',
        "Sec-fetch-dest": "document",
        "Sec-fetch-mode": "navigate",
        "Sec-fetch-site": "none",
        "Sec-fetch-user": "?1",
        "Upgrade-insecure-requests": "1",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    def login(self):
        login_page = self.open_page()
        self.wait(DELAY_10_15)
        print(login_page.page_source)
        login_page.find_element(By.ID, 'username').send_keys(self.username)
        login_page.find_element(By.ID, 'password').send_keys(self.password)
        self.wait(DELAY_4_8)
        login_page.find_element(By.CSS_SELECTOR, '[data-litms-control-urn="login-submit"]').click()
        self.wait(DELAY_60)

if __name__ == "__main__":
    # MongoManager.__init_database__()
    # db_manager = MongoManager("Vacancies", {VACANCY: Vacancy})
    # linkedin = LinkedinParser("https://www.linkedin.com/login/uk", 
    #                           db_manager, 
    #                           source_name="Linkedin", 
    #                           use_driver=True)
    # linkedin.login()
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.get("https://www.linkedin.com/login/uk")
