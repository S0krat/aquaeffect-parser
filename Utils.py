from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import Log


def kalkun_login(driver: WebDriver, config: dict) -> None:
    Log.info("Вход в аккаунт")
    driver.get(config['kalkun_url'])

    login_element = driver.find_element(By.NAME, "username")
    login_element.clear()
    login_element.send_keys(config["username"])

    password_element = driver.find_element(By.NAME, "password")
    password_element.clear()
    password_element.send_keys(config["password"])

    driver.find_element(By.ID, "submit").click()


def goto_phone_dict(driver: WebDriver) -> None:
    driver.find_element(By.LINK_TEXT, "Телефонная книга").click()


def goto_messages(driver: WebDriver) -> None:
    driver.find_element(By.LINK_TEXT, "Входящие").click()
