import time
import json
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#DB정보 호출
with open('C:\\Users\\USER\\ve_1\\DB\\3loginInfo.json', 'r',encoding='utf-8') as f:
    login = json.load(f)
with open('C:\\Users\\USER\\ve_1\\DB\\6faxInfo.json', 'r',encoding='utf-8') as f:
    fax_info = json.load(f)
login_info = pd.Series(login['nFax'])
bot_info = pd.Series(login['nFaxbot'])
fax = pd.DataFrame(fax_info)
#크롬 옵션설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=options)
#크롬 드라이버 실행
driver.get("https://www.enfax.com/common/login")
driver.implicitly_wait(1)
#로그인 정보입력(아이디)
id_box = driver.find_element(By.XPATH,'//input[@id="userId"]')
id = login_info['id']
ActionChains(driver).send_keys_to_element(id_box, '{}'.format(id)).perform()
#로그인 정보입력(비밀번호)
password_box = driver.find_element(By.XPATH,'//input[@id="userPwd"]')
login_button_2 = driver.find_element(By.XPATH,'//button[@id="btnLogin"]')
password = login_info['pw']
ActionChains(driver).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
time.sleep(2)
def faxCheck():
    driver.get("https://www.enfax.com/fax/view/receive")
    time.sleep(2)
    #타임 스케쥴 진행
    fax_soup = BeautifulSoup(driver.page_source,'html.parser')
    newfax = fax_soup.find('span', attrs={'class':'state_box stt_notread'})
    #요소 검증
    if newfax != None:
        #수신확인
        if newfax.get_text()=="안읽음":
            if fax_soup.find('div', attrs={'class':'t_row stt_notread faxReceiveBoxListRow'}) != None:
                faxNumber = fax_soup.find('div', attrs={'class':'t_row stt_notread faxReceiveBoxListRow'}).get('data-send-fax-number')
            else:
                faxNumber = "확인불가"
            if faxNumber in fax.loc['faxNumber'].tolist():
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {fax[fax['faxNumber'] == faxNumber]['원천사'].values}"
                #텔레그램 전송
                requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
                time.sleep(2)
            else:
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
                #텔레그램 전송
                requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
                time.sleep(2)
        else:
            time.sleep(8)
            pass
    else:
        time.sleep(8)
        pass
if __name__ == "__main__":
    while True:
        faxCheck()
        time.sleep(0.1)