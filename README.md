# 🎯 취미 추천 시스템

퇴직자를 위한 AI 기반 맞춤 취미 추천 플랫폼입니다.

## 📱 프로젝트 개요

설문 조사를 통해 사용자의 성향을 분석하고, 머신러닝 추천 알고리즘을 활용하여 개인에게 최적화된 취미를 추천합니다. 또한 지역별 모임/동아리 정보를 제공하여 취미 활동을 시작하는데 도움을 줍니다.

### 주요 기능

- ✅ **설문 기반 성향 분석**: 20개 질문으로 사용자 프로필 자동 생성
- ✅ **스마트 추천 알고리즘**: 프로필 매칭(70%) + 협업 필터링(20%) + 인기도(10%)
- ✅ **취미 검색 및 평가**: 다양한 필터링 옵션과 리뷰 시스템
- ✅ **모임/동아리 관리**: 지역별, 취미별 모임 검색 및 생성
- ✅ **JWT 기반 인증**: 안전한 사용자 인증 및 세션 관리

## 🛠️ 기술 스택

### Backend
- **Python 3.9+**
- **Flask 3.0** - 웹 프레임워크
- **SQLAlchemy** - ORM
- **MySQL 8.0** - 데이터베이스
- **JWT** - 인증

### Frontend (개발 예정)
- React Native / Flutter

## 📁 프로젝트 구조

```
hobby-recommender-app/
├── backend/
│   ├── app/
│   │   ├── api/              # API 엔드포인트
│   │   │   ├── users.py
│   │   │   ├── auth.py
│   │   │   ├── hobbies.py
│   │   │   ├── recommendations.py
│   │   │   └── gatherings.py
│   │   └── models/           # 데이터 모델
│   ├── app.py                # 메인 애플리케이션
│   ├── seed_data.py          # 초기 데이터 생성
│   ├── create_tables.sql     # DB 스키마
│   ├── tests/                # 테스트 스크립트
│   └── docs/                 # API 문서
└── README.md                 # 이 파일
```

## 🚀 시작하기

### 1. 사전 준비

다음 프로그램들이 설치되어 있어야 합니다:

