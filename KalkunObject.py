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
    def __init__(self, name: str, msg_format: dict, start_time: datetime.datetime):
        self.name = name
        self.last_time_check = start_time
        self.msg_format = msg_format
        self.status = "called"
        self.elem_status: dict[str, bool] = {}
        for elem in msg_format:
            self.elem_status[elem] = False
        self.messages = []
        self.times_of_messages = []
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
                        times_list) if times_list else datetime.datetime.now() - datetime.timedelta(minutes=3)
                    return message_list, times_list
            else:
                self.last_time_check = max(times_list) if times_list else datetime.datetime.now() - datetime.timedelta(
                    minutes=3)
                return message_list, times_list

    def process_messages(self, driver: WebDriver):
        Utils.goto_messages(driver)
        messages, times = self.find_messages(driver)
        if not messages:
            Log.warn(f"{self.name} : Сообщений не найдено")
        for i in range(len(messages)):
            numbers = re.findall(r'\+?-?\b\d{1,8}\b', messages[i])
            if len(numbers) < max(self.msg_format.values()) * 6 + 6:
                Log.warn(
                    f"{self.name} : Найдено сообщение \"{messages[i].replace('\n', ' ')}\", не соответствующее "
                    f"формату. Оно будет пропущено")
                continue
            else:
                Log.info(f"{self.name} : Найдено сообщение \"{messages[i].replace('\n', ' ')}\"")

            for element in self.msg_format:
                order = self.msg_format[element]
                if self.elem_status[element]:
                    continue
                if int(numbers[order * 6 + 2]):
                    Log.info(f"{self.name} : Записано значение {element} = '{numbers[order * 6]}'")
                    self.elem_status[element] = True
                    if times[i] not in self.times_of_messages:
                        self.messages.append(messages[i])
                        self.times_of_messages.append(times[i])
                else:
                    delta_to_check = int(numbers[order * 6 + 4])
                    if not delta_to_check:
                        Log.warn(f"{self.name} : {element} отсутствует на объекте")
                        self.elem_status[element] = True
                    else:
                        Log.info(f"{self.name} : {element} будет доступен через {delta_to_check} мин.")
                        new_time_to_check = times[i] + datetime.timedelta(minutes=delta_to_check + 3)
                        if self.time_to_check:
                            if self.time_to_check < new_time_to_check:
                                Log.info(
                                    f"{self.name} : Время проверки изменено с {(self.time_to_check - datetime.datetime.now()).total_seconds() // 60} на {(new_time_to_check - datetime.datetime.now()).total_seconds() // 60} мин.")
                                self.time_to_check = new_time_to_check
                                self.status = "wait"
                        else:
                            Log.info(f"{self.name} : {element} - новое время проверки = {times[i]} + {datetime.timedelta(minutes=delta_to_check + 3)} = {new_time_to_check}")
                            self.time_to_check = new_time_to_check
                            self.status = "wait"
                            Log.info(
                                f"{self.name} : Повторная проверка будет осуществлена через {(new_time_to_check - datetime.datetime.now()).total_seconds() // 60} мин.")

        if all(self.elem_status.values()):
            self.status = "done"
            self.post_to_file()

    def post_to_file(self):
        Log.info(f"{self.name} : Запись в файл")
        with open("output.txt", "a", encoding='utf-8') as file:
            output_string = f"**{self.name}**\n"
            length_of_answers = len(self.messages)
            if length_of_answers > 0:
                output_string += f"{self.times_of_messages[length_of_answers - 1]}\n```{self.messages[length_of_answers - 1]}```\n"
            file.write(output_string)

    def send_message(self, driver: WebDriver):
        Utils.goto_phone_dict(driver)
        while True:
            names_on_page = [lce.find_elements(By.CSS_SELECTOR, "*")[1].text for lce in
                             driver.find_elements(By.ID, "pbkname")]
            links_elements = driver.find_elements(By.CLASS_NAME, "sendmessage.simplelink")
            if self.name in names_on_page:
                index = names_on_page.index(self.name)
                driver.execute_script("$(arguments[0]).click();", links_elements[index])
                message = "Status?"
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "word_count"))).send_keys(message)
                self.status = "called"
                self.time_to_check = None
                Log.info(f"{self.name} : Отправление сообщения \"{message}\"...")
                driver.find_element(By.XPATH, "//button[text()='Послать сообщение']").click()
                # driver.find_element(By.XPATH, "//button[text()='Отмена']").click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Okay']"))).click()
                break
            else:
                try:
                    driver.find_element(By.LINK_TEXT, ">").click()
                except NoSuchElementException:
                    Log.error(
                        f"Объекта с именем \"{self.name}\" не существует в телефонной книге, хотя раньше был там???")
                    break
