"""
설문 조사 API 테스트
GET /api/survey/questions, POST /api/survey/submit 엔드포인트 테스트
"""

import requests
import json
from datetime import datetime

# 서버 설정
BASE_URL = 'http://localhost:5000'
SURVEY_QUESTIONS_URL = f'{BASE_URL}/api/survey/questions'
SURVEY_SUBMIT_URL = f'{BASE_URL}/api/survey/submit'
SURVEY_INIT_URL = f'{BASE_URL}/api/survey/init-questions'
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
        "username": f"surveytest{timestamp}",
        "email": f"surveytest{timestamp}@example.com",
        "password": "SurveyTest123!",
        "confirmPassword": "SurveyTest123!",
        "firstName": "설문",
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


def test_survey_init():
    """설문 질문 초기화 테스트"""
    try:
        response = requests.post(SURVEY_INIT_URL, timeout=10)
        print_test_result("설문 질문 초기화", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_get_survey_questions():
    """설문 질문 조회 테스트"""
    try:
        response = requests.get(SURVEY_QUESTIONS_URL, timeout=10)
        print_test_result("설문 질문 조회", response, 200)

        if response.status_code == 200:
            data = response.json()['data']
            questions = data['questions']
            print(f"📋 조회된 질문 수: {len(questions)}")

            # 카테고리별 질문 수 확인
            categories = {}
            for q in questions:
                cat = q['category']
                categories[cat] = categories.get(cat, 0) + 1

            print("📊 카테고리별 질문 수:")
            for cat, count in categories.items():
                print(f"  - {cat}: {count}개")

            return questions
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_submit_survey_responses(user_id, access_token, questions):
    """설문 응답 제출 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}

    # 샘플 응답 생성
    responses = []
    for i, question in enumerate(questions):
        if question['question_type'] == 'scale':
            # 1-5 척도
            response_value = (i % 5) + 1
        elif question['question_type'] == 'choice':
            # 선택지 중 첫 번째
            options = question.get('options', [])
            response_value = options[0] if options else '예'
        elif question['question_type'] == 'binary':
            # 예/아니오
            response_value = '예' if i % 2 == 0 else '아니오'
        else:
            response_value = 3  # 기본값

        responses.append({
            'question_id': question['question_id'],
            'answer_value': response_value
        })

    data = {'responses': responses}

    try:
        response = requests.post(SURVEY_SUBMIT_URL, json=data, headers=headers, timeout=10)
        print_test_result("설문 응답 제출", response, 200)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_submit_invalid_responses(user_id, access_token):
    """잘못된 설문 응답 제출 테스트"""
    headers = {'Authorization': f'Bearer {access_token}'}

    # 잘못된 응답 (존재하지 않는 질문 ID)
    data = {
        'responses': [
            {'question_id': 9999, 'answer_value': 3},  # 존재하지 않는 질문
            {'question_id': 1, 'answer_value': 10}     # 범위 초과 값
        ]
    }

    try:
        response = requests.post(SURVEY_SUBMIT_URL, json=data, headers=headers, timeout=10)
        print_test_result("잘못된 설문 응답 제출", response, 400)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def test_submit_without_token():
    """토큰 없이 설문 응답 제출 테스트"""
    data = {
        'responses': [
            {'question_id': 1, 'answer_value': 3}
        ]
    }

    try:
        response = requests.post(SURVEY_SUBMIT_URL, json=data, timeout=10)
        print_test_result("토큰 없이 설문 응답 제출", response, 401)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return None


def main():
    """메인 테스트 함수"""
    print("🧪 설문 조사 API 테스트를 시작합니다...")
    print(f"서버 주소: {BASE_URL}")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 서버 상태 확인
    if not test_server_health():
        print("❌ 서버가 실행되지 않았거나 응답하지 않습니다.")
        return

    print("✅ 서버가 정상적으로 응답합니다.")

    # 설문 질문 초기화
    print("\n📋 설문 질문을 초기화합니다...")
    test_survey_init()

    # 설문 질문 조회
    print("\n📋 설문 질문을 조회합니다...")
    questions = test_get_survey_questions()
    if not questions:
        print("❌ 설문 질문 조회에 실패했습니다.")
        return

    # 테스트용 사용자 생성 및 로그인
    print("\n📝 테스트용 사용자를 생성하고 로그인합니다...")
    user_id, access_token = create_and_login_test_user()
    if not user_id or not access_token:
        print("❌ 테스트용 사용자 생성 또는 로그인에 실패했습니다.")
        return

    # 테스트 실행
    test_cases = [
        ("정상적인 설문 응답 제출", lambda: test_submit_survey_responses(user_id, access_token, questions)),
        ("잘못된 설문 응답 제출", lambda: test_submit_invalid_responses(user_id, access_token)),
        ("토큰 없이 설문 응답 제출", test_submit_without_token)
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