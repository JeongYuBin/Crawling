import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException

# 크롤링을 하려고 진행을 할때, 헤더에 봇이 아닌 일반 크롬이 들어가도록 해야 한다
# 참고 url : https://m.blog.naver.com/shino1025/221305380045

# .env 파일 로드
# .env 파일에는 총 3개의 속성이 있어야 한다.
# EVERYTIME_ID , EVERYTIME_PW , MONGO_URI(데이터베이스가 명시되어 있는)

load_dotenv()
ID = os.getenv("EVERYTIME_ID")
PW = os.getenv("EVERYTIME_PW")

# Chrome 설정
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    """
})

try:
    driver.get("https://account.everytime.kr/login")
    time.sleep(2)

    driver.find_element(By.XPATH, '/html/body/div[1]/div/form/div[1]/input[1]').send_keys(ID)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/form/div[1]/input[2]').send_keys(PW)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/form/input').click()
    time.sleep(3)

    try:
        alert = driver.switch_to.alert
        print(f"🚨 알림창 감지: {alert.text}")
        alert.accept()
        print("❌ 로그인 실패 - 알림창 수락 후 종료")
        driver.quit()
        exit()
    except NoAlertPresentException:
        print("알림창 없음")

    print("로그인 성공")

    driver.get("https://everytime.kr/timetable")
    time.sleep(2)

    driver.find_element(By.XPATH, '//*[@id="container"]/ul/li[1]').click()
    time.sleep(2)

    print("시간표 첫 페이지 도착 완료")

    # 무한 스크롤 로직
    scroll_container = driver.find_element(By.XPATH, '//*[@id="subjects"]/div[2]')
    prev_tr_count = 0
    scroll_attempts = 0

    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
        time.sleep(1.5)  # 스크롤 후 데이터 로딩 대기

        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        curr_tr_count = len(rows)
        print(f"현재까지 로드된 강의 수: {curr_tr_count}")

        if curr_tr_count == prev_tr_count:
            scroll_attempts += 1
            if scroll_attempts >= 3:  # 3번 연속 변화 없으면 종료
                break
        else:
            scroll_attempts = 0
            prev_tr_count = curr_tr_count

    print(f"전체 로딩 완료. 총 {curr_tr_count}개의 강의 수집 시작")

    # MongoDB 연결
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["class"]    
    collection_name = "2025-1"    # collection_name 의 경우 해당 부분으로 설정하였으나 추후 자동화 작업에서 수정 해야한다
    collection = db[collection_name]

    for row in rows:
        try:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 6:
                continue

            class_idx = tds[1].text.strip()
            class_name = tds[2].text.strip()
            prof_name = tds[3].text.strip()
            class_credit = tds[4].text.strip()
            class_daytime = tds[5].text.strip()

            if not class_idx:
                continue

            result = collection.update_one(
                {"class_idx": class_idx},
                {
                    "$set": {
                        "class_name": class_name,
                        "prof_name": prof_name,
                        "class_credit": class_credit,
                        "class_daytime": class_daytime
                    }
                },
                upsert=False
            )

            if result.modified_count > 0:
                print(f"✅ 업데이트됨: {class_idx}")
            else:
                print(f"➖ 이미 존재 또는 없음: {class_idx}")

        except Exception as e:
            print("⚠️ 개별 항목 처리 오류:", e)

except Exception as e:
    print("오류 발생:", e)

finally:
    driver.quit()
    print("전체 작업 완료")
