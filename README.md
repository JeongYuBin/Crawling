# Crawling

## klas-lecture-plan-crwler
해당 크롤링은 광운대학교 강의계획서를 크롤링하여 각 강의실의 강의실 위치 정보를 가져오는 코드입니다.
먼저 klas 및 강의계획서까지의 과정을 제공해준 민혁님에게 감사를 표합니다.

사용한 DB의 경우 MongoDB를 사용하였으며,  MongoDB안에 강의명(class_name)과 학정 번호(class_idx)가 있다는 조건으로 크롤링이 진행됩니다. 
해당 강의명과 학정 번호의 경우 '광운대학교 수강신청 자료집'에서 수집한 데이터 이며 이외에도 '교수명', '강의 시간', '학점'의 정보가 DB에 담겨져 있지만
해당 데이터는 사용하지 않았습니다.

추가적으로 .env 파일에 해당 DB와 연결되는 MONGO_URI 와 klas에 로그인 하기 위한 ID 및 PASSWORD 를 작성해야 합니다. 

### .env 예시
``` 
ID = 2020000000
PASSWORD = password
MONGO_URI = mongodb+srv://~~~
```

동작 순서
klas 로그인 -> 강의 게획서 -> 입력란에 강의명 입력(DB에 있는 class_name을 가져와서) -> 결과물에 대해 차례대로 들어가기 -> 들어간 후, 해당 강의 계획서의 학정 번호와 DB에 있는 학정 번호(class_idx)를 비교하여서 일치 하는 데이터에 classroom_idx 업데이트(classroom_idx의 경우 강의 계획서에 있는 강의실 위치의 xPath를 가져온다) -> 뒤로가기 -> 다음 결과물로 들어가기 .... -> 한 과목에 대해 모두 돌고나서 다음이 없으면 앞에서 입력하지 않은 다른 교과명 입력 -> (반복)

![Image](https://github.com/user-attachments/assets/40ebc7b0-02ee-48ca-ad78-31c7037967ea)

![Image](https://github.com/user-attachments/assets/2cc4eb9b-ccb7-43fb-97e8-81fcbe18e4e1)

![Image](https://github.com/user-attachments/assets/d84d9ae5-4cab-4dfd-b1e5-a58af62693c7)

![Image](https://github.com/user-attachments/assets/52c77f64-f62b-4655-894d-bd1920675625)

## kwangwoon-notice

해당 크롤링은 광운대학교 공지사항을 크롤링한 코드이며, 공지사항의 title, url, 작성일, 수정일 총 4개를 가져왔다.
단, 해당 크롤링의 경우 광운대학교 공지사항의 1페이지만을 가져온 코드이다. 

![image](https://github.com/user-attachments/assets/3a635b54-c016-48a0-8ebb-b73626cbb2e3)

다음은 2025년 04월 08일 기준의 광운대학교 공지사항의 일부 사항을 .json 형태로 보여준 것이다.
