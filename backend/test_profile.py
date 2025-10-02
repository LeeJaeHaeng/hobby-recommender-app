"""
사용자 프로필 관리 API 테스트
GET/PUT /api/users/<user_id>, PUT /api/users/<user_id>/password 테스트
"""

import requests
import json
from datetime import datetime

# 서버 설정
BASE_URL = 'http://localhost:5000'
LOGIN_URL = f'{BASE_URL}/api/auth/login'
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


def create_and_login_test_user():
    """테스트용 사용자 생성 및 로그인"""
    timestamp = int(datetime.now().timestamp())

    # 사용자 생성
    user_data = {
        "username": f"profiletest{timestamp}",
        "email": f"profiletest{timestamp}@example.com",
        "password": "ProfileTest123!",
        "confirmPassword": "ProfileTest123!",
        "firstName": "프로필",
        "lastName": "테스트",
        "age": 30,
        "gender": "male",
        "location": "서울특별시"
    }

    try:
        # 회원가입
        response = requests.post(REGISTER_URL, json=user_data, timeout=10)
        if response.status_code != 201:
            print(f"❌ 테스트 사용자 생성 실패: {response.status_code}")
            return None, None

        user_info = response.json()['data']['user']
        print(f"✅ 테스트 사용자 생성됨: {user_info['username']} (ID: {user_info['user_id']})")

        # 로그인
        login_data = {
            "email": user_data['email'],
            "password": user_data['password']
        }

        login_response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            return None, None

        access_token = login_response.json()['data']['access_token']
        print(f"✅ 로그인 성공, 토큰 획득")

        return user_info['user_id'], access_token

    except requests.exceptions.RequestException as e:
        print(f"❌ 사용자 생성/로그인 실패: {e}")
        return None, None


def test_get_profile(user_id, access_token):
    """프로필 조회 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(f'{BASE_URL}/api/users/{user_id}', headers=headers, timeout=10)
        print_test_result("프로필 조회", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_get_other_user_profile(user_id, access_token):
    """다른 사용자 프로필 조회 테스트 (권한 없음)"""
    headers = {'Authorization': f'Bearer {access_token}'}
    other_user_id = user_id + 999  # 존재하지 않을 가능성이 높은 ID

    try:
        response = requests.get(f'{BASE_URL}/api/users/{other_user_id}', headers=headers, timeout=10)
        print_test_result("다른 사용자 프로필 조회 (권한 없음)", response, 403)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_update_basic_profile(user_id, access_token):
    """기본 프로필 정보 업데이트 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "age": 35,
        "gender": "female",
        "location": "부산광역시"
    }

    try:
        response = requests.put(f'{BASE_URL}/api/users/{user_id}', json=data, headers=headers, timeout=10)
        print_test_result("기본 프로필 정보 업데이트", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_update_preferences(user_id, access_token):
    """취미 선호도 업데이트 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "outdoor_preference": 0.8,
        "social_preference": 0.6,
        "creative_preference": 0.9,
        "learning_preference": 0.7,
        "physical_activity": 0.4,
        "budget_level": "high"
    }

    try:
        response = requests.put(f'{BASE_URL}/api/users/{user_id}', json=data, headers=headers, timeout=10)
        print_test_result("취미 선호도 업데이트", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_invalid_profile_update(user_id, access_token):
    """잘못된 프로필 업데이트 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "age": 150,  # 잘못된 나이
        "gender": "invalid",  # 잘못된 성별
        "outdoor_preference": 1.5,  # 잘못된 선호도 값
        "budget_level": "invalid"  # 잘못된 예산 수준
    }

    try:
        response = requests.put(f'{BASE_URL}/api/users/{user_id}', json=data, headers=headers, timeout=10)
        print_test_result("잘못된 프로필 업데이트", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_change_password(user_id, access_token):
    """비밀번호 변경 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "current_password": "ProfileTest123!",
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }

    try:
        response = requests.put(f'{BASE_URL}/api/users/{user_id}/password', json=data, headers=headers, timeout=10)
        print_test_result("비밀번호 변경", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_change_password_wrong_current(user_id, access_token):
    """잘못된 현재 비밀번호로 비밀번호 변경 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "current_password": "WrongPassword123!",
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }

    try:
        response = requests.put(f'{BASE_URL}/api/users/{user_id}/password', json=data, headers=headers, timeout=10)
        print_test_result("잘못된 현재 비밀번호", response, 401)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_change_password_weak(user_id, access_token):
    """약한 비밀번호로 변경 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "current_password": "NewPassword123!",  # 이전 테스트에서 변경된 비밀번호
        "new_password": "123456",  # 약한 비밀번호
        "confirm_password": "123456"
    }

    try:
        response = requests.put(f'{BASE_URL}/api/users/{user_id}/password', json=data, headers=headers, timeout=10)
        print_test_result("약한 비밀번호로 변경", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_access_without_token(user_id):
    """토큰 없이 접근 테스트"""
    try:
        response = requests.get(f'{BASE_URL}/api/users/{user_id}', timeout=10)
        print_test_result("토큰 없이 프로필 접근", response, 401)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def main():
    """메인 테스트 함수"""
    print("🧪 사용자 프로필 관리 API 테스트를 시작합니다...")
    print(f"서버 주소: {BASE_URL}")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 서버 상태 확인
    if not test_server_health():
        print("❌ 서버가 실행되지 않았거나 응답하지 않습니다.")
        return

    print("✅ 서버가 정상적으로 응답합니다.")

    # 테스트용 사용자 생성 및 로그인
    print("\n📝 테스트용 사용자를 생성하고 로그인합니다...")
    user_id, access_token = create_and_login_test_user()
    if not user_id or not access_token:
        print("❌ 테스트용 사용자 생성 또는 로그인에 실패했습니다.")
        return

    # 테스트 실행
    test_cases = [
        ("프로필 조회", lambda: test_get_profile(user_id, access_token)),
        ("다른 사용자 프로필 조회", lambda: test_get_other_user_profile(user_id, access_token)),
        ("기본 프로필 정보 업데이트", lambda: test_update_basic_profile(user_id, access_token)),
        ("취미 선호도 업데이트", lambda: test_update_preferences(user_id, access_token)),
        ("잘못된 프로필 업데이트", lambda: test_invalid_profile_update(user_id, access_token)),
        ("비밀번호 변경", lambda: test_change_password(user_id, access_token)),
        ("잘못된 현재 비밀번호", lambda: test_change_password_wrong_current(user_id, access_token)),
        ("약한 비밀번호로 변경", lambda: test_change_password_weak(user_id, access_token)),
        ("토큰 없이 접근", lambda: test_access_without_token(user_id))
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