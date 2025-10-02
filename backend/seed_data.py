"""
초기 데이터 생성 스크립트
데이터베이스에 샘플 취미 데이터를 생성합니다.
"""

from app import app, db
from app.models.hobby import Hobby
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_hobbies():
    """샘플 취미 데이터 생성"""

    hobbies_data = [
        # 운동 카테고리
        {
            'name': '요가',
            'category': '운동',
            'description': '몸과 마음의 균형을 찾는 건강한 운동입니다. 유연성과 근력을 동시에 향상시킬 수 있습니다.',
            'difficulty_level': 2,
            'physical_intensity': 3,
            'creativity_level': 2,
            'indoor_outdoor': 'both',
            'social_individual': 'both',
            'required_budget': 'low',
            'time_commitment': '주 2-3회, 1시간',
            'tutorial_video_url': 'https://example.com/yoga',
            'image_url': 'https://example.com/images/yoga.jpg'
        },
        {
            'name': '등산',
            'category': '운동',
            'description': '자연을 만끽하며 체력을 기를 수 있는 야외 활동입니다. 심폐지구력 향상에 효과적입니다.',
            'difficulty_level': 3,
            'physical_intensity': 4,
            'creativity_level': 1,
            'indoor_outdoor': 'outdoor',
            'social_individual': 'both',
            'required_budget': 'medium',
            'time_commitment': '주말, 4-6시간',
            'tutorial_video_url': 'https://example.com/hiking',
            'image_url': 'https://example.com/images/hiking.jpg'
        },
        {
            'name': '수영',
            'category': '운동',
            'description': '전신 운동으로 관절에 무리가 적고 건강에 좋습니다.',
            'difficulty_level': 2,
            'physical_intensity': 4,
            'creativity_level': 1,
            'indoor_outdoor': 'indoor',
            'social_individual': 'individual',
            'required_budget': 'medium',
            'time_commitment': '주 2-3회, 1시간',
            'tutorial_video_url': 'https://example.com/swimming',
            'image_url': 'https://example.com/images/swimming.jpg'
        },

        # 예술 카테고리
        {
            'name': '수채화',
            'category': '예술',
            'description': '물감과 붓으로 아름다운 그림을 그리는 활동입니다. 창의력과 집중력을 향상시킵니다.',
            'difficulty_level': 3,
            'physical_intensity': 1,
            'creativity_level': 5,
            'indoor_outdoor': 'indoor',
            'social_individual': 'individual',
            'required_budget': 'medium',
            'time_commitment': '자유',
            'tutorial_video_url': 'https://example.com/watercolor',
            'image_url': 'https://example.com/images/watercolor.jpg'
        },
        {
            'name': '도자기',
            'category': '예술',
            'description': '흙으로 그릇이나 작품을 만드는 전통 공예입니다.',
            'difficulty_level': 4,
            'physical_intensity': 2,
            'creativity_level': 5,
            'indoor_outdoor': 'indoor',
            'social_individual': 'both',
            'required_budget': 'high',
            'time_commitment': '주 1-2회, 2-3시간',
            'tutorial_video_url': 'https://example.com/pottery',
            'image_url': 'https://example.com/images/pottery.jpg'
        },
        {
            'name': '서예',
            'category': '예술',
            'description': '붓으로 아름다운 글씨를 쓰는 전통 예술입니다.',
            'difficulty_level': 3,
            'physical_intensity': 1,
            'creativity_level': 4,
            'indoor_outdoor': 'indoor',
            'social_individual': 'individual',
            'required_budget': 'low',
            'time_commitment': '자유',
            'tutorial_video_url': 'https://example.com/calligraphy',
            'image_url': 'https://example.com/images/calligraphy.jpg'
        },

        # 음악 카테고리
        {
            'name': '우쿨렐레',
            'category': '음악',
            'description': '배우기 쉬운 작은 현악기입니다. 기타보다 부담 없이 시작할 수 있습니다.',
            'difficulty_level': 2,
            'physical_intensity': 1,
            'creativity_level': 4,
            'indoor_outdoor': 'both',
            'social_individual': 'both',
            'required_budget': 'low',
            'time_commitment': '주 3-4회, 30분',
            'tutorial_video_url': 'https://example.com/ukulele',
            'image_url': 'https://example.com/images/ukulele.jpg'
        },
        {
            'name': '하모니카',
            'category': '음악',
            'description': '작고 휴대하기 좋은 악기로 언제 어디서나 연주할 수 있습니다.',
            'difficulty_level': 2,
            'physical_intensity': 1,
            'creativity_level': 3,
            'indoor_outdoor': 'both',
            'social_individual': 'both',
            'required_budget': 'low',
            'time_commitment': '자유',
            'tutorial_video_url': 'https://example.com/harmonica',
            'image_url': 'https://example.com/images/harmonica.jpg'
        },

        # 정원가꾸기 카테고리
        {
            'name': '텃밭 가꾸기',
            'category': '정원',
            'description': '직접 채소를 키워 수확하는 보람찬 활동입니다.',
            'difficulty_level': 2,
            'physical_intensity': 3,
            'creativity_level': 2,
            'indoor_outdoor': 'outdoor',
            'social_individual': 'individual',
            'required_budget': 'low',
            'time_commitment': '매일 30분',
            'tutorial_video_url': 'https://example.com/gardening',
            'image_url': 'https://example.com/images/gardening.jpg'
        },
        {
            'name': '분재',
            'category': '정원',
            'description': '작은 나무를 예술적으로 기르는 활동입니다.',
            'difficulty_level': 4,
            'physical_intensity': 1,
            'creativity_level': 4,
            'indoor_outdoor': 'both',
            'social_individual': 'individual',
            'required_budget': 'medium',
            'time_commitment': '매일 15분',
            'tutorial_video_url': 'https://example.com/bonsai',
            'image_url': 'https://example.com/images/bonsai.jpg'
        },

        # 공예 카테고리
        {
            'name': '목공예',
            'category': '공예',
            'description': '나무로 다양한 작품을 만드는 활동입니다.',
            'difficulty_level': 4,
            'physical_intensity': 3,
            'creativity_level': 4,
            'indoor_outdoor': 'both',
            'social_individual': 'individual',
            'required_budget': 'high',
            'time_commitment': '주 2-3회, 2-3시간',
            'tutorial_video_url': 'https://example.com/woodworking',
            'image_url': 'https://example.com/images/woodworking.jpg'
        },
        {
            'name': '뜨개질',
            'category': '공예',
            'description': '실로 옷이나 소품을 만드는 활동입니다.',
            'difficulty_level': 2,
            'physical_intensity': 1,
            'creativity_level': 3,
            'indoor_outdoor': 'indoor',
            'social_individual': 'both',
            'required_budget': 'low',
            'time_commitment': '자유',
            'tutorial_video_url': 'https://example.com/knitting',
            'image_url': 'https://example.com/images/knitting.jpg'
        },

        # 학습 카테고리
        {
            'name': '독서 토론',
            'category': '학습',
            'description': '책을 읽고 다른 사람들과 생각을 나누는 활동입니다.',
            'difficulty_level': 1,
            'physical_intensity': 1,
            'creativity_level': 3,
            'indoor_outdoor': 'both',
            'social_individual': 'social',
            'required_budget': 'low',
            'time_commitment': '주 1회, 2시간',
            'tutorial_video_url': 'https://example.com/reading',
            'image_url': 'https://example.com/images/reading.jpg'
        },
        {
            'name': '외국어 학습',
            'category': '학습',
            'description': '새로운 언어를 배워 세계를 넓히는 활동입니다.',
            'difficulty_level': 3,
            'physical_intensity': 1,
            'creativity_level': 2,
            'indoor_outdoor': 'both',
            'social_individual': 'both',
            'required_budget': 'medium',
            'time_commitment': '주 3-5회, 1시간',
            'tutorial_video_url': 'https://example.com/language',
            'image_url': 'https://example.com/images/language.jpg'
        },

        # 사교 카테고리
        {
            'name': '바둑',
            'category': '사교',
            'description': '전략적 사고를 요하는 전통 보드게임입니다.',
            'difficulty_level': 4,
            'physical_intensity': 1,
            'creativity_level': 4,
            'indoor_outdoor': 'both',
            'social_individual': 'social',
            'required_budget': 'low',
            'time_commitment': '주 2-3회, 2시간',
            'tutorial_video_url': 'https://example.com/go',
            'image_url': 'https://example.com/images/go.jpg'
        },
        {
            'name': '사진 촬영',
            'category': '예술',
            'description': '카메라로 아름다운 순간을 포착하는 활동입니다.',
            'difficulty_level': 3,
            'physical_intensity': 2,
            'creativity_level': 5,
            'indoor_outdoor': 'both',
            'social_individual': 'individual',
            'required_budget': 'high',
            'time_commitment': '자유',
            'tutorial_video_url': 'https://example.com/photography',
            'image_url': 'https://example.com/images/photography.jpg'
        }
    ]

    with app.app_context():
        # 기존 데이터 확인
        existing_count = Hobby.query.filter_by(is_deleted=False).count()

        if existing_count > 0:
            logger.info(f"이미 {existing_count}개의 취미 데이터가 존재합니다.")
            choice = input("기존 데이터를 삭제하고 새로 생성하시겠습니까? (y/N): ")
            if choice.lower() != 'y':
                logger.info("데이터 생성을 취소합니다.")
                return

            # 기존 데이터 삭제 (소프트 삭제)
            Hobby.query.update({'is_deleted': True})
            db.session.commit()
            logger.info("기존 데이터를 삭제했습니다.")

        # 새 데이터 생성
        created_count = 0
        for hobby_data in hobbies_data:
            hobby = Hobby(**hobby_data)
            db.session.add(hobby)
            created_count += 1

        db.session.commit()
        logger.info(f"✅ {created_count}개의 취미 데이터가 성공적으로 생성되었습니다!")

        # 카테고리별 통계
        categories = db.session.query(
            Hobby.category,
            db.func.count(Hobby.hobby_id)
        ).filter_by(is_deleted=False).group_by(Hobby.category).all()

        print("\n📊 카테고리별 통계:")
        for category, count in categories:
            print(f"  - {category}: {count}개")


if __name__ == '__main__':
    print("="*60)
    print("취미 추천 시스템 - 초기 데이터 생성")
    print("="*60)

    try:
        create_sample_hobbies()
    except Exception as e:
        logger.error(f"데이터 생성 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
