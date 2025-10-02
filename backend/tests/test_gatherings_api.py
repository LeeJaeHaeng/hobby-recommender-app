"""
모임 API 테스트 스크립트
모임 생성, 조회, 수정, 삭제 등을 테스트합니다.
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def print_response(title, response):
    """응답 출력"""
    print(f"\n{'='*70}")
    print(f"[{title}]")
    print(f"Status Code: {response.status_code}")
    if response.status_code < 500:
        try:
            print(f"Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(f"Raw Response: {response.text}")
    else:
        print(f"Error: {response.text[:200]}")
    print('='*70)

def test_gatherings_api():
    """모임 API 테스트"""

    print("🧪 모임 API 테스트 시작\n")

    # ========================================
    # 1. 테스트 사용자 준비
    # ========================================
    print("\n📝 1단계: 테스트 사용자 로그인")

    # 회원가입
    signup_data = {
        'username': f'gathering_test_user',
        'email': 'gathering_test@test.com',
        'password': 'Test1234!',
        'name': '모임테스트',
        'birth_year': 1980,
        'gender': 'female'
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
        'username': 'gathering_test_user',
        'password': 'Test1234!'
    }

    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"❌ 로그인 실패: {response.json()}")
        return

    token = response.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print(f"✅ 로그인 성공")

    # ========================================
    # 2. 모임 목록 조회 (전체)
    # ========================================
    print("\n\n📋 2단계: 모임 목록 조회")
    response = requests.get(f'{BASE_URL}/api/gatherings')
    print_response("전체 모임 목록", response)

    # ========================================
    # 3. 모임 생성
    # ========================================
    print("\n\n✨ 3단계: 모임 생성")

    # 취미 목록 조회 (모임 생성용)
    response = requests.get(f'{BASE_URL}/api/hobbies', params={'per_page': 1})
    if response.status_code == 200:
        hobbies = response.json()['data']['hobbies']
        if hobbies:
            hobby_id = hobbies[0]['hobby_id']
            print(f"📌 테스트용 취미 ID: {hobby_id} ({hobbies[0]['name']})")

            # 모임 생성
            gathering_data = {
                'hobby_id': hobby_id,
                'name': '서울 등산 동호회',
                'description': '매주 주말 서울 근교 산을 등반하는 모임입니다.',
                'location': '서울특별시 종로구',
                'region': '서울',
                'meeting_type': 'offline',
                'schedule_info': '매주 토요일 오전 8시',
                'member_count': 15,
                'contact_info': '010-1234-5678',
                'website_url': 'https://example.com/hiking',
                'is_active': True
            }

            response = requests.post(f'{BASE_URL}/api/gatherings',
                                    json=gathering_data,
                                    headers=headers)
            print_response("모임 생성", response)

            created_gathering_id = None
            if response.status_code == 201:
                created_gathering_id = response.json()['data']['gathering_id']
                print(f"\n✅ 생성된 모임 ID: {created_gathering_id}")

            # ========================================
            # 4. 모임 상세 조회
            # ========================================
            if created_gathering_id:
                print(f"\n\n🔍 4단계: 모임 상세 조회 (ID: {created_gathering_id})")
                response = requests.get(f'{BASE_URL}/api/gatherings/{created_gathering_id}')
                print_response(f"모임 ID {created_gathering_id} 상세 정보", response)

                # ========================================
                # 5. 모임 수정
                # ========================================
                print(f"\n\n✏️ 5단계: 모임 정보 수정")
                update_data = {
                    'name': '서울 등산 동호회 (수정됨)',
                    'description': '수정된 설명입니다.',
                    'member_count': 20
                }

                response = requests.put(f'{BASE_URL}/api/gatherings/{created_gathering_id}',
                                       json=update_data,
                                       headers=headers)
                print_response("모임 수정", response)

                # ========================================
                # 6. 지역별 필터링
                # ========================================
                print("\n\n🗺️ 6단계: 지역별 모임 조회")
                response = requests.get(f'{BASE_URL}/api/gatherings',
                                       params={'region': '서울'})
                print_response("서울 지역 모임", response)

                # ========================================
                # 7. 취미별 모임 조회
                # ========================================
                print(f"\n\n🎯 7단계: 취미별 모임 조회 (취미 ID: {hobby_id})")
                response = requests.get(f'{BASE_URL}/api/gatherings/hobby/{hobby_id}')
                print_response(f"취미 ID {hobby_id}의 모임 목록", response)

                # ========================================
                # 8. 지역 목록 조회
                # ========================================
                print("\n\n📍 8단계: 지역 목록 조회")
                response = requests.get(f'{BASE_URL}/api/gatherings/regions')
                print_response("사용 가능한 지역 목록", response)

                # ========================================
                # 9. 인기 모임 조회
                # ========================================
                print("\n\n🔥 9단계: 인기 모임 조회")
                response = requests.get(f'{BASE_URL}/api/gatherings/popular',
                                       params={'limit': 5})
                print_response("인기 모임 TOP 5", response)

                # ========================================
                # 10. 모임 유형별 필터링
                # ========================================
                print("\n\n💻 10단계: 모임 유형별 조회")
                response = requests.get(f'{BASE_URL}/api/gatherings',
                                       params={'meeting_type': 'offline'})
                print_response("오프라인 모임", response)

                # ========================================
                # 11. 검색 기능
                # ========================================
                print("\n\n🔎 11단계: 모임 검색")
                response = requests.get(f'{BASE_URL}/api/gatherings',
                                       params={'search': '등산'})
                print_response("'등산' 검색 결과", response)

                # ========================================
                # 12. 복합 필터링
                # ========================================
                print("\n\n🎲 12단계: 복합 필터링 (서울 + 오프라인)")
                response = requests.get(f'{BASE_URL}/api/gatherings',
                                       params={
                                           'region': '서울',
                                           'meeting_type': 'offline',
                                           'is_active': 'true'
                                       })
                print_response("서울 + 오프라인 모임", response)

                # ========================================
                # 13. 모임 삭제 (비활성화)
                # ========================================
                print(f"\n\n🗑️ 13단계: 모임 삭제 (ID: {created_gathering_id})")
                response = requests.delete(f'{BASE_URL}/api/gatherings/{created_gathering_id}',
                                          headers=headers)
                print_response("모임 삭제", response)

                # 삭제 후 조회
                print("\n📋 삭제 후 모임 조회:")
                response = requests.get(f'{BASE_URL}/api/gatherings/{created_gathering_id}')
                print_response("삭제된 모임 정보", response)

                # 비활성 모임 포함 조회
                print("\n📋 비활성 모임 포함 조회:")
                response = requests.get(f'{BASE_URL}/api/gatherings',
                                       params={'is_active': 'false'})
                print_response("비활성 모임 목록", response)

        else:
            print("❌ 테스트할 취미가 없습니다.")
    else:
        print("❌ 취미 목록 조회 실패")

    print("\n" + "="*70)
    print("✅ 모든 모임 API 테스트 완료!")
    print("="*70)

if __name__ == '__main__':
    try:
        test_gatherings_api()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("Flask 서버가 실행 중인지 확인하세요: python app.py")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
