"""
추천 API 테스트 스크립트
사용자 맞춤 추천, 인기 취미, 유사 취미 등을 테스트합니다.
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

def test_recommendations_api():
    """추천 API 테스트"""

    print("🧪 추천 API 테스트 시작\n")

    # ========================================
    # 1. 테스트 사용자 준비
    # ========================================
    print("\n📝 1단계: 테스트 사용자 준비")

    # 회원가입
    signup_data = {
        'username': f'recommend_test_user',
        'email': 'recommend_test@test.com',
        'password': 'Test1234!',
        'name': '추천테스트',
        'birth_year': 1975,
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
        'username': 'recommend_test_user',
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
    # 2. 설문 응답 (프로필 생성)
    # ========================================
    print("\n📝 2단계: 설문 응답 제출")

    # 설문 질문 조회
    response = requests.get(f'{BASE_URL}/api/survey/questions')
    if response.status_code != 200:
        print(f"❌ 설문 질문 조회 실패")
        # 설문 초기화 시도
        requests.post(f'{BASE_URL}/api/survey/init-questions')
        response = requests.get(f'{BASE_URL}/api/survey/questions')

    questions = response.json()['data']['questions']
    print(f"📋 설문 질문 {len(questions)}개 조회 완료")

    # 설문 응답 생성 (예시)
    survey_responses = []
    for q in questions:
        if q['question_type'] == 'scale':
            # 야외 활동, 사회성향 높게 설정
            if '야외' in q['question_text'] or '사회' in q['question_text']:
                answer = 5
            elif '혼자' in q['question_text'] or '실내' in q['question_text']:
                answer = 2
            else:
                answer = 4
            survey_responses.append({
                'question_id': q['question_id'],
                'answer_value': answer
            })
        elif q['question_type'] == 'binary':
            survey_responses.append({
                'question_id': q['question_id'],
                'answer_value': True
            })
        elif q['question_type'] == 'choice':
            # 첫 번째 선택지 선택
            choices = q['options'].get('choices', [])
            if choices:
                survey_responses.append({
                    'question_id': q['question_id'],
                    'answer_value': choices[0]['value']
                })

    # 설문 제출
    response = requests.post(f'{BASE_URL}/api/survey/submit',
                            json={'responses': survey_responses},
                            headers=headers)
    if response.status_code == 200:
        print(f"✅ 설문 응답 제출 완료")
        profile = response.json()['data']['user_profile']
        print(f"   프로필: {json.dumps(profile, indent=4, ensure_ascii=False)}")
    else:
        print(f"❌ 설문 제출 실패: {response.json()}")

    # ========================================
    # 3. 인기 취미 조회 (인증 불필요)
    # ========================================
    print("\n\n🔥 3단계: 인기 취미 조회")
    response = requests.get(f'{BASE_URL}/api/recommendations/popular',
                           params={'limit': 5})
    print_response("인기 취미 TOP 5", response)

    # ========================================
    # 4. 사용자 맞춤 추천 (인증 필요)
    # ========================================
    print("\n\n✨ 4단계: 사용자 맞춤 추천")
    response = requests.get(f'{BASE_URL}/api/recommendations',
                           params={'limit': 10, 'exclude_rated': 'true'},
                           headers=headers)
    print_response("맞춤 추천 TOP 10", response)

    # 추천 결과에서 첫 번째 취미 ID 저장
    recommended_hobby_id = None
    if response.status_code == 200:
        recommendations = response.json()['data']['recommendations']
        if recommendations:
            recommended_hobby_id = recommendations[0]['hobby']['hobby_id']
            print(f"\n📌 첫 번째 추천 취미 ID: {recommended_hobby_id}")

    # ========================================
    # 5. 유사 취미 추천
    # ========================================
    if recommended_hobby_id:
        print(f"\n\n🔍 5단계: 유사 취미 추천 (기준: 취미 ID {recommended_hobby_id})")
        response = requests.get(
            f'{BASE_URL}/api/recommendations/similar/{recommended_hobby_id}',
            params={'limit': 5}
        )
        print_response(f"취미 ID {recommended_hobby_id}와 유사한 취미", response)
    else:
        print("\n⚠️ 5단계 스킵: 추천 취미가 없음")

    # ========================================
    # 6. 취미 평가 후 재추천
    # ========================================
    print("\n\n⭐ 6단계: 취미 평가 후 재추천 테스트")

    if recommended_hobby_id:
        # 첫 번째 추천 취미에 평가
        rating_data = {
            'rating': 5,
            'review_text': '정말 좋은 추천이었습니다!',
            'experienced': False
        }
        response = requests.post(
            f'{BASE_URL}/api/hobbies/{recommended_hobby_id}/rate',
            json=rating_data,
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ 취미 ID {recommended_hobby_id} 평가 완료 (5점)")

        # 재추천 (평가한 취미 제외)
        print("\n📊 재추천 조회 (평가한 취미 제외):")
        response = requests.get(f'{BASE_URL}/api/recommendations',
                               params={'limit': 5, 'exclude_rated': 'true'},
                               headers=headers)
        print_response("재추천 결과", response)

    # ========================================
    # 7. 카테고리별 추천
    # ========================================
    print("\n\n📂 7단계: 카테고리별 추천")

    # 카테고리 목록 조회
    response = requests.get(f'{BASE_URL}/api/hobbies/categories')
    if response.status_code == 200:
        categories = response.json()['data']['categories']
        if categories:
            # 첫 번째 카테고리로 추천 조회
            category_name = categories[0]['category']
            print(f"\n📌 '{category_name}' 카테고리 추천:")
            response = requests.get(
                f'{BASE_URL}/api/recommendations/category/{category_name}',
                params={'limit': 5}
            )
            print_response(f"{category_name} 카테고리 추천", response)

    # ========================================
    # 8. 추천 점수 상세 분석
    # ========================================
    print("\n\n📈 8단계: 추천 점수 상세 분석")
    response = requests.get(f'{BASE_URL}/api/recommendations',
                           params={'limit': 3},
                           headers=headers)

    if response.status_code == 200:
        recommendations = response.json()['data']['recommendations']
        print("\n" + "="*70)
        print("추천 점수 상세 분석 (TOP 3)")
        print("="*70)

        for i, rec in enumerate(recommendations[:3], 1):
            hobby = rec['hobby']
            breakdown = rec['score_breakdown']
            print(f"\n{i}. {hobby['name']}")
            print(f"   매칭률: {rec['match_percentage']}%")
            print(f"   총점: {rec['recommendation_score']:.4f}")
            print(f"   상세 점수:")
            print(f"     - 프로필 매칭: {breakdown['profile_match']:.4f}")
            print(f"     - 협업 필터링: {breakdown['collaborative_filtering']:.4f}")
            print(f"     - 인기도: {breakdown['popularity']:.4f}")
            print(f"   특성:")
            print(f"     - 카테고리: {hobby['category']}")
            print(f"     - 실내/외: {hobby['indoor_outdoor']}")
            print(f"     - 사회성/개인: {hobby['social_individual']}")
            print(f"     - 예산: {hobby['required_budget']}")
            print(f"     - 난이도: {hobby['difficulty_level']}/5")
            print(f"     - 평균 평점: {hobby.get('average_rating', 0)}/5")

    print("\n" + "="*70)
    print("✅ 모든 추천 API 테스트 완료!")
    print("="*70)

if __name__ == '__main__':
    try:
        test_recommendations_api()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("Flask 서버가 실행 중인지 확인하세요: python app.py")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
