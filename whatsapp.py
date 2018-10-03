from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from command import Thuisbezorgd, LaatsteNieuws, Screenshot, Weersverwachting, Bieraanbieding, Fap


class Bot:
    last_message = None

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='C:\\Users\\Boris\\chromedriver.exe')
        self.driver.maximize_window()

    def get_qr(self):
        """
        Waits for the QR-code to be scanned.

        :return: void
        """
        self.driver.get('https://web.whatsapp.com/')
        wait_message = "Open WhatsApp on your phone"
        while wait_message in self.driver.page_source:
            pass
        sleep(5)
        return

    def get_last_message(self):
        """
        Retrieves the last message, and compares it against the last sender.

        :return: string
        """
        try:
            all_msgs = self.driver.find_elements(By.XPATH, '//*[@id="main"]//div[contains(@class, "message")]')
            if len(all_msgs) > 0:
                msg = all_msgs[-1]
                author, msg = self.fetch_information(msg)
                if self.last_message != author + msg:
                    self.last_message = author + msg
                    print('[Received] {}'.format(self.last_message))
                    return msg
                else:
                    return None
        except Exception as e:
            print('[DEBUG] {}'.format(str(e)))

    def fetch_information(self, webelement):
        """
        Fetch the autor and message out of an element.

        :param webelement: Selenium Element
        :return: string, string
        """
        try:
            msg = webelement.find_element(By.XPATH, './/div[contains(@class, "copyable-text")]')
            msg_sender = msg.get_attribute('data-pre-plain-text')
            msg_text = msg.find_elements(By.XPATH, './/span[contains(@class, "selectable-text")]')[-1].text
        except IndexError as e:
            msg_text = ""
            print('[DEBUG] {}'.format(str(e)))
        except Exception as e:
            msg_sender = ""
            msg_text = ""
            print('[DEBUG] {}'.format(str(e)))
        return msg_sender, msg_text

    def go_to_chat(self, chat):
        """
        Clicks on a chat

        :param chat: string
        :return: void
        """
        self.driver.find_element(By.XPATH, '//*[@title="{}"]'.format(chat)).click()
        return

    def sendmsg(self, msg):
        """
        Type 'msg' in 'driver' and press RETURN
        """
        # select correct input box to type msg
        input_box = self.driver.find_element(
            By.XPATH, '//*[@id="main"]//footer//div[contains(@contenteditable, "true")]')
        # input_box.clear()
        input_box.click()
        msg = msg.split('\n')
        action = ActionChains(self.driver)
        for m in msg:
            action\
                .send_keys(m)\
                .key_down(Keys.SHIFT)\
                .send_keys(Keys.RETURN)\
                .key_up(Keys.SHIFT)
        action.send_keys(Keys.RETURN)
        action.perform()


running_commands = [Thuisbezorgd(), LaatsteNieuws(), Screenshot(), Weersverwachting(), Bieraanbieding(), Fap()]

bot = Bot()
bot.get_qr()
bot.go_to_chat('Oefenbal')

while True:
    msg = bot.get_last_message()
    if msg is not None:
        if msg.startswith('!help'):
            bericht = ""
            for command in running_commands:
                bericht += '*' + command.get_title() + '*\n' + command.description + '\n\n'
            bot.sendmsg(bericht)
        for command in running_commands:
            if msg.startswith(command.get_prefix()):
                if command.optional and not command.driver:
                    opt = msg.split()[1]
                    bot.sendmsg(command.run(opt))
                elif command.driver:
                    if command.optional:
                        opt = msg.split()[1:]
                        opt = "".join(opt)
                        command.run(driver=bot.driver, params=opt)
                    else:
                        command.run(bot.driver)
                else:
                    bot.sendmsg(command.run())

