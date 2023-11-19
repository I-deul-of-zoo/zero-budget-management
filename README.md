# (3차 과제) Budget management application

## 목차
- [개요](#개요)
- [요구사항](#요구사항)
- [개발환경세팅](#개발환경세팅)
- [Installation & Run](#Installation)
- [ER-Diagram](#ER-Diagram)
- [API Documentation](#API)
- [프로젝트 진행 및 이슈 관리](#프로젝트)
- [구현과정(설계 및 의도)](#구현과정)
- [TIL 및 회고](#TIL)
- [Authors](#Authors)



## 개요
개개인의 재무를 관리 할 수 있도록하며 지출을 추적하는데 도움을 주는 애플리케이션입니다. 이 앱은 사용자들이 
예산을 책정하고 적정한 지출을 할 수 있도록 하며 지출을 모니터링 하며 재무 목표를 달성하는데 도움을 줍니다.


### 유저히스토리
- **A. 유저는 본 사이트에 들어와 회원가입을 통해 서비스를 이용합니다**
- **B. 예산 설정 및 설계 서비스**
    - `월별` 총 예산을 설정합니다.
    - 본 서비스는 `카테고리` 별 예산을 설계(=추천)하여 사용자의 과다 지출을 방지합니다.
- **C. 지출 기록**
    - 사용자는 `지출`을 `금액`.`카테고리` 등을 지정하여 등록 합니다. 언제든지 수정 및 삭제 할 수 있습니다.
- **D. 지출 컨설팅**
    - `월별` 설정한 예산을 기준으로 오늘 소비 가능한 `지출`을 알려줍니다.
    - 매일 발생한 `지출`을 `카테고리` 별로 안내받습니다.
- **E. 지출 통계**
    - `지난 달 대비`,`지난 요일 대비`, `다른 유저 대비`등 여러 기중 `카테고리 별` 지출 통계를 확인 할 수 있습니다. 


## 요구사항 및 구현사항

### A. 유저

#### 사용자 회원가입(API)
- 본 서비스에서는 유저 고유 정보가 크게 사용되지 않아 간단히 구현합니다.
- `계정명` , `패스워드` 입력하여 회원가입

#### 사용자 로그인(API)
- `계정`, `비밀번호` 로 로그시 `JWT` 가 발급됩니다.
- 이후 모든 API 요청 Header 에 `JWT` 가 항시 포함되며, `JWT` 유효성을 검증합니다.

#### 사용자 설정 업데이트(API)
- 사용자의 위치 인 `위도`, `경도` 를 업데이트 합니다.
    - 시구군 API로 제공되는 위치 정보 이용
- `점심 추천 기능 사용 여부` 를 업데이트 합니다.
    - 하위 점심추천 기능을 받을지 설정합니다.

### B. 예산설정 및 설계

#### 카테고리

- 카테고리는 `식비` , `교통` 등 일반적인 지출 카테고리를 의미합니다.
- 자유롭게 구성하여 생성하세요.

#### 카테고리 목록(API)

- 유저가 예산설정에 사용할 수 있도록 모든 카테고리 목록을 반환합니다.

#### 예산 설정(API)

- 해당 기간 별 설정한 `예산` 을 설정합니다. 예산은 `카테고리` 를 필수로 지정합니다.
    - ex) `식비` : 40만원, `교통` : 20만원
- 사용자는 언제든지 위 정보를 변경할 수 있습니다.
- 예산 설정을 함으로써 이후 한달 간의 각 `카테고리`의 적정 지출량을 정해줍니다.
- 또한 예산이 변경 됨에 따라 변경 된 만큼과 남은 기간의 적정 지출량을 새로이 지정해줍니다.

'''
    새로운 적정 예산 = ( 새로운 에산 - 이전 예산) / 남은 기간  + 원래 있던 적정 예산
    남은 기간  =  (created_at 한달뒤 날짜  - 현재 날짜 차이)
'''

#### 예산 설계 (=추천) (API)

- 카테고리 별 예산 설정에 어려움이 있는 사용자를 위해 예산 비율 추천 기능이 존재합니다.
- `카테고리` 지정 없이 총액 (ex. 100만원) 을 입력하면, `카테고리` 별 예산을 자동 생성합니다.
- 자동 생성된 예산은, 기존 이용중인 `유저` 들이 설정한 평균 값 입니다.
    - 유저들이 설정한 카테고리 별 예산을 통계하여, 평균적으로 40% 를 `식비`에, 30%를 `주거` 에 설정 하였다면 이에 맞게 추천.
    - 10% 이하의 카테고리들은 모두 묶어 `기타` 로 제공한다.(8% 문화, 7% 레져 라면 15% 기타로 표기)
    - **위 비율에 따라 금액이 입력됩니다.**
        - **ex) 식비 40만원, 주거 30만원, 취미 13만원 등.**

- 예산 설계 추천 또한 예산 설정과 같이 적정 지출 금액을 산출합니다. 

### C. 지출 기록

#### 지출

- `지출 일시`, `지출 금액`, `카테고리` 와 `메모` 를 입력하여 생성합니다
    - 추가적인 필드 자유롭게 사용

#### 지출 CRUD (API)

- 지출을 `생성`, `수정`, `읽기(상세)`, `읽기(목록)`, `삭제` , `합계제외` 할 수 있습니다.
- `생성한 유저`만 위 권한을 가집니다.
- `읽기(목록)` 은 아래 기능을 가지고 있습니다.
    - 필수적으로 `기간` 으로 조회 합니다.
    - 조회된 모든 내용의 `지출 합계` , `카테고리 별 지출 합계` 를 같이 반환합니다.
    - 특정 `카테고리` 만 조회.
    - `최소` , `최대` 금액으로 조회.
        - ex) 0~10000원 / 20000원 ~ 100000원
- `합계제외` 처리한 지출은 목록에 포함되지만, 모든 `지출 합계`에서 제외됩니다.

### D. 지출 컨설팅

#### 오늘 지출 추천(API)

- 설정한 `월별` 예산을 만족하기 위해 오늘 지출 가능한 금액을 `총액` 과 `카테고리 별 금액` 으로 제공합니다.
    - ex) 11월 9일 지출 가능 금액 총 30,000원, 식비 15,000 … 으로 페이지에 노출 예정.
- 고려사항 1. 앞선 일자에서 과다 소비하였다 해서 오늘 예산을 극히 줄이는것이 아니라, 이후 일자에 부담을 분배한다.
    - 앞선 일자에서 사용가능한 금액을 1만원 초과했다 하더라도, 오늘 예산이 1만원 주는것이 아닌 남은 기간 동안 분배해서 부담(10일 남았다면 1천원 씩).
- 고려사항 2. 기간 전체 예산을 초과 하더라도 `0원` 또는 `음수` 의 예산을 추천받지 않아야 합니다.
    - 지속적인 소비 습관을 생성하기 위한 서비스이므로 예산을 초과하더라도 적정한 금액을 추천받아야 합니다.
    - `최소 금액`을 10000원으로 설정 하였습니다.
- 유저의 상황에 맞는 1 문장의 `멘트` 노출.
    - 잘 아끼고 있을 때, 적당히 사용 중 일 때, 기준을 넘었을때, 예산을 초과하였을 때 등 유저의 상황에 맞는 메세지를 같이 노출합니다.
    - 조건과 기준은 자유롭게 설정하세요.
    - ex) “절약을 잘 실천하고 계세요! 오늘도 절약 도전!” 등
- 15333원 과 같은 값이라면 백원 단위 반올림 등으로 사용자 친화적이게 변환.
- **선택 구현 기능)** 매일 08:00 시 알림 발송
    - Celery, Redis를 이용한 Scheduler 추가 구현 예정

#### 오늘 지출 안내(API)

- 오늘 지출한 내용을 `총액` 과 `카테고리 별 금액` 을 알려줍니다.
- `월별`설정한 예산 기준 `카테고리 별` 통계 제공
    - 일자기준 오늘 `적정 금액` : 오늘 기준 사용했으면 적절했을 금액
- 일자기준 오늘 `지출 금액` : 오늘 기준 사용한 금액
- `위험도` : 카테고리 별 적정 금액, 지출금액의 차이를 위험도로 나타내며 %(퍼센테이지) 입니다.
    - ex) 오늘 사용하면 적당한 금액 10,000원/ 사용한 금액 20,000원 이면 200%
- **선택 구현 기능)** 매일 20:00 시 알림 발송
    - Celery, Redis를 이용한 Scheduler 추가 구현 예정

## E. 지출 통계

### Dummy 데이터 생성

- 사용자의 통계데이터 생성을 위해 Dummy 데이터를 생성합니다.

### 지출 통계 (API)

- `지난 달` 대비 `총액`, `카테고리 별` 소비율.
    - 오늘이 10일차 라면, 지난달 10일차 까지의 데이터를 대상으로 비교
    - ex) `식비` 지난달 대비 150%
- `지난 요일` 대비 소비율
    - 오늘이 `월요일` 이라면 지난 `월요일` 에 소비한 모든 기록 대비 소비율
    - ex) `월요일` 평소 대비 80%
