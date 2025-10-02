"""
취미 API 테스트 스크립트
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def print_response(title, response):
    """응답 출력"""
    print(f"\n{'='*60}")
    print(f"[{title}]")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print('='*60)

def test_hobbies_api():
    """취미 API 테스트"""

    print("🧪 취미 API 테스트 시작\n")

    # 1. 취미 목록 조회
    print("\n1️⃣ 취미 목록 조회 (GET /api/hobbies)")
    response = requests.get(f'{BASE_URL}/api/hobbies')
    print_response("취미 목록", response)

    # 2. 카테고리 필터링
    print("\n2️⃣ 카테고리 필터링 (GET /api/hobbies?category=운동)")
    response = requests.get(f'{BASE_URL}/api/hobbies', params={'category': '운동'})
    print_response("카테고리 필터", response)

    # 3. 검색
    print("\n3️⃣ 검색 (GET /api/hobbies?search=요가)")
    response = requests.get(f'{BASE_URL}/api/hobbies', params={'search': '요가'})
    print_response("검색", response)

    # 4. 카테고리 목록
    print("\n4️⃣ 카테고리 목록 (GET /api/hobbies/categories)")
    response = requests.get(f'{BASE_URL}/api/hobbies/categories')
    print_response("카테고리 목록", response)

    # 5. 취미 상세 조회 (ID 1)
    print("\n5️⃣ 취미 상세 조회 (GET /api/hobbies/1)")
    response = requests.get(f'{BASE_URL}/api/hobbies/1')
    print_response("취미 상세", response)

    # 6. 인증 필요한 API 테스트 (회원가입 & 로그인)
    print("\n6️⃣ 회원가입 및 로그인")

    # 테스트 사용자 회원가입
    signup_data = {
        'username': f'testuser_hobbies',
        'email': 'testuser_hobbies@test.com',
        'password': 'Test1234!',
        'name': '테스트사용자',
        'birth_year': 1980,
        'gender': 'male'
    }

    response = requests.post(f'{BASE_URL}/api/users/signup', json=signup_data)
    if response.status_code == 201:
        print("✅ 회원가입 성공")
    elif response.status_code == 409:
        print("⚠️ 이미 가입된 사용자 (계속 진행)")
    else:
        print(f"❌ 회원가입 실패: {response.json()}")

    # 로그인
    login_data = {
        'username': 'testuser_hobbies',
        'password': 'Test1234!'
    }

    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    if response.status_code == 200:
        token = response.json()['data']['access_token']
        print(f"✅ 로그인 성공")

        headers = {'Authorization': f'Bearer {token}'}

        # 7. 취미 평가
        print("\n7️⃣ 취미 평가 (POST /api/hobbies/1/rate)")
        rating_data = {
            'rating': 5,
            'review_text': '정말 좋은 취미입니다! 추천합니다.',
            'experienced': True
        }

        response = requests.post(f'{BASE_URL}/api/hobbies/1/rate',
                                json=rating_data,
                                headers=headers)
        print_response("취미 평가", response)

        # 8. 취미 평가 목록 조회
        print("\n8️⃣ 취미 평가 목록 (GET /api/hobbies/1/ratings)")
        response = requests.get(f'{BASE_URL}/api/hobbies/1/ratings')
        print_response("평가 목록", response)

    else:
        print(f"❌ 로그인 실패: {response.json()}")

    # 9. 필터 조합 테스트
    print("\n9️⃣ 필터 조합 (실내 + 저예산 + 난이도 1-3)")
    params = {
        'indoor_outdoor': 'indoor',
        'budget': 'low',
        'difficulty_min': 1,
        'difficulty_max': 3
    }
    response = requests.get(f'{BASE_URL}/api/hobbies', params=params)
    print_response("필터 조합", response)

    print("\n✅ 모든 테스트 완료!")

if __name__ == '__main__':
    try:
        test_hobbies_api()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("Flask 서버가 실행 중인지 확인하세요: python app.py")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
