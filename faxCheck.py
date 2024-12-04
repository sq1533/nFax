import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time as t
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
with open('C:\\Users\\USER\\ve_1\\DB\\3loginInfo.json', 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open('C:\\Users\\USER\\ve_1\\DB\\6faxInfo.json', 'r',encoding='utf-8') as f:
    fax_info = json.load(f)
works_login = pd.Series(login_info['worksMail'])
bot_info = pd.Series(login_info['nFaxbot'])
bot_HC = pd.Series(login_info['nFaxbot_hc'])
fax = pd.DataFrame(fax_info)
#works로그인
def getHome(page) -> None:
    t.sleep(2)
    id_box = page.find_element(By.XPATH,'//input[@id="user_id"]')
    login_button_1 = page.find_element(By.XPATH,'//button[@id="loginStart"]')
    id = works_login['id']
    ActionChains(page).send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()
    t.sleep(1)
    password_box = page.find_element(By.XPATH,'//input[@id="user_pwd"]')
    login_button_2 = page.find_element(By.XPATH,'//button[@id="loginBtn"]')
    password = works_login['pw']
    ActionChains(page).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
    t.sleep(2)
    page.get("https://mail.worksmobile.com/#/my/103")
#엔팩스 메일 확인
def newFax(page) -> None:
    page.refresh()
    t.sleep(2)
    mailHome_soup = BeautifulSoup(page.page_source,'html.parser')
    if mailHome_soup.find('li', attrs={'class':'notRead'}) != None:
        newMail = page.find_element(By.XPATH,"//li[contains(@class,'notRead')]//div[@class='mTitle']//strong[@class='mail_title']")
        ActionChains(page).click(newMail).perform()
        t.sleep(1)
        download = page.find_element(By.XPATH,'//button[@class="btn_down_pc"]')
        ActionChains(page).click(download).perform()
        t.sleep(0.5)
        mail_soup = BeautifulSoup(page.page_source,'html.parser')
        faxNumber = mail_soup.find('span',attrs={'class':'subject'}).getText().replace(' ','').split("hecto_2f에")[1].split("로부터")[0]
        fileName = mail_soup.find('a',attrs={'class':'file_name_txt'}).getText()
        url = f"https://api.telegram.org/bot{bot_info['token']}/sendDocument"
        with open(f"C:\\Users\\USER\\Downloads\\{fileName}","rb") as file:
            requests.post(url, data={"chat_id":bot_info['chatId']}, files={"document":file})
        if faxNumber in fax['faxNumber'].tolist():
            tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {fax[fax['faxNumber'].isin([faxNumber])]['원천사'].reset_index(drop=True)[0]}"
            requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
        else:
            tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
            requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
        page.get("https://mail.worksmobile.com/#/my/103")
    else:pass
def main() -> None:
    reset_time = t.time()
    while True:
        try:
            options = Options()
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            driver = webdriver.Firefox(options=options)
            driver.get("https://mail.worksmobile.com/")
            getHome(driver)
            browser_runtime = 600
            max_runtime = 1800
            start_time = t.time()
            while t.time()-start_time < browser_runtime:
                print(int(t.time()-start_time))
                newFax(driver)
                t.sleep(10)
            requests.get(f"https://api.telegram.org/bot{bot_HC['token']}/sendMessage?chat_id={bot_HC['chatId']}&text=브라우저_재시작")
            t.sleep(2)
            driver.quit()
            if t.time()-reset_time >= max_runtime:
                requests.get(f"https://api.telegram.org/bot{bot_HC['token']}/sendMessage?chat_id={bot_HC['chatId']}&text=스크립트_재시작")
                t.sleep(2)
                driver.quit()
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:pass
        except Exception as e:
            requests.get(f"https://api.telegram.org/bot{bot_HC['token']}/sendMessage?chat_id={bot_HC['chatId']}&text=오류발생:{e}")
            driver.quit()
            t.sleep(2)
            os.execl(sys.executable, sys.executable, *sys.argv)
if __name__ == "__main__":main()