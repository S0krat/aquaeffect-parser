from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import re

import Log
import Utils


class KalkunObject:
    def __init__(self, name: str, start_time: datetime.datetime):
        self.name = name
        self.last_time_check = start_time
        self.status = "called"
        self.Ag1 = None
        self.workedAg1 = None
        self.Cu1 = None
        self.workedCu1 = None
        self.time_of_message_Cu1 = None
        self.time_of_message_Ag1 = None
        self.time_to_check = None

    def find_messages(self, driver: WebDriver):
        message_list = []
        times_list = []

        while True:
            times, names = zip(*[kids.find_elements(By.CSS_SELECTOR, "*")[0].text.strip().split("     ") for kids in
                                 driver.find_elements(By.CLASS_NAME, "message_toggle")])
            elements = driver.find_elements(By.CLASS_NAME, "messagelist")
            times = [datetime.datetime.fromisoformat(time) for time in times]
            names = [" ".join(name.split()[:-1]) for name in names]
            indexes = [i for i in range(20) if names[i] == self.name]

            for index in indexes:
                if times[index] > self.last_time_check:
                    message_list.append(elements[index].get_attribute("title"))
                    times_list.append(times[index])

            if times[19] >= self.last_time_check:
                try:
                    driver.find_element(By.LINK_TEXT, ">").click()
                except NoSuchElementException:
                    self.last_time_check = max(
                        times_list) if times_list else datetime.datetime.now() - datetime.timedelta(minutes=1)
                    return message_list, times_list
            else:
                self.last_time_check = max(times_list) if times_list else datetime.datetime.now() - datetime.timedelta(
                    minutes=1)
                return message_list, times_list

    def process_messages(self, driver: WebDriver, regexp):
        Utils.goto_messages(driver)
        messages, times = self.find_messages(driver)
        if not messages:
            Log.warn(f"{self.name} : Сообщений не найдено")
        for i in range(len(messages)):
            if regexp.match(messages[i]):
                numbers = re.findall(r'\+?-?\b\d+\b', messages[i])
                if len(numbers) < 12:
                    Log.warn(
                        f"{self.name} : Найдено сообщение \"{messages[i].replace('\n', ' ')}\", не соответствующее формату. Оно "
                        f"будет пропущено")
                    continue
                else:
                    Log.info(f"{self.name} : Найдено сообщение \"{messages[i].replace('\n', ' ')}\"")
                if int(numbers[2]):
                    Log.info(f"{self.name} : Записано значение Cu1 = '{numbers[0]}'")
                    self.Cu1 = numbers[0]
                    self.workedCu1 = int(numbers[2])
                    self.time_of_message_Cu1 = times[i]
                if (not int(numbers[2])) and (not self.Cu1):
                    delta_to_check = int(numbers[4])
                    if not delta_to_check:
                        Log.warn(f"{self.name} : Cu1 отсутствует на объекте. Записано значение Cu1 = '000'")
                        self.Cu1 = '000'
                        self.workedCu1 = 0
                        self.time_of_message_Cu1 = times[i]
                    else:
                        new_time_to_check = times[i] + datetime.timedelta(minutes=delta_to_check + 2)
                        if self.time_to_check:
                            if self.time_to_check > new_time_to_check:
                                self.time_to_check = new_time_to_check
                                self.status = "wait"
                                Log.info(
                                    f"{self.name} : Повторная проверка будет осуществлена через {(new_time_to_check - datetime.datetime.now()).total_seconds() // 60} мин.")
                        else:
                            self.time_to_check = new_time_to_check
                            self.status = "wait"
                            Log.info(
                                f"{self.name} : Повторная проверка будет осуществлена через {(new_time_to_check - datetime.datetime.now()).total_seconds() // 60} мин.")
                if int(numbers[8]):
                    Log.info(f"{self.name} : Записано значение Ag1 = '{numbers[6]}'")
                    self.Ag1 = numbers[6]
                    self.workedAg1 = int(numbers[8])
                    self.time_of_message_Ag1 = times[i]
                if (not int(numbers[8])) and (not self.Ag1):
                    delta_to_check = int(numbers[10])
                    if not delta_to_check:
                        Log.warn(f"{self.name} : Ag1 отсутствует на объекте. Записано значение Ag1 = '000'")
                        self.Ag1 = '000'
                        self.workedAg1 = 0
                        self.time_of_message_Ag1 = times[i]
                    else:
                        new_time_to_check = times[i] + datetime.timedelta(minutes=int(numbers[10]) + 2)
                        if self.time_to_check:
                            if self.time_to_check > new_time_to_check:
                                self.time_to_check = new_time_to_check
                                self.status = "wait"
                                Log.info(
                                    f"{self.name} : Повторная проверка будет осуществлена через {(new_time_to_check - datetime.datetime.now()).total_seconds() // 60} мин.")
                        else:
                            self.time_to_check = new_time_to_check
                            self.status = "wait"
                            Log.info(
                                f"{self.name} : Повторная проверка будет осуществлена через {(new_time_to_check - datetime.datetime.now()).total_seconds() // 60} мин.")

            else:
                Log.warn(
                    f"{self.name} : Найдено сообщение \"{messages[i].replace('\n', ' ')}\", не соответствующее формату. Оно будет "
                    f"пропущено")

        if self.Cu1 and self.Ag1:
            self.status = "done"
            self.post_to_excel()

    def post_to_excel(self):
        Log.info(f"{self.name} : Запись в файл")
        with open("output.txt", "a") as file:
            if self.Cu1 == '000':
                file.write(
                    f"{self.name} : {self.time_of_message_Ag1.strftime('%d.%m.%Y')} : {self.time_of_message_Ag1.strftime('%H:%M')} : Ag1 = {self.Ag1}, {self.workedAg1}\n")
            elif self.time_of_message_Cu1 == self.time_of_message_Ag1:
                file.write(
                    f"{self.name} : {self.time_of_message_Cu1.strftime('%d.%m.%Y')} : {self.time_of_message_Cu1.strftime('%H:%M')} : Cu1 = {self.Cu1}, {self.workedCu1} : Ag1 = {self.Ag1}, {self.workedAg1}\n")
            else:
                length_of_name = len(self.name) + 3
                file.write(
                    f"{self.name} : {self.time_of_message_Cu1.strftime('%d.%m.%Y')} : {self.time_of_message_Cu1.strftime('%H:%M')} : Cu1 = {self.Cu1}, {self.workedCu1}\n{" " * length_of_name}{self.time_of_message_Ag1.strftime('%d.%m.%Y')} : {self.time_of_message_Ag1.strftime('%H:%M')} : Ag1 = {self.Ag1}, {self.workedAg1}\n")

    def send_message(self, driver: WebDriver):
        Utils.goto_phone_dict(driver)
        while True:
            names_on_page = [lce.find_elements(By.CSS_SELECTOR, "*")[1].text for lce in
                             driver.find_elements(By.ID, "pbkname")]
            links_elements = driver.find_elements(By.CLASS_NAME, "sendmessage.simplelink")
            if self.name in names_on_page:
                index = names_on_page.index(self.name)
                driver.execute_script("$(arguments[0]).click();", links_elements[index])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "word_count"))).send_keys("Status?")
                self.status = "called"
                self.time_to_check = None
                Log.info(f"{self.name} : Отправление сообщения \"Status?\"...")
                driver.find_element(By.XPATH, "//button[text()='Послать сообщение']").click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Okay']"))).click()
                Log.info(f"{self.name} : Отправлено сообщение \"Status?\"")
                break
            else:
                try:
                    driver.find_element(By.LINK_TEXT, ">").click()
                except NoSuchElementException:
                    Log.error(
                        f"Объекта с именем \"{self.name}\" не существует в телефонной книге, хотя раньше был там???")
                    break
