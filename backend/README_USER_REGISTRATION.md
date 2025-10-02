# 사용자 회원가입 API

퇴직자 맞춤 취미 추천 앱의 사용자 회원가입 API 구현이 완료되었습니다.

## 🚀 구현된 기능

### POST /api/users/register
완전한 입력 검증과 에러 처리를 포함한 사용자 회원가입 API

#### 📝 요청 데이터
```json
{
  "username": "testuser123",
  "email": "test@example.com",
  "password": "Test123!@#",
  "confirmPassword": "Test123!@#",
  "firstName": "홍",
  "lastName": "길동",
  "age": 65,
  "gender": "male",
  "location": "서울특별시"
}
```

#### 필수 필드
- `username`: 3-30자, 영문자/숫자/언더스코어만 허용
- `email`: 유효한 이메일 형식
- `password`: 최소 8자, 대소문자/숫자/특수문자 포함
- `confirmPassword`: 비밀번호와 일치해야 함
- `firstName`: 1-50자, 한글/영문자/공백만 허용
- `lastName`: 1-50자, 한글/영문자/공백만 허용

#### 선택 필드
- `age`: 13-120 사이의 정수
- `gender`: "male", "female", "other" 중 하나
- `location`: 거주지역

#### ✅ 성공 응답 (201)
```json
{
  "status": "success",
  "message": "회원가입이 완료되었습니다.",
  "data": {
    "user": {
      "user_id": 123,
      "username": "testuser123",
      "email": "test@example.com",
      "age": 65,
      "gender": "male",
      "location": "서울특별시",
      "email_verified": false,
      "created_at": "2024-10-02T10:30:00"
    }
  }
}
```

#### ❌ 에러 응답 예시

**400 - 검증 실패:**
```json
{
  "error": "Validation Error",
  "message": "입력 데이터가 올바르지 않습니다.",
  "validation_errors": [
    {
      "field": "password",
      "message": "비밀번호에 대문자가 포함되어야 합니다."
    },
    {
      "field": "confirmPassword",
      "message": "비밀번호가 일치하지 않습니다."
    }
  ]
}
```

**409 - 중복 사용자:**
```json
{
  "error": "Conflict",
  "message": "이미 등록된 이메일입니다."
}
```

### POST /api/users/check-availability
사용자명/이메일 중복 확인 API

#### 📝 요청 데이터
```json
{
  "username": "testuser123",
  "email": "test@example.com"
}
```

#### ✅ 성공 응답 (200)
```json
{
  "status": "success",
  "data": {
    "username": {
      "available": true,
      "message": "사용 가능한 사용자명입니다."
    },
    "email": {
      "available": false,
      "message": "이미 등록된 이메일입니다."
    }
  }
}
```

## 🔒 보안 기능

### 입력 검증
- **이메일**: 정규식으로 형식 검증
- **사용자명**: 길이, 문자 제한 검증
- **비밀번호**: 복잡성 규칙 (대소문자, 숫자, 특수문자)
- **나이**: 범위 검증 (13-120세)
- **이름**: 한글/영문자만 허용

### 데이터 보안
- **비밀번호 해싱**: Werkzeug의 generate_password_hash 사용
- **중복 방지**: 사용자명/이메일 유니크 제약
- **소프트 삭제**: is_deleted 플래그로 데이터 보존
- **SQL Injection 방지**: SQLAlchemy ORM 사용

### 에러 처리
- **포괄적 예외 처리**: try-catch로 모든 에러 캐치
- **로깅**: 에러 발생 시 상세 로그 기록
- **트랜잭션 롤백**: 에러 시 DB 상태 복구
- **사용자 친화적 메시지**: 기술적 세부사항 숨김

## 🧪 테스트

### 테스트 실행
```bash
cd /c/hobby-recommender-app/backend

# 서버 실행 (별도 터미널)
python app.py

# 테스트 실행 (다른 터미널)
python test_registration.py
```

### 테스트 케이스
1. ✅ 정상적인 회원가입
2. ❌ 필수 필드 누락
3. ❌ 잘못된 이메일 형식
4. ❌ 약한 비밀번호
5. ❌ 비밀번호 불일치
6. ❌ 잘못된 나이
7. ✅ 중복 확인 API
8. ❌ 중복 회원가입

## 📁 구현된 파일

```
backend/
├── app.py                     # Flask 메인 앱 (Blueprint 등록 추가됨)
├── app/
│   └── api/
│       ├── __init__.py        # API 패키지 초기화
│       └── users.py           # 사용자 회원가입 API
├── test_registration.py       # API 테스트 스크립트
└── README_USER_REGISTRATION.md # 이 문서
```

## 🔧 추가 개발 권장사항

### 인증/인가 (다음 단계)
- JWT 토큰 기반 로그인 API
- 이메일 인증 시스템
- 비밀번호 재설정 기능

### 보안 강화
- Rate Limiting (요청 제한)
- CSRF 보호
- 입력 데이터 sanitization

### 사용자 경험
- 프로필 사진 업로드
- 소셜 로그인 연동
- 실시간 중복 확인

## 🐛 알려진 제약사항

1. **이메일 인증 없음**: 현재는 이메일 인증 없이 가입 가능
2. **Rate Limiting 없음**: 무제한 가입 시도 가능
3. **비밀번호 복구 없음**: 비밀번호 찾기 기능 미구현

## 📊 데이터베이스 영향

### 사용된 테이블
- **users**: 기본 사용자 정보 저장
- **user_profiles**: 기본 프로필 자동 생성

### 자동 생성 데이터
- 회원가입 시 기본 UserProfile 생성 (모든 선호도 0.5, 예산 수준 medium)
- 생성/수정 타임스탬프 자동 기록