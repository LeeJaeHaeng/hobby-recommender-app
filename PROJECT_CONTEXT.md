\# 퇴직자 맞춤 취미 추천 앱 - 프로젝트 전체 컨텍스트



\## 📋 프로젝트 개요



\### 기본 정보

\- \*\*프로젝트명\*\*: 퇴직자 맞춤 취미 추천 및 체험·모임 연결 앱

\- \*\*목적\*\*: 퇴직자들이 개인 성향에 맞는 취미를 발견하고 관련 모임에 참여할 수 있도록 지원

\- \*\*타겟 사용자\*\*: 50대 이상 퇴직자 (디지털 기기 사용이 익숙하지 않을 수 있음)



\### 기술 스택

\- \*\*백엔드\*\*: Python Flask 2.3.3, SQLAlchemy 2.0.21

\- \*\*프론트엔드\*\*: React 18, Material-UI

\- \*\*데이터베이스\*\*: MySQL 8.0.42

\- \*\*머신러닝\*\*: scikit-learn, pandas, numpy

\- \*\*인증\*\*: JWT (추후 구현 예정)



\### 프로젝트 구조

```

C:\\hobby-recommender-app\\

├── backend/

│   ├── app/

│   │   ├── models/

│   │   │   ├── \_\_init\_\_.py

│   │   │   ├── user.py

│   │   │   ├── hobby.py

│   │   │   └── admin.py

│   │   ├── api/           # (생성 예정)

│   │   ├── services/      # (생성 예정)

│   │   └── utils/         # (생성 예정)

│   ├── hobby\_env/         # 가상환경

│   ├── app.py

│   ├── .env

│   └── requirements.txt

└── frontend/

&nbsp;   └── src/

&nbsp;       ├── pages/

&nbsp;       ├── components/

&nbsp;       └── services/

```



---



\## 🎯 핵심 개발 원칙 (반드시 준수)



\### 1. 철저한 예외 처리

```python

\# 모든 API 엔드포인트는 try-catch 사용

@app.route('/api/example')

def example():

&nbsp;   try:

&nbsp;       # 로직

&nbsp;       return jsonify(result), 200

&nbsp;   except ValueError as e:

&nbsp;       logger.error(f"Validation error: {str(e)}")

&nbsp;       return jsonify({'error': '입력값 오류', 'message': str(e)}), 400

&nbsp;   except Exception as e:

&nbsp;       logger.error(f"Unexpected error: {str(e)}", exc\_info=True)

&nbsp;       db.session.rollback()

&nbsp;       return jsonify({'error': '서버 오류'}), 500

```



\### 2. 유지보수성

\- \*\*명확한 변수/함수명\*\* 사용

\- \*\*복잡한 로직에 주석\*\* 추가

\- \*\*중복 코드 제거\*\* (DRY 원칙)

\- \*\*모듈화\*\*: 기능별로 파일 분리



\### 3. 관리자 기능 고려

\- 모든 주요 기능에 관리자 API 제공 (`/api/admin/\*`)

\- 관리자 활동 로그 자동 기록

\- 권한 체크 데코레이터 사용



\### 4. 기본 보안

\- \*\*입력 검증\*\*: 모든 사용자 입력 검증

\- \*\*SQL Injection 방지\*\*: SQLAlchemy ORM 사용

\- \*\*XSS 방지\*\*: 입력값 이스케이프

\- \*\*비밀번호\*\*: bcrypt 해싱

\- \*\*CSRF 토큰\*\*: 추후 구현



---



\## 🎨 UI/UX 원칙 (중장년층 타겟)



\### 필수 적용 사항

1\. \*\*큰 글꼴\*\*: 최소 16px, 중요 텍스트는 18-20px

2\. \*\*높은 대비\*\*: 배경-텍스트 명확한 구분

3\. \*\*단순한 구조\*\*: 한 화면에 하나의 주요 기능

4\. \*\*명확한 라벨\*\*: 아이콘만 사용 금지, 텍스트 병기