- `다른 유저` 대비 소비율
    - 오늘 기준 다른 `유저` 가 예산 대비 사용한 평균 비율 대비 나의 소비율
    - 오늘기준 다른 유저가 소비한 지출이 평균 50%(ex. 예산 100만원 중 50만원 소비중) 이고 나는 60% 이면 120%.
    - ex) `다른 사용자` 대비 120%

### 개발환경세팅
가상환경: ![pyenv](https://img.shields.io/badge/pyenv-pyenv-red)

언어 및 프레임워크: ![Python](https://img.shields.io/badge/python-3670A0?&logo=python&logoColor=ffdd54) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?&logo=django&logoColor=white&color=ff1709&labelColor=gray)

데이터 베이스: ![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?&logo=mysql&logoColor=white)


## Installation & Run
### MySQL DB 세팅
- DATABASE생성
    - DB_NAME=foodie
    - DB_HOST=localhost
    - DB_PORT=3306
- USER생성
    - DB_USER=dubdget
    - 유저에게 db권한주기

### 환경 세팅

## 2️⃣ 애플리케이션의 실행 방법 (엔드포인트 호출 방법 포함)
(전제) `python >= 3.10` 과 `mysql >= 8.0` 은 설치되어 있습니다.

#### 1. pyenv와 poetry를 이용해서 가상환경을 세팅해줍니다.
1. pip를 이용해서 pyenv와 poetry를 설치해줍니다.
```
pip install pyenv poetry
```
2. 가상환경을 만드는 명령어
```
pyenv virtualenv (python-version) <environment_name>
(EX. pyenv virtualenv 3.10 foodie)
```
3. (선택) 가상환경이 만들어졌는지 확인 명령어
```
pyenv versions
```
4. 가상환경 활성화 
```
pyenv activate <가상환경이름>
```
- windows os는 pyenv를 지원하지 않아 pyenv-win을 설치해야 합니다.
- 또는 windows 상에서 ubuntu를 사용할 수 있도록 해주는 wsl2를 이용하여 리눅스 상에 pyenv와 poetry를 설치 할 수 있습니다.

#### 2. `pyproject.toml` 을 통해 동일한 환경을 만들어줍니다.
```
poetry install
```
- 위의 명령어 입력시, 현 폴더 위치에 `poetry.lock` 파일 생성 or 업데이트

#### 3. `manage.py` 가 있는 위치에서 모델 migration을 해줍니다.
```
(pyenv run) python manage.py migrate
```
[참고]
- `python manage.py makemigrations` : 아직 데이터베이스에 적용되지 않음, 데이터베이스 스키마 변경사항을 기록하는 용
- `python manage.py migrate` : 위의 명령어에서 생성된 마이그레이션 파일들을 데이터베이스에 적용
(지금은 두번째 명령어만 작성하는게 맞습니다. 변경사항 없이 DB에 적용하기 위함이기 때문입니다.)

#### 4. `manage.py` 가 있는 위치에서 서버를 실행합니다.
```
(pyenv run) python manage.py runserver [port_num]
```
- 필요에 따라 위의 명령어 뒤에 포트번호를 붙입니다.

#### 5. End-point 호출 방법 
[참고] Django REST Framework는 admin 패널을 제공합니다. Postman을 사용하지 않아도 (header인증 제외) 웹 상으로 request/response가 가능합니다.


## ER-Diagram
<img width="800" alt="ER-Diagram" src="https://github.com/airhac/wanted-pre-onboarding-backend/assets/86655679/759f1e15-f657-45c8-a66d-f20f35ec0fca">

<br>

## API Documentation
<img width="800" alt="ER-Diagram" src="https://github.com/airhac/wanted-pre-onboarding-backend/assets/86655679/50835226-ac7b-4031-9ab8-4b270115f689">

<!-- [TODO]
아래의 details 태그 안에 각자 구현한 부분 Request/Response 작성하기 -->

<details>
<summary>1. 회원가입 API - click</summary>

#### Request
```plain
  POST /api/auths/registration
```
- Auth Required: False

| Body Parameter | Type     | Description    |
| :------------- | :------- | :------------- |
| `username`     | `string` | **Required**.  |
| `password`     | `string` | **Required**.  |
```
EX)
{
    "username": "user1",
    "password": "devpassword1"
}
```

#### Response
```http
HTTP 201 Created
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "username": "user1"
}
```
</details>

<details>
<summary>2. 로그인 API - click</summary>

#### Request
```plain
  POST /api/auths/login
```
- Auth Required: False

| Body Parameter | Type     | Description    |
| :------------- | :------- | :------------- |
| `username`     | `string` | **Required**.  |
| `password`     | `string` | **Required**.  |

```
EX)
{
    "username": "user1",
    "password": "devpassword1"
}
```

#### Response
```http
HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "username": "user1",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpVXCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk5NDM2NTA3LCJpYXQiOjE2OTk0MzI5MDcsImp0aSI6Ijc4Y2E1NzI3NDZkMDQzYzA4ZWZlNWM3NGNjMDFkNDNiIiwidXNlcl9pZCI6MX0.W-z5wAg0zNJWlaLA6mb0xEMPeEdOqenKeKrCsenWCNs",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpVXC..."
}
```
</details>

<details>
<summary>3. 카테고리 목록 API </summary>

#### Request
```plain
  GET /api/budgets
```
- Auth Required: True

#### Rquest Header

| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |

#### Response
```
[
    {
        "id": 1,
        "name": "식비"
    },
    {
        "id": 2,
        "name": "주거"
    },
    {
        "id": 3,
        "name": "취미"
    },
    {
        "id": 4,
        "name": "교통비"
    },
    {
        "id": 5,
        "name": "저축"
    },
    {
        "id": 6,
        "name": "보험비"
    },
    {
        "id": 7,
        "name": "주식"
    },
    {
        "id": 8,
        "name": "기타"
    }
]
```

</details>
<details>
<summary>4. 예산 설정(API)</summary>

#### Request
```plain
  POST api/budegets
  {
   "category" : {
       "식비" : 1000000,
       "주식" : 500000,
       "주거" : 500000,
   }
}
```
- Auth Required: True
- 'category안 dict에 넣어야함'
| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `식비`     | `string` | **Required**.         |
| `주거`    | `string` | **Required*            |
| `취미` | `string` | **Required**.             |
| `교통비` | `string` | **Required**.             |
| `저출` | `string` | **Required**.             |
| `보험비` | `string` | **Required**.             |
| `주식` | `string` | **Required**.             |
| `기타` | `string` | **Required**.             |



#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{"objects":[{"category":1},{"category":2},{"category":3},{"category":4},{"category":5},{"category":6},{"category":7},{"category":8}]}
```
</details>

<details>
<summary>5. 예산 수정(API)</summary>

#### Request
```plain
  PATCH api/budegets
  {
   "category" : {
       "식비" : 1000000,
       "주식" : 700000,
       "주거" : 600000,
   }
}
```
- Auth Required: True
- 'category안 dict에 넣어야함'
| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `식비`     | `string` | **Required**.         |
| `주거`    | `string` | **Required*            |
| `취미` | `string` | **Required**.             |
| `교통비` | `string` | **Required**.             |
| `저출` | `string` | **Required**.             |
| `보험비` | `string` | **Required**.             |
| `주식` | `string` | **Required**.             |
| `기타` | `string` | **Required**.             |



#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{"objects":[{"category":1},{"category":2},{"category":7}]}

```
</details>

<details>
<summary>6. 예산 설게(=추천)(API)</summary>

#### Request
```plain
  POST api/budegets
  {
   "total" : 4000000, 
}
```
- Auth Required: True

| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `total`     | `string` | **Required**. 전체 예산        |



#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{"objects":[{"category":1},{"category":2},{"category":3},{"category":4},{"category":5},{"category":6},{"category":7},{"category":8}]}
```
</details>

<details>
<summary>7. 예산 설게(=추천)(API) 수정</summary>

#### Request
```plain
  UPDATE api/budegets
  {
   "total" : 4000000, 
}
```
- Auth Required: True

| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `total`     | `string` | **Required**. 전체 예산        |



#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{"objects":[{"category":1},{"category":2},{"category":3},{"category":4},{"category":5},{"category":6},{"category":7},{"category":8}]}
```
</details>

<details>
<summary>8. 지출 목록(API)</summary>

#### Request
```plain
  GET api/expenditures/

```
- Auth Required: True


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

[
    {
        "user_id": 1,
        "consumption_amount": 3000,
        "category_id": 1,
        "content": "부스터",
        "is_except": false,
        "total_expend": 48000,
        "total_expend_category": [
            {
                "category_id": 2,
                "total_consumption": 30000
            },
            {
                "category_id": 3,
                "total_consumption": 15000
            },
            {
                "category_id": 1,
                "total_consumption": 3000
            }
        ],
        "created_at": "2023-11-19T14:13:21.835845",
        "reasonable_amount": 33300
    },
    {
        "user_id": 1,
        "consumption_amount": 15000,
        "category_id": 3,
        "content": "헬스장",
        "is_except": false,
        "total_expend": 48000,
        "total_expend_category": [
            {
                "category_id": 2,
                "total_consumption": 30000
            },
            {
                "category_id": 3,
                "total_consumption": 15000
            },
            {
                "category_id": 1,
                "total_consumption": 3000
            }
        ],
        "created_at": "2023-11-19T14:12:50.827842",
        "reasonable_amount": 0
    },
    {
        "user_id": 1,
        "consumption_amount": 30000,
        "category_id": 2,
        "content": "관리비",
        "is_except": false,
        "total_expend": 48000,
        "total_expend_category": [
            {
                "category_id": 2,
                "total_consumption": 30000
            },
            {
                "category_id": 3,
                "total_consumption": 15000
            },
            {
                "category_id": 1,
                "total_consumption": 3000
            }
        ],
        "created_at": "2023-11-19T14:06:11.840171",
        "reasonable_amount": 16600
    }
]

```
</details>

<details>
<summary>9. 지출 기록(API)</summary>

#### Request
```plain
  POST api/expenditures/
{
    "consumption_amount":int,
    "category_id": char,
    "content": char,
    "is_except" : Boolen
    }
```
- Auth Required: True

| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `consumption_amount`     | `int` | **Required**.         |
| `category_id`    | `string` | **Required**.            |
| `content` | `string` | **Required**.             |
| `is_except` | `boolen` | **Required**.             |


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{"user_id":1,"consumption_amount":30000,"category_id":2,"content":"관리비"}

```
</details>

<details>
<summary>10. 지출 상세(API)</summary>

#### Request
```plain
  GET api/expenditures/<int:pk>/
```
- Auth Required: True


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{
    "user_id": 1,
    "consumption_amount": 15000,
    "category_id": 3,
    "content": "헬스장",
    "is_except": false
}

```
</details>

<details>
<summary>11. 지출 수정(API)</summary>

#### Request
```plain
 PATCH api/expenditures/<int:pk>/
{
    "consumption_amount" : 15500
    }
```
- Auth Required: True

| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `consumption_amount`     | `int` | **Required**.         |
| `category_id`    | `string` | **Required**.            |
| `content` | `string` | **Required**.             |
| `is_except` | `boolen` | **Required**.             |


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http
{
    "user_id": 1,
    "consumption_amount": 15500,
    "category_id": 3,
    "content": "헬스장",
    "is_except": false
}

```
</details>

<details>
<summary>12. 지출 삭제(API)</summary>

#### Request
```plain
 DELETE api/expenditures/<int:pk>/

```
- Auth Required: True

| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `consumption_amount`     | `int` | **Required**.         |
| `category_id`    | `string` | **Required**.            |
| `content` | `string` | **Required**.             |
| `is_except` | `boolen` | **Required**.             |


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http
DELETE /api/expenditures/2/ HTTP/1.1" 204 0
```
</details>


<details>
<summary>13. 오늘 지출 추천(API)</summary>

#### Request
```plain
GET api/expenditures/rec/

```
- Auth Required: True


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{   "user":1,
    "total":66500,
    "category_total":{"1":33300,"2":16600,"3":0,"4":0,"5":0,"6":0,"7":16600,"8":0},
    "datetime":"2023-11-19",
    "content":"절약을 잘 실천하고 계세요! 오늘도 절약 도전"
}
```
</details>

<details>
<summary>14. 오늘 지출 안내(API)</summary>

#### Request
```plain
 GET api/expenditures/noti/

```
- Auth Required: True


#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http
=> 더미데이터 생성후 진행가능 지금 더미데이터 작성중
```
</details>


## 프로젝트 진행 및 이슈 관리
- issue와 project로 등록해서 관리했습니다.

<img width="800" alt="ER-Diagram" src="https://github.com/airhac/wanted-pre-onboarding-backend/assets/86655679/8e0ceeca-e269-4a9c-9a69-2213525d9019">


<br>

## 구현과정(설계 및 의도)

1. 환경설정
    - 공통의 환경을 구축하는 것이 중요하다고 생각해서 아래와 같이 환경설정을 진행하였습니다.
        - window os: wsl2 + Ubuntu 22.04을 세팅  
        - linux(mac) os: brew & pip 사용
    - 아래와 같이 로컬의 개발환경을 세팅하는 것으로 결정했습니다.
        - Pyenv 로 python 버전 통일 3.11.6 및 가상환경 생성
        - Poetry 로 패키지 관리

<br>

##  회고

## 일정 관리
- 요구사항 분석 이후 작업 가능한 최소 단위의 task로 업무를 나누었습니다.

<img width="800" alt="ER-Diagram" src="https://github.com/I-deul-of-zoo/zero-budget-management/assets/86655679/b92507f5-158e-4a03-8203-2327feca7b7b">
<br>

## Authors

|이름|github주소|
|---|---------|
|오동혁|https://github.com/airhac|
