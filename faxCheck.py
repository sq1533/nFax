import time as t
import requests
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument("--disable-javascript")
options.add_argument('--disable-extensions')
options.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=options)
class nfax:
    def __init__(self):
        with open('C:\\Users\\USER\\ve_1\\DB\\3loginInfo.json', 'r', encoding='utf-8') as f:
            login_info = json.load(f)
        with open('C:\\Users\\USER\\ve_1\\DB\\6faxInfo.json', 'r',encoding='utf-8') as f:
            fax_info = json.load(f)
        self.works_login = pd.Series(login_info['worksMail'])
        self.bot_info = pd.Series(login_info['nFaxbot'])
        self.fax = pd.DataFrame(fax_info)
    #로그인
    def getHome(self):
        driver.get("https://mail.worksmobile.com/")
        t.sleep(1)
        #로그인 정보입력(아이디)
        id_box = driver.find_element(By.XPATH,'//input[@id="user_id"]')
        login_button_1 = driver.find_element(By.XPATH,'//button[@id="loginStart"]')
        id = self.works_login['id']
        ActionChains(driver).send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()
        t.sleep(1)
        #로그인 정보입력(비밀번호)
        password_box = driver.find_element(By.XPATH,'//input[@id="user_pwd"]')
        login_button_2 = driver.find_element(By.XPATH,'//button[@id="loginBtn"]')
        password = self.works_login['pw']
        ActionChains(driver).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
        t.sleep(1)
    #엔팩스 메일 확인
    def newMail(self):
        driver.get("https://mail.worksmobile.com/#/my/103")
        t.sleep(2)
        mailHome_soup = BeautifulSoup(driver.page_source,'html.parser')
        if mailHome_soup.find('li', attrs={'class':'notRead'}) != None:
            faxNumber = mailHome_soup.find('strong', attrs={'class':'mail_title'}).getText().replace(' ','').split("hecto_2f에")[1].split("로부터")[0]
            if faxNumber in self.fax['faxNumber'].tolist():
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {self.fax[self.fax['faxNumber'] == faxNumber]['원천사'].values}"
                requests.get(f"https://api.telegram.org/bot{self.bot_info['token']}/sendMessage?chat_id={self.bot_info['chatId']}&text={tell}")
            else:
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
                requests.get(f"https://api.telegram.org/bot{self.bot_info['token']}/sendMessage?chat_id={self.bot_info['chatId']}&text={tell}")
            newMail = driver.find_element(By.XPATH,"//li[contains(@class,'notRead')]//div[@class='mTitle']//strong[@class='mail_title']")
            ActionChains(driver).click(newMail).perform()
        else:
            pass
    #종료
    def logout(self):
        logout_profile = driver.find_element(By.XPATH,'//div[@class="profile_area"]')
        logout_btn = driver.find_element(By.XPATH,'//a[@class="btn logout"]')
        ActionChains(driver).click(logout_profile).click(logout_btn).perform()
        t.sleep(1)
    def login(self):
        password_box = driver.find_element(By.XPATH,'//input[@id="user_pwd"]')
        login_button_2 = driver.find_element(By.XPATH,'//button[@id="loginBtn"]')
        password = self.works_login['pw']
        ActionChains(driver).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
        t.sleep(1)
NFAX = nfax()
if __name__ == "__main__":
    NFAX.getHome()
    while True:
        for i in range(300):
            NFAX.newMail()
            t.sleep(5)
        NFAX.logout()
        NFAX.login()
        t.sleep(0.5)