5\. \*\*큰 터치 영역\*\*: 버튼 최소 48x48px

6\. \*\*충분한 간격\*\*: 요소 간 여백 확보

7\. \*\*시각적 피드백\*\*: 클릭/호버 시 명확한 반응



\### React 컴포넌트 예시

```jsx

<Button 

&nbsp; variant="contained" 

&nbsp; size="large"

&nbsp; sx={{ 

&nbsp;   fontSize: '18px',

&nbsp;   padding: '16px 32px',

&nbsp;   minHeight: '56px'

&nbsp; }}

>

&nbsp; 취미 찾기 시작하기

</Button>

```



---



\## 🗄️ 데이터베이스 스키마



\### 주요 테이블 (12개)



\#### 1. users - 사용자 기본 정보

```sql

\- user\_id (PK)

\- username, email, password\_hash

\- age, gender, location

\- email\_verified, verification\_token

\- last\_login, failed\_login\_attempts

\- is\_deleted (소프트 삭제)

\- created\_at, updated\_at

```



\#### 2. user\_profiles - 사용자 성향 프로필

```sql

\- profile\_id (PK)

\- user\_id (FK → users)

\- outdoor\_preference (0.00-1.00)

\- social\_preference (0.00-1.00)

\- creative\_preference (0.00-1.00)

\- learning\_preference (0.00-1.00)

\- physical\_activity (0.00-1.00)

\- budget\_level (low/medium/high)

```



\#### 3. survey\_questions - 설문 질문 (20개)

```sql

\- question\_id (PK)

\- question\_text

\- question\_type (scale/choice/binary)

\- category (활동성향/사회성향/학습성향/창의성향 등)

\- options (JSON)

```



\#### 4. survey\_responses - 설문 응답

```sql

\- response\_id (PK)

\- user\_id (FK), question\_id (FK)

\- answer\_value

\- created\_at

```



\#### 5. hobbies - 취미 마스터 데이터 (30개)

```sql

\- hobby\_id (PK)

\- name, category, description

\- difficulty\_level (1-5)

\- indoor\_outdoor (indoor/outdoor/both)

\- social\_individual (social/individual/both)

\- required\_budget (low/medium/high)

\- physical\_intensity (1-5)

\- creativity\_level (1-5)

\- tutorial\_video\_url, image\_url

\- is\_deleted

```



\#### 6. user\_hobby\_ratings - 취미 평가

```sql

\- rating\_id (PK)

\- user\_id (FK), hobby\_id (FK)

\- rating (1-5)

\- review\_text

\- experienced (boolean)

```



\#### 7. gatherings - 모임/동아리 정보

```sql

\- gathering\_id (PK)

\- hobby\_id (FK)

\- name, description, location, region

\- meeting\_type (online/offline/hybrid)

\- schedule\_info, member\_count

\- contact\_info, website\_url

\- is\_active

```



\#### 8. admin\_users - 관리자 계정

```sql

\- admin\_id (PK)

\- username, password\_hash, email

\- role (super\_admin/content\_manager/support)

\- is\_active, last\_login

```



\#### 9. admin\_activity\_logs - 관리자 활동 로그

```sql

\- log\_id (PK)

\- admin\_id (FK)

\- action\_type (CREATE/UPDATE/DELETE/VIEW)

\- target\_table, target\_id

\- action\_details (JSON)

\- ip\_address, user\_agent

```



\#### 10. user\_feedback - 사용자 피드백

```sql

\- feedback\_id (PK)

\- user\_id (FK)

\- feedback\_type (bug/suggestion/question/complaint)

\- subject, content

\- status (pending/in\_progress/resolved/closed)

\- admin\_response, responded\_by (FK → admin\_users)

```



\#### 11. announcements - 공지사항

```sql

\- announcement\_id (PK)

\- title, content

\- announcement\_type (notice/update/maintenance/event)

\- is\_published, is\_pinned

\- published\_at, expires\_at

\- created\_by (FK → admin\_users)

```



