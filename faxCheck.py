import time as t
import requests
import json
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
with open('C:\\Users\\USER\\ve_1\\DB\\3loginInfo.json', 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open('C:\\Users\\USER\\ve_1\\DB\\6faxInfo.json', 'r',encoding='utf-8') as f:
    fax_info = json.load(f)
works_login = pd.Series(login_info['nFax'])
bot_info = pd.Series(login_info['nFaxbot'])
fax = pd.DataFrame(fax_info)
class nfax:
    def __init__(self):
        from selenium import webdriver
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-javascript")
        options.add_argument('--disable-extensions')
        options.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = webdriver.Chrome(options=options)
    #로그인
    def getHome(self):
        self.driver.get("https://www.enfax.com/fax/view/receive")
        t.sleep(1)
        #로그인 정보입력(아이디)
        id_box = self.driver.find_element(By.XPATH,'//input[@id="userId"]')
        id = works_login['id']
        ActionChains(self.driver).send_keys_to_element(id_box, '{}'.format(id)).perform()
        t.sleep(1)
        #로그인 정보입력(비밀번호)
        password_box = self.driver.find_element(By.XPATH,'//input[@id="userPwd"]')
        loginbtn = self.driver.find_element(By.XPATH, '//button[@id="btnLogin"]')
        password = works_login['pw']
        ActionChains(self.driver).send_keys_to_element(password_box, '{}'.format(password)).click(loginbtn).perform()
        t.sleep(1)
    #엔팩스 메일 확인
    def newFax(self):
        self.driver.get("https://www.enfax.com/fax/view/receive")
        t.sleep(2)
        faxSoup = BeautifulSoup(self.driver.page_source,'html.parser')
        newfax = faxSoup.find('span', attrs={'class':'state_box stt_notread'})
        #요소 검증
        if newfax != None:
            #수신확인
            if newfax.get_text()=="안읽음":
                faxNumber = faxSoup.find('div', attrs={'class':'t_row stt_notread faxReceiveBoxListRow'}).get('data-send-fax-number')
                if faxNumber in fax['faxNumber'].tolist():
                    tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {fax[fax['faxNumber'] == faxNumber]['원천사'].values}"
                    #텔레그램 전송
                    requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
                    t.sleep(2)
                else:
                    tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
                    #텔레그램 전송
                    requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
                    t.sleep(2)
    #종료
    def logout(self):
        logout_btn = self.driver.find_element(By.XPATH,'//a[@class="link_logout"]')
        ActionChains(self.driver).click(logout_btn).perform()
        t.sleep(1)
NFAX = nfax()
if __name__ == "__main__":
    while True:
        NFAX.getHome()
        for i in range(100):
            NFAX.newFax()
            t.sleep(5)
        NFAX.logout()
        t.sleep(0.5)