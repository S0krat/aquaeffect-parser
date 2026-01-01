import datetime
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import Log
from KalkunObject import KalkunObject


class SuibObject(KalkunObject):
    def __init__(self, name: str, msg_format: dict, start_time: datetime.datetime, kalkun_tab, suib_tab, suib_name):
        super().__init__(name, msg_format, start_time)
        self.kalkun_tab = kalkun_tab
        self.suib_tab = suib_tab
        self.suib_name = suib_name

    def send_message(self, driver: WebDriver):
        Log.info(f"{self.name} : Отправление сообщения \"Status?\"...")
        self.status = "called"
        self.time_to_check = None
        driver.switch_to.window(self.suib_tab)
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='md-raised md-button md-ink-ripple']"))).click()
        time.sleep(2)
        elem = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Молодежный')]")))
        scroll_origin = ScrollOrigin.from_element(elem, 0, -50)
        ActionChains(driver) \
            .scroll_from_origin(scroll_origin, 0, 2000) \
            .perform()
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{self.suib_name}')]"))).click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='СМС']").click()
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='md-text ng-binding']"))).click()
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "md-option[value='Status?']"))).click()
        # WebDriverWait(driver, 3).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "md-option[value='StatG1?']"))).click()
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='buttonОтправить']").click()
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='Все ИП']").click()
        driver.switch_to.window(self.kalkun_tab)
