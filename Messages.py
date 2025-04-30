import datetime

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Log
import Utils
from KalkunObject import KalkunObject
from typing import List


def send_all_messages(driver: WebDriver, objects_list: List[str]):
    kalkunObjectsList = []
    Utils.goto_phone_dict(driver)
    object_num = len(objects_list)
    i = 0
    while i < object_num:
        names_on_page = [lce.find_elements(By.CSS_SELECTOR, "*")[1].text for lce in
                         driver.find_elements(By.ID, "pbkname")]
        links_elements = driver.find_elements(By.CLASS_NAME, "sendmessage.simplelink")
        if objects_list[i] in names_on_page:
            index = names_on_page.index(objects_list[i])
            driver.execute_script("$(arguments[0]).click();", links_elements[index])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "word_count"))).send_keys(
                "Status?")
            kalkunObjectsList.append(KalkunObject(objects_list[i], datetime.datetime.now()))
            driver.find_element(By.XPATH, "//button[text()='Послать сообщение']").click()
            Log.info(f"{objects_list[i]} : Отправлено сообщение \"Status?\"")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Okay']"))).click()
            driver.find_element(By.LINK_TEXT, "Телефонная книга").click()
            i += 1
        else:
            try:
                driver.find_element(By.LINK_TEXT, ">").click()
            except NoSuchElementException:
                Log.warn(f"Объекта с именем \"{objects_list[i]}\" не существует в телефонной книге, объект пропущен")
                driver.find_element(By.LINK_TEXT, "Телефонная книга").click()
                i += 1

    return kalkunObjectsList
