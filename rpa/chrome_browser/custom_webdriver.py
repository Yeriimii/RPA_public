import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException as WDE
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert

class CustomWebDriver:

    @classmethod
    def run_chrome(cls):
        # # Debugger Chrome + headless
        # subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --headless --window-size=1920x1080 --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')

        # Debugger Chrome normal
        try:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')
        except:
            subprocess.Popen(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')

        option = Options()
        option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        option.add_argument('lang=ko_KR')

        # if OS is Linux: (--Headless, --no-sandbox, --disable-dev-shm-usage)
        # option.add_argument('disable-gpu')  # linux
        # option.add_argument('--headless')  # linux
        # option.add_argument("--no-sandbox")  # linux
        # option.add_argument("--disable-dev-shm-usage")  # linux (WSL 환경일 때)
        # option.binary_location = "/usr/bin/google-chrome" # linux Chrome 바이너리 경로 설정

        # Headless Chrome
        # option.headless = True
        option.add_argument("window-size=1920x1080")
        # option.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=option)
        # try:
        #     driver.maximize_window()
        # except:
        #     pass

        # print(driver.session_id)
        return driver
