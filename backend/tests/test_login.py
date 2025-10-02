"""
사용자 로그인 API 테스트
POST /api/auth/login 엔드포인트 테스트
"""

import requests
import json
from datetime import datetime

# 서버 설정
BASE_URL = 'http://localhost:5000'
LOGIN_URL = f'{BASE_URL}/api/auth/login'
REFRESH_URL = f'{BASE_URL}/api/auth/refresh'
ME_URL = f'{BASE_URL}/api/auth/me'
LOGOUT_URL = f'{BASE_URL}/api/auth/logout'
REGISTER_URL = f'{BASE_URL}/api/users/register'

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
    return response


def test_server_health():
    """서버 상태 확인"""
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=10)
        print_test_result("서버 헬스 체크", response, 200)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False


def create_test_user():
    """테스트용 사용자 생성"""
    timestamp = int(datetime.now().timestamp())

    user_data = {
        "username": f"logintest{timestamp}",
        "email": f"logintest{timestamp}@example.com",
        "password": "LoginTest123!",
        "confirmPassword": "LoginTest123!",
        "firstName": "로그인",
        "lastName": "테스트"
    }

    try:
        response = requests.post(REGISTER_URL, json=user_data, timeout=10)
        if response.status_code == 201:
            user_info = response.json()['data']['user']
            print(f"✅ 테스트 사용자 생성됨: {user_info['username']} ({user_info['email']})")
            return {
                'username': user_info['username'],
                'email': user_info['email'],
                'password': 'LoginTest123!'
            }
        else:
            print(f"❌ 테스트 사용자 생성 실패: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 테스트 사용자 생성 실패: {e}")
        return None


def test_login_success(user_credentials):
    """정상적인 로그인 테스트"""
    data = {
        "email": user_credentials['email'],
        "password": user_credentials['password']
    }

    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        result = print_test_result("정상적인 로그인 (이메일)", response, 200)

        if response.status_code == 200:
            return response.json()['data']['access_token']
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_login_with_username(user_credentials):
    """사용자명으로 로그인 테스트"""
    data = {
        "username": user_credentials['username'],
        "password": user_credentials['password']
    }

    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        print_test_result("사용자명으로 로그인", response, 200)

        if response.status_code == 200:
            return response.json()['data']['access_token']
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_login_remember_me(user_credentials):
    """Remember Me 로그인 테스트"""
    data = {
        "email": user_credentials['email'],
        "password": user_credentials['password'],
        "remember_me": True
    }

    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        print_test_result("Remember Me 로그인", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_login_wrong_password(user_credentials):
    """잘못된 비밀번호 로그인 테스트"""
    data = {
        "email": user_credentials['email'],
        "password": "WrongPassword123!"
    }

    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        print_test_result("잘못된 비밀번호", response, 401)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_login_nonexistent_user():
    """존재하지 않는 사용자 로그인 테스트"""
    data = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }

    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        print_test_result("존재하지 않는 사용자", response, 401)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_login_missing_fields():
    """필수 필드 누락 테스트"""
    data = {
        "email": "test@example.com"
        # password 누락
    }

    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        print_test_result("필수 필드 누락", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_get_current_user(access_token):
    """현재 사용자 정보 조회 테스트"""
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(ME_URL, headers=headers, timeout=10)
        print_test_result("현재 사용자 정보 조회", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_protected_route_without_token():
    """토큰 없이 보호된 라우트 접근 테스트"""
    try:
        response = requests.get(ME_URL, timeout=10)
        print_test_result("토큰 없이 보호된 라우트 접근", response, 401)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_logout(access_token):
    """로그아웃 테스트"""
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.post(LOGOUT_URL, headers=headers, timeout=10)
        print_test_result("로그아웃", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def main():
    """메인 테스트 함수"""
    print("🧪 사용자 로그인 API 테스트를 시작합니다...")
    print(f"서버 주소: {BASE_URL}")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 서버 상태 확인
    if not test_server_health():
        print("❌ 서버가 실행되지 않았거나 응답하지 않습니다.")
        return

    print("✅ 서버가 정상적으로 응답합니다.")

    # 테스트용 사용자 생성
    print("\n📝 테스트용 사용자를 생성합니다...")
    user_credentials = create_test_user()
    if not user_credentials:
        print("❌ 테스트용 사용자 생성에 실패했습니다.")
        return

    # 로그인 테스트 실행
    access_token = None

    test_cases = [
        ("정상 로그인 (이메일)", lambda: test_login_success(user_credentials)),
        ("정상 로그인 (사용자명)", lambda: test_login_with_username(user_credentials)),
        ("Remember Me 로그인", lambda: test_login_remember_me(user_credentials)),
        ("잘못된 비밀번호", lambda: test_login_wrong_password(user_credentials)),
        ("존재하지 않는 사용자", test_login_nonexistent_user),
        ("필수 필드 누락", test_login_missing_fields),
        ("토큰 없이 보호된 라우트 접근", test_protected_route_without_token)
    ]

    success_count = 0
    total_count = len(test_cases)

    for test_name, test_func in test_cases:
        try:
            result = test_func()
            if result is not None:
                success_count += 1
                # 첫 번째 정상 로그인에서 토큰 저장
                if test_name == "정상 로그인 (이메일)" and isinstance(result, str):
                    access_token = result
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}")

    # 토큰이 있는 경우 추가 테스트
    if access_token:
        print("\n🔐 인증 토큰을 사용한 추가 테스트...")
        try:
            test_get_current_user(access_token)
            test_logout(access_token)
            success_count += 2
            total_count += 2
        except Exception as e:
            print(f"❌ 인증 테스트 중 오류 발생: {e}")

    print(f"\n{'='*60}")
    print(f"테스트 완료: {success_count}/{total_count} 성공")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()