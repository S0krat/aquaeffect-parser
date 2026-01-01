from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import Log
import Utils
import yaml
import datetime
import time
import traceback

from KalkunObject import KalkunObject
from SuibObject import SuibObject

Log.info("Загрузка конфигурации из файла config.yml")
config = yaml.safe_load(open("config.yml", 'r', encoding="utf-8"))

aquaeffect_objects = []
std_format = {"Cu1": 0, "Ag1": 1}

Log.info("Создание драйвера для симуляции работы браузера на основе Chrome")
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

Utils.kalkun_login(driver, config)
kalkun_tab = driver.current_window_handle

driver.switch_to.new_window('tab')
driver.get(config['suib_url'])
suib_tab = driver.current_window_handle

driver.switch_to.window(kalkun_tab)

for obj in config['objects']:
    if 'suib' in obj:
        if 'format' in obj:
            aquaeffect_objects.append(SuibObject(obj['name'], obj['format'], datetime.datetime.now() - datetime.timedelta(minutes=60), kalkun_tab, suib_tab, obj['suib']))
        else:
            aquaeffect_objects.append(SuibObject(obj['name'], std_format, datetime.datetime.now() - datetime.timedelta(minutes=60), kalkun_tab, suib_tab, obj['suib']))
    else:
        if 'format' in obj:
            aquaeffect_objects.append(KalkunObject(obj['name'], obj['format'], datetime.datetime.now() - datetime.timedelta(minutes=60)))
        else:
            aquaeffect_objects.append(KalkunObject(obj['name'], std_format, datetime.datetime.now() - datetime.timedelta(minutes=60)))

for aquaeffect_obj in aquaeffect_objects:
    try:
        aquaeffect_obj.send_message(driver)
    except Exception:
        Log.error(f"{traceback.format_exc()}")
        driver.refresh()
        driver.switch_to.window(kalkun_tab)
    time.sleep(5)

while True:
    time_for_next_iter = datetime.datetime.now() + datetime.timedelta(minutes=1)
    for aquaeffect_obj in aquaeffect_objects:
        try:
            if aquaeffect_obj.status == "done":
                continue
            elif aquaeffect_obj.status == "called":
                aquaeffect_obj.process_messages(driver)
            elif aquaeffect_obj.status == "wait":
                time_to_check = aquaeffect_obj.time_to_check
                now = datetime.datetime.now()
                if time_to_check < now:
                    aquaeffect_obj.send_message(driver)
                else:
                    Log.info(f"{aquaeffect_obj.name} : Повторная отправка сообщения произойдёт через {(aquaeffect_obj.time_to_check - datetime.datetime.now()).total_seconds() // 60 + 1} мин.")
        except Exception:
            Log.error(f"{traceback.format_exc()}")
            driver.refresh()
            driver.switch_to.window(kalkun_tab)
            Log.info("Перезагрузка страницы...")
            time.sleep(5)
    time_to_sleep = (time_for_next_iter - datetime.datetime.now()).total_seconds()
    if time_to_sleep > 1:
        Log.info(f"Остановка на {time_to_sleep} секунд...")
        time.sleep(time_to_sleep)
