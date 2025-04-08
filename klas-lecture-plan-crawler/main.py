from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import re
from dotenv import load_dotenv
from pymongo import MongoClient
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, ElementNotInteractableException
from pymongo.errors import CursorNotFound

# 환경 변수 로드
load_dotenv()

# MongoDB 연결 설정
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
collection = db["class"]

# Selenium 웹드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def handle_alert():
    try:
        alert = driver.switch_to.alert  # 경고창 처리(폐강 강의 관련)
        alert_text = alert.text
        if "폐강된 강의입니다" in alert_text:
            print("폐강된 강의입니다. 경고창을 닫고 넘어갑니다.")
            alert.accept()   # 경고창을 닫고 다음으로 넘어간다
            return True    # 경고창을 처리하면 True 변환
    except NoAlertPresentException:
        return False   # 경고창이 없으면 False 처리리

def search_and_update(course_name):
    try:
        # 과목명 입력 필드드
        search_field = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div[2]/div[2]/table[1]/tbody/tr[2]/td[1]/input')
        search_field.clear()
        time.sleep(1)  # 입력전 안정성 확보하기기
        search_field.send_keys(course_name)
        
        # 조회 버튼 클릭
        search_button = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div[2]/div[2]/div/button')
        search_button.click()
        time.sleep(3)
        
        # 검색 결과 찾기
        results = driver.find_elements(By.XPATH, '/html/body/main/div/div/div/div[2]/div[2]/table[2]/tbody/tr')
        
        for i in range(len(results)):
            try:
                results = driver.find_elements(By.XPATH, '/html/body/main/div/div/div/div[2]/div[2]/table[2]/tbody/tr')
                results[i].click()
                time.sleep(5)
                
                if handle_alert():
                    continue
                
                class_idx_element = driver.find_element(By.XPATH, '//*[@id="appModule"]/div[2]/div[2]/table[1]/tbody/tr[2]/td[1]')
                class_idx = class_idx_element.text.strip()
                
                # db 에서 class_idx 있는지 찾기 
                class_in_db = collection.find_one({"class_idx": class_idx})
                if class_in_db:
                    classroom_element = driver.find_element(By.XPATH, '//*[@id="appModule"]/div[2]/div[2]/table[1]/tbody/tr[4]/td[1]')
                    classroom_text = classroom_element.text.strip()
                    matches = re.findall(r'\((.*?)\)', classroom_text)
                    classroom_idx = ', '.join(set(matches)) if matches else ""
                    
                    print(f"강의명: {course_name}, 강의 ID: {class_idx}, 강의실: {classroom_idx}")
                    
                    # db에 강의실 정보 업데이트 
                    collection.update_one(
                        {"class_idx": class_idx}, 
                        {"$set": {"classroom_idx": classroom_idx}}, 
                        upsert=True
                    )
                
                # 뒤로가기 버튼(과목 조회하는 곳으로 돌아가기)
                back_button = driver.find_element(By.XPATH, '//*[@id="appModule"]/div[2]/div[2]/div/button')
                back_button.click()
                time.sleep(3)
            except UnexpectedAlertPresentException:  # 경고창을 닫고 다음 결과로 넘어가기기
                if handle_alert():
                    continue
            except Exception as e:
                print(f"오류 발생: {e}")
                continue  # 오류가 발생해도 계속해서 진행행
    except ElementNotInteractableException:
        print(f"입력 필드 비활성화 오류 발생: {course_name} 검색 시 문제 발생")
    except Exception as e:
        print(f"검색 오류 발생: {e}")

# 커서 타임아웃 문제 처리리
def handle_cursor_timeout():
    while True:
        try:
            return list(collection.find({}, {"class_name": 1, "_id": 0}).batch_size(10))
        except CursorNotFound:
            print("커서가 만료되었습니다. 다시 시도합니다.")
            time.sleep(1)

try:
    driver.get("https://klas.kw.ac.kr/usr/cmn/login/LoginForm.do")
    time.sleep(2)
    
    id_field = driver.find_element(By.XPATH, '//*[@id="loginId"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="loginPwd"]')
    id_field.send_keys(os.getenv("ID"))
    password_field.send_keys(os.getenv("PASSWORD"))
    
    login_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/form/div[2]/button')
    login_button.click()
    time.sleep(5)
    
    driver.get("https://klas.kw.ac.kr/std/cps/atnlc/LectrePlanStdPage.do")
    time.sleep(3)
    
    # 커서 처리 및 과목 검색색
    page_size = 100
    total_courses = collection.count_documents({})  # 총 과목 수
    
    for page in range(0, total_courses, page_size):
        courses = handle_cursor_timeout()[page:page+page_size]
        processed_courses = set()  # 이미 처리한 과목을 저장하며 중복 방지
        
        for course in courses:
            if course["class_name"] in processed_courses:
                continue
            search_and_update(course["class_name"])
            processed_courses.add(course["class_name"])
finally:
    driver.quit()