\#### 12. user\_notifications - 사용자 알림

```sql

\- notification\_id (PK)

\- user\_id (FK)

\- notification\_type (recommendation/gathering/announcement/system)

\- title, message, link\_url

\- is\_read, read\_at

```



---



\## ✅ 완료된 작업



\### 1단계: 개발 환경 구축 ✅

\- \[x] 프로젝트 폴더 구조 생성

\- \[x] Python 가상환경 설정 (hobby\_env)

\- \[x] MySQL 데이터베이스 생성 (hobby\_recommender)

\- \[x] Flask 백엔드 기본 설정

\- \[x] React 프론트엔드 생성

\- \[x] 필수 패키지 설치



\### 2단계: 데이터베이스 설계 ✅

\- \[x] 12개 테이블 스키마 설계

\- \[x] 제약조건 및 인덱스 추가

\- \[x] 관리자 기능 테이블 추가

\- \[x] 보안 필드 추가 (password\_hash, verification\_token 등)

\- \[x] 소프트 삭제 구현 (is\_deleted)



\### 3단계: 초기 데이터 입력 ✅

\- \[x] 설문 질문 20개 입력

\- \[x] 취미 데이터 30개 입력 (미술, 스포츠, 음악, 공예 등)



\### 4단계: SQLAlchemy 모델 정의 ✅

\- \[x] User, UserProfile 모델

\- \[x] SurveyQuestion, SurveyResponse 모델

\- \[x] Hobby, UserHobbyRating, Gathering 모델

\- \[x] AdminUser, AdminActivityLog 모델

\- \[x] UserFeedback, Announcement, UserNotification 모델

\- \[x] 관계 설정 (relationships)

\- \[x] 제약조건 (CheckConstraint)

\- \[x] 유틸리티 메서드 (to\_dict, set\_password 등)



\### 5단계: Flask 앱 개선 ✅

\- \[x] 에러 핸들러 추가 (400, 404, 500)

\- \[x] 로깅 설정 (파일 + 콘솔)

\- \[x] 헬스 체크 엔드포인트

\- \[x] CLI 명령어 (init\_db, seed\_admin)

\- \[x] Before/After Request 핸들러



\### 6단계: React 기본 페이지 ✅

\- \[x] HomePage 컴포넌트

\- \[x] SurveyPage 컴포넌트

\- \[x] React Router 설정

\- \[x] Material-UI 테마 설정

\- \[x] API 서비스 설정 (axios)



---



\## 🚧 다음 작업 (우선순위)



\### Phase 1: API 개발

1\. \*\*사용자 API\*\* (`/api/users`)

&nbsp;  - \[ ] 회원가입 (POST /api/users/register)

&nbsp;  - \[ ] 로그인 (POST /api/users/login)

&nbsp;  - \[ ] 프로필 조회/수정 (GET/PUT /api/users/<id>)

&nbsp;  - \[ ] 비밀번호 변경



2\. \*\*설문 API\*\* (`/api/survey`)

&nbsp;  - \[ ] 설문 질문 조회 (GET /api/survey/questions)

&nbsp;  - \[ ] 설문 응답 제출 (POST /api/survey/submit)

&nbsp;  - \[ ] 사용자 프로필 생성/업데이트



3\. \*\*취미 API\*\* (`/api/hobbies`)

&nbsp;  - \[ ] 취미 목록 조회 (GET /api/hobbies)

&nbsp;  - \[ ] 취미 상세 조회 (GET /api/hobbies/<id>)

&nbsp;  - \[ ] 취미 평가 (POST /api/hobbies/<id>/rate)

&nbsp;  - \[ ] 카테고리별 조회



4\. \*\*추천 API\*\* (`/api/recommendations`)

&nbsp;  - \[ ] 개인 맞춤 추천 (GET /api/recommendations)

&nbsp;  - \[ ] 추천 알고리즘 구현

&nbsp;  - \[ ] 협업 필터링 + 컨텐츠 기반 필터링



5\. \*\*모임 API\*\* (`/api/gatherings`)