- **Python 3.9 이상** ([다운로드](https://www.python.org/downloads/))
- **MySQL 8.0 이상** ([다운로드](https://dev.mysql.com/downloads/mysql/))
- **Git** ([다운로드](https://git-scm.com/downloads))

### 2. 프로젝트 다운로드

```bash
git clone <repository-url>
cd hobby-recommender-app
```

### 3. Python 가상환경 설정

#### Windows
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors flask-migrate python-dotenv mysql-connector-python bcrypt
```

### 5. MySQL 데이터베이스 설정

MySQL에 접속하여 다음 명령어를 실행합니다:

```sql
CREATE DATABASE hobby_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hobby_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON hobby_recommender.* TO 'hobby_user'@'localhost';
FLUSH PRIVILEGES;
```

### 6. 환경 변수 설정

`backend/.env` 파일을 생성하고 다음 내용을 입력합니다:

```env
DATABASE_URL=mysql+mysqlconnector://hobby_user:password123@localhost:3306/hobby_recommender
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too
FLASK_ENV=development
FLASK_DEBUG=True
```

**⚠️ 중요**: 실제 배포 시에는 반드시 `SECRET_KEY`와 `JWT_SECRET_KEY`를 변경하세요!

### 7. 데이터베이스 테이블 생성

#### 방법 1: SQL 파일 사용 (권장)
```bash
mysql -u hobby_user -p hobby_recommender < create_tables.sql
```

#### 방법 2: Flask CLI 사용
```bash
flask init-db
```

### 8. 초기 데이터 생성

샘플 취미 데이터를 생성합니다:

```bash
python seed_data.py
```

16개의 취미 데이터가 자동으로 생성됩니다 (요가, 등산, 수채화, 우쿨렐레 등).

### 9. 설문 질문 초기화

서버를 실행한 후, 다음 API를 호출하여 설문 질문을 생성합니다:

```bash
# 서버 실행 (별도 터미널)
python app.py

# 설문 초기화 (새 터미널)
curl -X POST http://localhost:5000/api/survey/init-questions
```

또는 브라우저에서 Postman/Thunder Client를 사용하여 `POST http://localhost:5000/api/survey/init-questions`를 호출합니다.

### 10. 서버 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

---

## 🎨 프론트엔드 실행

백엔드 서버가 실행된 상태에서 새 터미널을 열어 진행합니다.

### 1. 프론트엔드 디렉토리로 이동

```bash
cd frontend
```

### 2. 패키지 설치 (최초 1회만)

```bash
npm install
```

### 3. 개발 서버 실행

```bash
npm start
```

프론트엔드가 `http://localhost:3000`에서 실행됩니다.

### 4. 브라우저에서 접속

```
http://localhost:3000
```

### 주요 페이지

- **메인 페이지**: `/` - 시작 화면
- **회원가입**: `/signup` - 새 계정 생성
- **로그인**: `/login` - 로그인
- **설문조사**: `/survey` - 성향 분석 (로그인 필요)
- **취미 탐색**: `/hobbies` - 모든 취미 검색
- **맞춤 추천**: `/recommendations` - AI 추천 결과 (설문 완료 필요)

## 🧪 테스트

### API 동작 확인

브라우저에서 다음 URL을 열어 서버가 정상 동작하는지 확인합니다:

- 메인: http://localhost:5000
- 헬스체크: http://localhost:5000/api/health
- 설문 질문: http://localhost:5000/api/survey/questions
- 취미 목록: http://localhost:5000/api/hobbies

### 전체 테스트 실행

```bash
cd backend/tests

# 각 기능별 테스트
python test_registration.py    # 회원가입 테스트
python test_login.py            # 로그인 테스트
python test_survey.py           # 설문 테스트
python test_hobbies_api.py      # 취미 API 테스트
python test_recommendations_api.py  # 추천 API 테스트
python test_gatherings_api.py   # 모임 API 테스트
```

## 📚 API 문서

상세한 API 문서는 [backend/docs/API_DOCUMENTATION.md](backend/docs/API_DOCUMENTATION.md)를 참조하세요.

### 주요 API 엔드포인트

| 기능 | 메소드 | 엔드포인트 | 인증 필요 |
|------|--------|-----------|----------|
| 회원가입 | POST | `/api/users/signup` | ❌ |
| 로그인 | POST | `/api/auth/login` | ❌ |
| 설문 조회 | GET | `/api/survey/questions` | ❌ |
| 설문 제출 | POST | `/api/survey/submit` | ✅ |
| 취미 목록 | GET | `/api/hobbies` | ❌ |
| 취미 평가 | POST | `/api/hobbies/{id}/rate` | ✅ |
| 맞춤 추천 | GET | `/api/recommendations` | ✅ |
| 모임 목록 | GET | `/api/gatherings` | ❌ |
| 모임 생성 | POST | `/api/gatherings` | ✅ |

## 🔧 추천 알고리즘

### 점수 계산 방식

```
최종 점수 = (프로필 매칭 × 0.7) + (협업 필터링 × 0.2) + (인기도 × 0.1)
```

#### 1. 프로필 기반 매칭 (70%)
사용자 설문 응답과 취미 특성 비교:
- 실내/외 선호도 (20%)
- 사회성향 (20%)
- 창의성 (15%)
- 학습성향 (10%)
- 신체활동 (20%)
- 예산 (15%)

#### 2. 협업 필터링 (20%)
유사한 평가를 한 사용자들의 선호도 기반

#### 3. 인기도 (10%)
베이지안 평균으로 공정한 순위 산정

## 📊 사용 예시

### 1. 회원가입

```bash
curl -X POST http://localhost:5000/api/users/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234!",
    "name": "홍길동",
    "birth_year": 1970,
    "gender": "male"
  }'
```

### 2. 로그인

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test1234!"
  }'
```

응답에서 `access_token`을 저장하여 이후 API 호출에 사용합니다.

### 3. 맞춤 추천 받기

```bash
curl -X GET http://localhost:5000/api/recommendations \
  -H "Authorization: Bearer <your-access-token>"
```

## 🔒 보안

- ✅ JWT 기반 토큰 인증
- ✅ Bcrypt 비밀번호 해싱
- ✅ SQL 인젝션 방지 (SQLAlchemy ORM)
- ✅ 로그인 실패 5회 시 계정 잠금 (30분)
- ✅ CORS 설정

## 🐛 문제 해결

### MySQL 연결 오류

```
Error: Can't connect to MySQL server
```

**해결방법**:
1. MySQL 서비스가 실행 중인지 확인
2. `.env` 파일의 데이터베이스 정보 확인
3. 사용자 권한 확인

### 포트 충돌

```
Error: Address already in use
```

**해결방법**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### 패키지 설치 오류

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 캐시 클리어 후 재설치
pip cache purge
pip install -r requirements.txt
```

## 📈 개발 로드맵

### ✅ Phase 1: 백엔드 API (완료)
- [x] 사용자 인증 시스템
- [x] 설문 및 프로필 관리
- [x] 취미 CRUD 및 검색
- [x] 추천 알고리즘
- [x] 모임 관리

### ✅ Phase 2: 프론트엔드 (완료)
- [x] React 웹 애플리케이션
- [x] UI/UX 디자인 (Material-UI)
- [x] 반응형 디자인
- [x] 주요 페이지 구현 (로그인, 설문, 추천, 검색)

### 📅 Phase 3: 배포 (계획)
- [ ] AWS/GCP 배포
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인
- [ ] 모니터링 시스템

## 🤝 기여

이 프로젝트는 현재 개발 중입니다. 버그 리포트나 기능 제안은 Issue를 통해 알려주세요.

## 📄 라이선스

This project is for educational purposes.

---

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

**개발 완료일**: 2025-10-02
**버전**: 1.0.0
