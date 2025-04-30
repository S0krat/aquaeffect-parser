from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import Log
import Utils
import Messages
import yaml
import datetime
import re
import time

Log.info("Загрузка конфигурации из файла config.yml")
config = yaml.safe_load(open("config.yml", 'r', encoding="utf-8"))

Log.info("Создание драйвера для симуляции работы браузера на основе Chrome")
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

Utils.kalkun_login(driver, config)

regexp = re.compile(r"Cu1:.{,5}/.{,5},.{,5}/.{,5},.{,5}/.{,5},.{,10}\nAg1:.{,5}/.{,5},.{,5}/.{,5},.{,5}/.{,10},.*")

kalkunObjectList = Messages.send_all_messages(driver, config['objects'])

while True:
    try:
        time_for_next_iter = datetime.datetime.now() + datetime.timedelta(minutes=1)
        for kalkunObject in kalkunObjectList:
            if kalkunObject.status == "done":
                continue
            elif kalkunObject.status == "called":
                kalkunObject.process_messages(driver, regexp)
            elif kalkunObject.status == "wait":
                time_to_check = kalkunObject.time_to_check
                now = datetime.datetime.now()
                if time_to_check < now:
                    kalkunObject.send_message(driver)
                else:
                    Log.info(f"{kalkunObject.name} : Повторная отправка сообщения произойдёт через {(kalkunObject.time_to_check - datetime.datetime.now()).total_seconds() // 60 + 1} мин.")
        time_to_sleep = (time_for_next_iter - datetime.datetime.now()).total_seconds()
        if time_to_sleep > 1:
            Log.info(f"Остановка на {time_to_sleep} секунд...")
            time.sleep(time_to_sleep)
    except Exception as e:
        Log.error(f"{e}")
        driver.refresh()
        Log.info("Перезагрузка страницы...")
        time.sleep(5)
