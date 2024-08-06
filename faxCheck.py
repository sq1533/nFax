import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#로그인 정보 호출
with open('C:\\Users\\USER\\ve_1\\nFax\\login.json', 'r') as f:
    login_info = json.load(f)
#Nfax 신규 수신 확인
driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--blink-settings=imagesEnabled=false'))
#크롬 드라이버 실행
driver.get("https://www.enfax.com/common/login")
driver.implicitly_wait(1)
#로그인 정보입력(아이디)
id_box = driver.find_element(By.XPATH,'//input[@id="userId"]')
id = login_info['nFax']['id']
ActionChains(driver).send_keys_to_element(id_box, '{}'.format(id)).perform()
#로그인 정보입력(비밀번호)
password_box = driver.find_element(By.XPATH,'//input[@id="userPwd"]')
login_button_2 = driver.find_element(By.XPATH,'//button[@id="btnLogin"]')
password = login_info['nFax']['pw']
ActionChains(driver).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
time.sleep(2)
def faxCheck():
    driver.get("https://www.enfax.com/fax/view/receive")
    time.sleep(2)
    #타임 스케쥴 진행
    html = driver.page_source
    fax_soup = BeautifulSoup(html,'html.parser')
    checkPoint = [span.get_text() for span in fax_soup.find_all('span', attrs={'class':'state_box stt_notread'})]
    if "안읽음" in checkPoint:
        #텔레그램 전송
        requests.get(f"https://api.telegram.org/bot{login_info['bot']['token']}/sendMessage?chat_id={login_info['bot']['chatId']}&text=신규 팩스 수신, 확인필요")
    else:
        pass
if __name__ == "__main__":
    while True:
        faxCheck()
        time.sleep(0.2)