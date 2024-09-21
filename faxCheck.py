import time
import requests
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#DB정보 호출
with open('C:\\Users\\USER\\ve_1\\DB\\3loginInfo.json', 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open('C:\\Users\\USER\\ve_1\\DB\\6faxInfo.json', 'r',encoding='utf-8') as f:
    fax_info = json.load(f)
class nfax:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-javascript")
        options.add_argument('--disable-extensions')
        options.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = webdriver.Chrome(options=options)
        self.works_login = pd.Series(login_info['worksMail'])
        self.bot_info = pd.Series(login_info['nFaxbot'])
        self.fax = pd.DataFrame(fax_info)
    #로그인
    def getHome(self):
        self.driver.get("https://mail.worksmobile.com/")
        time.sleep(1)
        #로그인 정보입력(아이디)
        id_box = self.driver.find_element(By.XPATH,'//input[@id="user_id"]')
        login_button_1 = self.driver.find_element(By.XPATH,'//button[@id="loginStart"]')
        id = self.works_login['id']
        ActionChains(self.driver).send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()
        time.sleep(1)
        #로그인 정보입력(비밀번호)
        password_box = self.driver.find_element(By.XPATH,'//input[@id="user_pwd"]')
        login_button_2 = self.driver.find_element(By.XPATH,'//button[@id="loginBtn"]')
        password = self.works_login['pw']
        ActionChains(self.driver).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
        time.sleep(1)
    #엔팩스 메일 확인
    def newMail(self):
        self.driver.get("https://mail.worksmobile.com/#/my/103")
        time.sleep(2)
        mailHome_soup = BeautifulSoup(self.driver.page_source,'html.parser')
        if mailHome_soup.find('li', attrs={'class':'notRead'}) != None:
            faxNumber = mailHome_soup.find('strong', attrs={'class':'mail_title'}).getText().replace(' ','').split("hecto_2f에")[1].split("로부터")[0]
            if faxNumber in self.fax['faxNumber'].tolist():
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {self.fax[self.fax['faxNumber'] == faxNumber]['원천사'].values}"
                requests.get(f"https://api.telegram.org/bot{self.bot_info['token']}/sendMessage?chat_id={self.bot_info['chatId']}&text={tell}")
            else:
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
                requests.get(f"https://api.telegram.org/bot{self.bot_info['token']}/sendMessage?chat_id={self.bot_info['chatId']}&text={tell}")
            newMail = self.driver.find_element(By.XPATH,"//li[contains(@class,'notRead')]//div[@class='mTitle']//strong[@class='mail_title']")
            ActionChains(self.driver).click(newMail).perform()
        else:
            pass
    #종료
    def __del__(self):
        self.driver.quit()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-javascript")
        options.add_argument('--disable-extensions')
        options.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = webdriver.Chrome(options=options)
NFAX = nfax()
if __name__ == "__main__":
    while True:
        NFAX.getHome()
        for i in range(300):
            NFAX.newMail()
            time.sleep(5)
        NFAX.__del__()
        time.sleep(0.5)