&nbsp;  - \[ ] 취미별 모임 조회

&nbsp;  - \[ ] 지역별 모임 검색



\### Phase 2: 관리자 기능

6\. \*\*관리자 인증\*\* (`/api/admin/auth`)

&nbsp;  - \[ ] 관리자 로그인

&nbsp;  - \[ ] JWT 토큰 발급

&nbsp;  - \[ ] 권한 체크 데코레이터



7\. \*\*관리자 대시보드\*\* (`/api/admin`)

&nbsp;  - \[ ] 통계 API (사용자 수, 설문 응답률 등)

&nbsp;  - \[ ] 사용자 관리 (조회/삭제)

&nbsp;  - \[ ] 취미 데이터 CRUD

&nbsp;  - \[ ] 피드백 관리

&nbsp;  - \[ ] 공지사항 CRUD

&nbsp;  - \[ ] 활동 로그 조회



\### Phase 3: 프론트엔드

8\. \*\*설문 컴포넌트\*\*

&nbsp;  - \[ ] 20개 질문 UI

&nbsp;  - \[ ] 진행률 표시

&nbsp;  - \[ ] 답변 검증



9\. \*\*추천 결과 페이지\*\*

&nbsp;  - \[ ] 추천 취미 카드 UI

&nbsp;  - \[ ] 상세 정보 모달

&nbsp;  - \[ ] 체험 기능



10\. \*\*관리자 페이지\*\*

&nbsp;   - \[ ] 로그인 페이지

&nbsp;   - \[ ] 대시보드

&nbsp;   - \[ ] 데이터 관리 UI



\### Phase 4: 고급 기능

11\. \*\*머신러닝\*\*

&nbsp;   - \[ ] 추천 모델 학습

&nbsp;   - \[ ] 모델 평가 및 개선



12\. \*\*보안 강화\*\*

&nbsp;   - \[ ] JWT 인증

&nbsp;   - \[ ] CSRF 보호

&nbsp;   - \[ ] Rate Limiting



---



\## 📝 개발 시 참고사항



\### 환경 변수 (.env)

```env

FLASK\_APP=app.py

FLASK\_ENV=development

FLASK\_DEBUG=True

SECRET\_KEY=hobby-recommender-secret-key-2024

DATABASE\_URL=mysql+mysqlconnector://hobby\_user:password123@localhost:3306/hobby\_recommender

```



\### 서버 실행 명령어

```bash

\# Backend

cd C:\\hobby-recommender-app\\backend

hobby\_env\\Scripts\\activate

python app.py



\# Frontend

cd C:\\hobby-recommender-app\\frontend

npm start

```



\### 관리자 기본 계정

```

Username: admin

Password: admin123!

⚠️ 반드시 변경 필요!

```



\### API 응답 형식 표준

```json

// 성공

{

&nbsp; "status": "success",

&nbsp; "data": { ... },

&nbsp; "message": "작업이 완료되었습니다."

}



// 실패

{

&nbsp; "error": "Error Type",

&nbsp; "message": "사용자 친화적 메시지",

&nbsp; "details": "상세 오류 (개발 환경에서만)"

}

```



\### 코드 스타일 가이드

\- Python: PEP 8

\- JavaScript: Airbnb Style Guide

\- 함수명: snake\_case (Python), camelCase (JS)

\- 클래스명: PascalCase

\- 상수: UPPER\_SNAKE\_CASE



---



\## 🐛 알려진 이슈 및 해결방법



\### 1. MySQL 연결 오류

```python

\# .env에서 DATABASE\_URL 확인

DATABASE\_URL=mysql+mysqlconnector://...  # mysql+mysqlconnector 필수!

```



\### 2. CORS 오류

```python

\# app.py에서 CORS 설정 확인

CORS(app, origins=\['http://localhost:3000'], supports\_credentials=True)

```



\### 3. 한글 깨짐

```python

\# app.py

app.config\['JSON\_AS\_ASCII'] = False

```



---



\## 📚 

