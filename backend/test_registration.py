"""
사용자 회원가입 API 테스트
POST /api/users/register 엔드포인트 테스트
"""

import requests
import json
from datetime import datetime

# 서버 설정
BASE_URL = 'http://localhost:5000'
REGISTER_URL = f'{BASE_URL}/api/users/register'
CHECK_URL = f'{BASE_URL}/api/users/check-availability'

def print_test_result(test_name, response, expected_status=None):
    """테스트 결과 출력"""
    print(f"\n{'='*50}")
    print(f"테스트: {test_name}")
    print(f"{'='*50}")
    print(f"상태 코드: {response.status_code}")

    try:
        response_data = response.json()
        print(f"응답 데이터:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
    except:
        print(f"응답 텍스트: {response.text}")

    if expected_status and response.status_code == expected_status:
        print("✅ 예상된 상태 코드")
    elif expected_status:
        print(f"❌ 예상 상태 코드: {expected_status}, 실제: {response.status_code}")

    print("-" * 50)


def test_valid_registration():
    """정상적인 회원가입 테스트"""
    timestamp = int(datetime.now().timestamp())

    data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "Test123!@#",
        "confirmPassword": "Test123!@#",
        "firstName": "홍",
        "lastName": "길동",
        "age": 65,
        "gender": "male",
        "location": "서울특별시"
    }

    try:
        response = requests.post(REGISTER_URL, json=data, timeout=10)
        print_test_result("정상적인 회원가입", response, 201)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_missing_fields():
    """필수 필드 누락 테스트"""
    data = {
        "username": "testuser",
        "email": "test@example.com"
        # password, confirmPassword, firstName, lastName 누락
    }

    try:
        response = requests.post(REGISTER_URL, json=data, timeout=10)
        print_test_result("필수 필드 누락", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_invalid_email():
    """잘못된 이메일 형식 테스트"""
    data = {
        "username": "testuser2",
        "email": "invalid-email",
        "password": "Test123!@#",
        "confirmPassword": "Test123!@#",
        "firstName": "홍",
        "lastName": "길동"
    }

    try:
        response = requests.post(REGISTER_URL, json=data, timeout=10)
        print_test_result("잘못된 이메일 형식", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_weak_password():
    """약한 비밀번호 테스트"""
    data = {
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "123456",  # 약한 비밀번호
        "confirmPassword": "123456",
        "firstName": "홍",
        "lastName": "길동"
    }

    try:
        response = requests.post(REGISTER_URL, json=data, timeout=10)
        print_test_result("약한 비밀번호", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_password_mismatch():
    """비밀번호 불일치 테스트"""
    data = {
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "Test123!@#",
        "confirmPassword": "Different123!@#",  # 다른 비밀번호
        "firstName": "홍",
        "lastName": "길동"
    }

    try:
        response = requests.post(REGISTER_URL, json=data, timeout=10)
        print_test_result("비밀번호 불일치", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_duplicate_registration():
    """중복 회원가입 테스트"""
    # 먼저 사용자 등록
    timestamp = int(datetime.now().timestamp())
    data = {
        "username": f"dupuser{timestamp}",
        "email": f"dup{timestamp}@example.com",
        "password": "Test123!@#",
        "confirmPassword": "Test123!@#",
        "firstName": "홍",
        "lastName": "길동"
    }

    try:
        # 첫 번째 등록
        response1 = requests.post(REGISTER_URL, json=data, timeout=10)

        if response1.status_code == 201:
            # 같은 데이터로 두 번째 등록 시도
            response2 = requests.post(REGISTER_URL, json=data, timeout=10)
            print_test_result("중복 회원가입 (같은 사용자명)", response2, 409)

            # 같은 이메일로 다른 사용자명 등록 시도
            data['username'] = f"dupuser{timestamp}_2"
            response3 = requests.post(REGISTER_URL, json=data, timeout=10)
            print_test_result("중복 회원가입 (같은 이메일)", response3, 409)
        else:
            print("❌ 첫 번째 사용자 등록 실패, 중복 테스트 건너뜀")

    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")


def test_invalid_age():
    """잘못된 나이 테스트"""
    data = {
        "username": "testuser5",
        "email": "test5@example.com",
        "password": "Test123!@#",
        "confirmPassword": "Test123!@#",
        "firstName": "홍",
        "lastName": "길동",
        "age": 150  # 잘못된 나이
    }

    try:
        response = requests.post(REGISTER_URL, json=data, timeout=10)
        print_test_result("잘못된 나이", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_check_availability():
    """사용자명/이메일 중복 확인 테스트"""
    data = {
        "username": "testuser",
        "email": "test@example.com"
    }

    try:
        response = requests.post(CHECK_URL, json=data, timeout=10)
        print_test_result("중복 확인", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_server_health():
    """서버 상태 확인"""
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=10)
        print_test_result("서버 헬스 체크", response, 200)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🧪 사용자 회원가입 API 테스트를 시작합니다...")
    print(f"서버 주소: {BASE_URL}")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 서버 상태 확인
    if not test_server_health():
        print("❌ 서버가 실행되지 않았거나 응답하지 않습니다.")
        print("다음 명령어로 서버를 실행하세요:")
        print("cd /c/hobby-recommender-app/backend")
        print("python app.py")
        return

    print("✅ 서버가 정상적으로 응답합니다.")

    # 테스트 실행
    test_cases = [
        ("정상적인 회원가입", test_valid_registration),
        ("필수 필드 누락", test_missing_fields),
        ("잘못된 이메일 형식", test_invalid_email),
        ("약한 비밀번호", test_weak_password),
        ("비밀번호 불일치", test_password_mismatch),
        ("잘못된 나이", test_invalid_age),
        ("중복 확인 API", test_check_availability),
        ("중복 회원가입", test_duplicate_registration)
    ]

    success_count = 0
    total_count = len(test_cases)

    for test_name, test_func in test_cases:
        try:
            result = test_func()
            if result is not None:
                success_count += 1
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}")

    print(f"\n{'='*60}")
    print(f"테스트 완료: {success_count}/{total_count} 성공")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()