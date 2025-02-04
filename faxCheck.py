import os
import sys
import json
import pandas as pd
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

#정보 불러오기
loginPath = os.path.join(os.path.dirname(__file__),"..","loginInfo.json")
faxInfoPath = os.path.join(os.path.dirname(__file__),"DB","faxInfo.json")
with open(loginPath, 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open(faxInfoPath, 'r',encoding='utf-8') as f:
    fax_info = json.load(f)
works_login = pd.Series(login_info['worksMail'])
bot_info = pd.Series(login_info['nFaxbot'])
bot_HC = pd.Series(login_info['nFaxbot_hc'])
fax = pd.DataFrame(fax_info)

#works로그인
def getHome(page) -> None:
    page.get("https://mail.worksmobile.com/")
    time.sleep(2)
    id_box = page.find_element(By.XPATH,'//input[@id="user_id"]')
    login_button_1 = page.find_element(By.XPATH,'//button[@id="loginStart"]')
    id = works_login['id']
    ActionChains(page).send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()
    time.sleep(1)
    password_box = page.find_element(By.XPATH,'//input[@id="user_pwd"]')
    login_button_2 = page.find_element(By.XPATH,'//button[@id="loginBtn"]')
    password = works_login['pw']
    ActionChains(page).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
    time.sleep(2)
    page.get("https://mail.worksmobile.com/#/my/103")
#'C:\\Users\\USER\\Downloads\\fx_C023085724_D0260082368_B0_CH010_1738663363_0.tif'
#엔팩스 메일 확인
def newFax(page) -> None:
    page.refresh()
    time.sleep(2)
    mailHome_soup = BeautifulSoup(page.page_source,'html.parser')
    newMail = mailHome_soup.find('li', attrs={'class':'notRead'})
    if newMail != None:
        newMail = page.find_element(By.XPATH,"//li[contains(@class,'notRead')]//div[@class='mTitle']//strong[@class='mail_title']")
        ActionChains(page).click(newMail).perform()
        time.sleep(2)
        mail_soup = BeautifulSoup(page.page_source,'html.parser')
        fileName = mail_soup.find('a',attrs={'class':'file_name_txt'})
        if fileName != None:
            ActionChains(page).click(page.find_element(By.XPATH,'//button[@class="btn_down_pc"]')).perform()
            time.sleep(1)
            url = f"https://api.telegram.org/bot{bot_info['token']}/sendDocument"
            with open(f"C:\\Users\\USER\\Downloads\\{fileName.getText()}","rb") as file:
                requests.post(url, data={"chat_id":bot_info['chatId']}, files={"document":file})
            os.remove(f"C:\\Users\\USER\\Downloads\\{fileName.getText()}")
        else:
            pass
        faxNumber = mail_soup.find('span',attrs={'class':'subject'}).getText().replace(' ','').split("hecto_2f에")[1].split("로부터")[0]
        if faxNumber in fax['faxNumber'].tolist():
            tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {fax[fax['faxNumber'].isin([faxNumber])]['원천사'].reset_index(drop=True)[0]}"
            requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
        else:
            tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
            requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
        page.get("https://mail.worksmobile.com/#/my/103")
    else:
        pass

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
driver = webdriver.Firefox(options=options)
getHome(driver)
max_runtime = 1800
start_time = time.time()

#함수 구동
def main() -> None:
    try:
        runningTime = int(time.time()-start_time)  
        print(runningTime)
        newFax(driver)
        time.sleep(5)
        if (runningTime) >= max_runtime:
            requests.get(f"https://api.telegram.org/bot{bot_HC['token']}/sendMessage?chat_id={bot_HC['chatId']}&text=스크립트_재시작")
            time.sleep(2)
            driver.quit()
        else:
            pass
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(e)
        driver.quit()
        time.sleep(1)
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    while True:
        main()