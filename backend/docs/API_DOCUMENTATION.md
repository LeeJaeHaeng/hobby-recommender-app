# 취미 추천 시스템 API 문서

## 개요
퇴직자 맞춤 취미 추천 시스템의 백엔드 REST API 문서입니다.

## 기본 정보
- **Base URL**: `http://localhost:5000`
- **인증 방식**: JWT (Bearer Token)
- **응답 형식**: JSON

---

## 📋 목차
1. [사용자 관리 API](#1-사용자-관리-api)
2. [인증 API](#2-인증-api)
3. [프로필 API](#3-프로필-api)
4. [설문 API](#4-설문-api)
5. [취미 API](#5-취미-api)
6. [추천 API](#6-추천-api)
7. [모임 API](#7-모임-api)

---

## 1. 사용자 관리 API

### 회원가입
```http
POST /api/users/signup
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Password123!",
  "name": "홍길동",
  "birth_year": 1970,
  "gender": "male"
}
```

### 사용자명 중복 확인
```http
GET /api/users/check-username?username=testuser
```

### 이메일 중복 확인
```http
GET /api/users/check-email?email=test@example.com
```

---

## 2. 인증 API

### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "Password123!"
}
```

**응답 예시:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "user_id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

### 토큰 갱신
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### 로그아웃
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

---

## 3. 프로필 API

### 프로필 조회
```http
GET /api/users/{user_id}
Authorization: Bearer <access_token>
```

### 프로필 수정
```http
PUT /api/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "홍길동",
  "location": "서울"
}
```

### 비밀번호 변경
```http
PUT /api/users/{user_id}/password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

---

## 4. 설문 API

### 설문 질문 조회
```http
GET /api/survey/questions
```

**응답 예시:**
```json
{
  "status": "success",
  "data": {
    "questions": [
      {
        "question_id": 1,
        "question_text": "새로운 사람들과 만나는 것을 좋아하시나요?",
        "question_type": "scale",
        "category": "사회성향",
        "options": {
          "min": 1,
          "max": 5,
          "labels": {
            "1": "전혀 아니다",
            "3": "보통이다",
            "5": "매우 그렇다"
          }
        }
      }
    ],
    "total_questions": 20
  }
}
```

### 설문 응답 제출
```http
POST /api/survey/submit
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "responses": [
    {
      "question_id": 1,
      "answer_value": 4
    },
    {
      "question_id": 2,
      "answer_value": 3
    }
  ]
}
```

### 내 설문 응답 조회
```http
GET /api/survey/responses/{user_id}
Authorization: Bearer <access_token>
```

---

## 5. 취미 API

### 취미 목록 조회
```http
GET /api/hobbies?category=운동&indoor_outdoor=outdoor&page=1&per_page=20
```

**쿼리 파라미터:**
- `category`: 카테고리 필터
- `search`: 검색어 (이름, 설명)
- `indoor_outdoor`: 실내/외 (`indoor`, `outdoor`, `both`)
- `social_individual`: 사회성/개인 (`social`, `individual`, `both`)
- `budget`: 예산 (`low`, `medium`, `high`)
- `difficulty_min`: 최소 난이도 (1~5)
- `difficulty_max`: 최대 난이도 (1~5)
- `page`: 페이지 번호 (기본: 1)
- `per_page`: 페이지당 항목 수 (기본: 20, 최대: 100)

### 취미 상세 조회
```http
GET /api/hobbies/{hobby_id}
```

**응답 예시:**
```json
{
  "status": "success",
  "data": {
    "hobby_id": 1,
    "name": "요가",
    "category": "운동",
    "description": "몸과 마음을 건강하게...",
    "difficulty_level": 2,
    "physical_intensity": 3,
    "creativity_level": 2,
    "indoor_outdoor": "both",
    "social_individual": "both",
    "required_budget": "low",
    "average_rating": 4.5,
    "rating_count": 120,
    "recent_reviews": [...]
  }
}
```

### 취미 평가
```http
POST /api/hobbies/{hobby_id}/rate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rating": 5,
  "review_text": "정말 좋은 취미입니다!",
  "experienced": true
}
```

### 카테고리 목록 조회
```http
GET /api/hobbies/categories
```

### 취미 평가 목록 조회
```http
GET /api/hobbies/{hobby_id}/ratings?page=1&per_page=20
```

---

## 6. 추천 API

### 사용자 맞춤 추천
```http
GET /api/recommendations?limit=10&exclude_rated=true
Authorization: Bearer <access_token>
```

**쿼리 파라미터:**
- `limit`: 추천 개수 (기본: 10, 최대: 50)
- `exclude_rated`: 평가한 취미 제외 여부 (기본: true)

**응답 예시:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "hobby": {
          "hobby_id": 5,
          "name": "등산",
          "category": "운동",
          ...
        },
        "recommendation_score": 0.8542,
        "match_percentage": 85.4,
        "score_breakdown": {
          "profile_match": 0.8800,
          "collaborative_filtering": 0.7500,
          "popularity": 0.8000
        }
      }
    ],
    "total": 10,
    "user_profile": {
      "outdoor_preference": 0.85,
      "social_preference": 0.60,
      ...
    }
  }
}
```

### 인기 취미 조회
```http
GET /api/recommendations/popular?limit=10&period=all
```

**쿼리 파라미터:**
- `limit`: 개수 (기본: 10, 최대: 50)
- `period`: 기간 (`all`, `week`, `month`)

### 유사 취미 추천
```http
GET /api/recommendations/similar/{hobby_id}?limit=5
```

### 카테고리별 추천
```http
GET /api/recommendations/category/{category}?limit=10
```

---

## 추천 알고리즘

### 점수 계산 방식
최종 추천 점수는 다음 3가지 요소를 결합하여 계산됩니다:

1. **프로필 기반 매칭 (70%)**
   - 실내/외 선호도 (20%)
   - 사회성향 (20%)
   - 창의성 (15%)
   - 학습성향 (10%)
   - 신체활동 (20%)
   - 예산 (15%)

2. **협업 필터링 (20%)**
   - 유사한 평가를 한 사용자들의 선호도 기반
   - Top-K 유사 사용자 활용

3. **인기도 (10%)**
   - 베이지안 평균 적용
   - 평가 수가 적은 취미에 페널티

### 유사 취미 계산
두 취미 간 유사도는 다음 요소로 계산됩니다:
- 카테고리 일치 (30%)
- 실내/외 속성 (15%)
- 사회성/개인 속성 (15%)
- 예산 유사도 (10%)
- 난이도 유사도 (10%)
- 신체 강도 유사도 (10%)
- 창의성 유사도 (10%)

---

## 7. 모임 API

### 모임 목록 조회
```http
GET /api/gatherings?hobby_id=1&region=서울&meeting_type=offline&page=1&per_page=20
```

**쿼리 파라미터:**
- `hobby_id`: 취미 ID 필터
- `region`: 지역 필터
- `meeting_type`: 모임 유형 (`online`, `offline`, `hybrid`)
- `search`: 검색어 (모임명, 설명)
- `is_active`: 활성 모임 여부 (기본: true)
- `page`: 페이지 번호 (기본: 1)
- `per_page`: 페이지당 항목 수 (기본: 20, 최대: 100)

**응답 예시:**
```json
{
  "status": "success",
  "data": {
    "gatherings": [
      {
        "gathering_id": 1,
        "hobby_id": 5,
        "name": "서울 등산 동호회",
        "description": "매주 주말 서울 근교 산을 등반합니다.",
        "location": "서울특별시 종로구",
        "region": "서울",
        "meeting_type": "offline",
        "schedule_info": "매주 토요일 오전 8시",
        "member_count": 15,
        "contact_info": "010-1234-5678",
        "website_url": "https://example.com/hiking",
        "is_active": true,
        "created_at": "2025-10-01T10:00:00",
        "hobby": {
          "hobby_id": 5,
          "name": "등산",
          "category": "운동"
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_items": 5,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### 모임 상세 조회
```http
GET /api/gatherings/{gathering_id}
```

### 모임 생성
```http
POST /api/gatherings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "hobby_id": 5,
  "name": "서울 등산 동호회",
  "description": "매주 주말 서울 근교 산을 등반하는 모임입니다.",
  "location": "서울특별시 종로구",
  "region": "서울",
  "meeting_type": "offline",
  "schedule_info": "매주 토요일 오전 8시",
  "member_count": 15,
  "contact_info": "010-1234-5678",
  "website_url": "https://example.com/hiking",
  "is_active": true
}
```

**필수 필드:**
- `hobby_id`: 취미 ID
- `name`: 모임 이름
- `region`: 지역

### 모임 수정
```http
PUT /api/gatherings/{gathering_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "서울 등산 동호회 (수정됨)",
  "description": "수정된 설명입니다.",
  "member_count": 20
}
```

### 모임 삭제
```http
DELETE /api/gatherings/{gathering_id}
Authorization: Bearer <access_token>
```

**참고:** 실제 삭제가 아닌 비활성화(is_active=false) 처리됩니다.

### 취미별 모임 조회
```http
GET /api/gatherings/hobby/{hobby_id}?region=서울&page=1
```

### 지역 목록 조회
```http
GET /api/gatherings/regions
```

**응답 예시:**
```json
{
  "status": "success",
  "data": {
    "regions": [
      {
        "region": "서울",
        "count": 45
      },
      {
        "region": "부산",
        "count": 23
      }
    ],
    "total_regions": 16
  }
}
```

### 인기 모임 조회
```http
GET /api/gatherings/popular?limit=10
```

회원 수가 많은 순으로 인기 모임을 조회합니다.

---

## 에러 코드

| 상태 코드 | 설명 |
|---------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 중복 (회원가입 등) |
| 500 | 서버 오류 |

---

## 테스트 스크립트

### 취미 API 테스트
```bash
python backend/test_hobbies_api.py
```

### 추천 API 테스트
```bash
python backend/test_recommendations_api.py
```

### 모임 API 테스트
```bash
python backend/test_gatherings_api.py
```

---

## 개발 환경

### 서버 실행
```bash
cd backend
python app.py
```

### 데이터베이스 초기화
```bash
flask init-db
```

### 관리자 계정 생성
```bash
flask seed-admin
```

---

## 주의사항

1. **인증 토큰**: 대부분의 사용자 관련 API는 JWT 토큰이 필요합니다.
2. **설문 응답**: 맞춤 추천을 받기 위해서는 먼저 설문에 응답해야 합니다.
3. **페이지네이션**: 목록 조회 API는 최대 100개까지만 조회할 수 있습니다.
4. **CORS**: 프론트엔드는 `http://localhost:3000`에서만 접근 가능합니다.

---

**문서 버전**: 1.0.0
**최종 수정일**: 2025-10-02
