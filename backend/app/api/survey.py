"""
설문 조사 관련 API 엔드포인트
설문 질문 조회, 응답 제출, 성향 분석 등
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User, UserProfile, SurveyQuestion, SurveyResponse
import logging
from datetime import datetime
from sqlalchemy import func

logger = logging.getLogger(__name__)

survey_bp = Blueprint('survey', __name__, url_prefix='/api/survey')


@survey_bp.route('/questions', methods=['GET'])
def get_survey_questions():
    """
    설문 질문 목록 조회
    GET /api/survey/questions
    """
    try:
        # 모든 설문 질문 조회
        questions = SurveyQuestion.query.order_by(SurveyQuestion.question_id).all()

        if not questions:
            # 설문 질문이 없으면 샘플 데이터 생성
            return jsonify({
                'error': 'No Questions Found',
                'message': '설문 질문이 없습니다. 관리자에게 문의하세요.',
                'suggestion': '설문 질문을 초기화하려면 /api/survey/init-questions를 호출하세요.'
            }), 404

        # 카테고리별로 그룹화
        questions_by_category = {}
        for question in questions:
            category = question.category
            if category not in questions_by_category:
                questions_by_category[category] = []
            questions_by_category[category].append(question.to_dict())

        # 전체 질문 리스트
        questions_list = [question.to_dict() for question in questions]

        return jsonify({
            'status': 'success',
            'data': {
                'questions': questions_list,
                'questions_by_category': questions_by_category,
                'total_questions': len(questions_list),
                'categories': list(questions_by_category.keys())
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting survey questions: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '설문 질문 조회 중 오류가 발생했습니다.'
        }), 500


@survey_bp.route('/init-questions', methods=['POST'])
def init_survey_questions():
    """
    설문 질문 초기화 (개발용)
    POST /api/survey/init-questions
    """
    try:
        # 기존 질문이 있는지 확인
        existing_count = SurveyQuestion.query.count()
        if existing_count > 0:
            return jsonify({
                'message': f'이미 {existing_count}개의 설문 질문이 존재합니다.',
                'status': 'skipped'
            }), 200

        # 20개 설문 질문 데이터
        sample_questions = [
            {
                'question_text': '새로운 사람들과 만나는 것을 좋아하시나요?',
                'question_type': 'scale',
                'category': '사회성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '혼자만의 시간을 갖는 것을 선호하시나요?',
                'question_type': 'scale',
                'category': '사회성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '야외 활동을 즐기시나요?',
                'question_type': 'scale',
                'category': '활동성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '실내에서 하는 취미를 선호하시나요?',
                'question_type': 'scale',
                'category': '활동성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '창작 활동(그림, 음악, 글쓰기 등)에 관심이 있으신가요?',
                'question_type': 'scale',
                'category': '창의성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '손으로 만드는 공예 활동을 좋아하시나요?',
                'question_type': 'scale',
                'category': '창의성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '새로운 지식을 배우는 것을 즐기시나요?',
                'question_type': 'scale',
                'category': '학습성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '책 읽기를 좋아하시나요?',
                'question_type': 'scale',
                'category': '학습성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '몸을 움직이는 활동을 선호하시나요?',
                'question_type': 'scale',
                'category': '신체활동',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '정적인 활동(독서, 바둑 등)을 좋아하시나요?',
                'question_type': 'scale',
                'category': '신체활동',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '취미 활동에 얼마나 투자할 의향이 있으신가요?',
                'question_type': 'choice',
                'category': '예산성향',
                'options': {
                    'choices': [
                        {'value': 'low', 'label': '월 10만원 이하'},
                        {'value': 'medium', 'label': '월 10-30만원'},
                        {'value': 'high', 'label': '월 30만원 이상'}
                    ]
                }
            },
            {
                'question_text': '비싼 장비가 필요한 취미도 시도해보실 의향이 있나요?',
                'question_type': 'binary',
                'category': '예산성향',
                'options': {'choices': [{'value': True, 'label': '예'}, {'value': False, 'label': '아니오'}]}
            },
            {
                'question_text': '경쟁이 있는 활동을 좋아하시나요?',
                'question_type': 'scale',
                'category': '성격성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '협력이 필요한 팀 활동을 선호하시나요?',
                'question_type': 'scale',
                'category': '성격성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '규칙적인 스케줄의 활동을 좋아하시나요?',
                'question_type': 'scale',
                'category': '라이프스타일',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '즉흥적이고 자유로운 활동을 선호하시나요?',
                'question_type': 'scale',
                'category': '라이프스타일',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '새로운 도전을 즐기시나요?',
                'question_type': 'scale',
                'category': '모험성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '안전하고 익숙한 활동을 선호하시나요?',
                'question_type': 'scale',
                'category': '모험성향',
                'options': {'min': 1, 'max': 5, 'labels': {'1': '전혀 아니다', '3': '보통이다', '5': '매우 그렇다'}}
            },
            {
                'question_text': '결과물이 남는 활동을 선호하시나요?',
                'question_type': 'binary',
                'category': '성취성향',
                'options': {'choices': [{'value': True, 'label': '예'}, {'value': False, 'label': '아니오'}]}
            },
            {
                'question_text': '과정 자체를 즐기는 활동을 좋아하시나요?',
                'question_type': 'binary',
                'category': '성취성향',
                'options': {'choices': [{'value': True, 'label': '예'}, {'value': False, 'label': '아니오'}]}
            }
        ]

        # 질문들을 데이터베이스에 저장
        questions_added = []
        for i, q_data in enumerate(sample_questions, 1):
            question = SurveyQuestion(
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                category=q_data['category'],
                options=q_data['options']
            )
            db.session.add(question)
            questions_added.append(q_data['question_text'][:50] + '...')

        db.session.commit()
        logger.info(f"Added {len(sample_questions)} survey questions to database")

        return jsonify({
            'status': 'success',
            'message': f'{len(sample_questions)}개의 설문 질문이 성공적으로 추가되었습니다.',
            'data': {
                'questions_added': len(sample_questions),
                'categories': list(set(q['category'] for q in sample_questions))
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing survey questions: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '설문 질문 초기화 중 오류가 발생했습니다.'
        }), 500


@survey_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_survey_responses():
    """
    설문 응답 제출
    POST /api/survey/submit
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'responses' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': '설문 응답 데이터가 필요합니다.'
            }), 400

        responses_data = data['responses']
        if not isinstance(responses_data, list):
            return jsonify({
                'error': 'Bad Request',
                'message': '응답 데이터는 배열 형태여야 합니다.'
            }), 400

        # 사용자 확인
        user = User.query.filter_by(user_id=current_user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 기존 응답 삭제 (재제출 허용)
        SurveyResponse.query.filter_by(user_id=current_user_id).delete()

        # 응답 검증 및 저장
        saved_responses = []
        validation_errors = []

        for i, response_data in enumerate(responses_data):
            try:
                question_id = response_data.get('question_id')
                answer_value = response_data.get('answer_value')

                if not question_id:
                    validation_errors.append({'index': i, 'message': 'question_id가 필요합니다.'})
                    continue

                if answer_value is None:
                    validation_errors.append({'index': i, 'message': 'answer_value가 필요합니다.'})
                    continue

                # 질문 존재 확인
                question = SurveyQuestion.query.get(question_id)
                if not question:
                    validation_errors.append({'index': i, 'message': f'질문 ID {question_id}를 찾을 수 없습니다.'})
                    continue

                # 답변 값 검증
                if question.question_type == 'scale':
                    try:
                        answer_int = int(answer_value)
                        min_val = question.options.get('min', 1)
                        max_val = question.options.get('max', 5)
                        if not (min_val <= answer_int <= max_val):
                            validation_errors.append({
                                'index': i,
                                'message': f'답변 값은 {min_val}과 {max_val} 사이여야 합니다.'
                            })
                            continue
                        answer_value = str(answer_int)
                    except (ValueError, TypeError):
                        validation_errors.append({'index': i, 'message': 'scale 타입 질문의 답변은 숫자여야 합니다.'})
                        continue

                elif question.question_type == 'binary':
                    if answer_value not in [True, False, 'true', 'false', '1', '0', 1, 0]:
                        validation_errors.append({'index': i, 'message': 'binary 타입 질문의 답변은 true/false여야 합니다.'})
                        continue
                    answer_value = str(answer_value).lower()

                elif question.question_type == 'choice':
                    # choice 타입은 options의 options 배열에서 valid한 value인지 확인
                    valid_choices = question.options.get('options', [])
                    if answer_value not in valid_choices:
                        validation_errors.append({
                            'index': i,
                            'message': f'유효하지 않은 선택입니다. 가능한 값: {valid_choices}'
                        })
                        continue
                    answer_value = str(answer_value)

                # 응답 저장
                survey_response = SurveyResponse(
                    user_id=current_user_id,
                    question_id=question_id,
                    answer_value=answer_value
                )
                db.session.add(survey_response)
                saved_responses.append({
                    'question_id': question_id,
                    'question_text': question.question_text,
                    'answer_value': answer_value,
                    'category': question.category
                })

            except Exception as e:
                validation_errors.append({'index': i, 'message': f'응답 처리 중 오류: {str(e)}'})

        # 검증 에러가 있으면 반환
        if validation_errors:
            db.session.rollback()
            return jsonify({
                'error': 'Validation Error',
                'message': '일부 응답에 오류가 있습니다.',
                'validation_errors': validation_errors
            }), 400

        try:
            # 응답 저장 후 사용자 프로필 업데이트
            db.session.commit()

            # 프로필 선호도 계산 및 업데이트
            updated_profile = calculate_and_update_preferences(current_user_id)

            logger.info(f"Survey responses submitted for user {current_user_id}: {len(saved_responses)} responses")

            return jsonify({
                'status': 'success',
                'message': '설문 응답이 성공적으로 제출되었습니다.',
                'data': {
                    'responses_count': len(saved_responses),
                    'user_profile': updated_profile,
                    'submitted_at': datetime.utcnow().isoformat()
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during survey submission: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Database Error',
                'message': '설문 응답 저장 중 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error during survey submission: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '설문 응답 처리 중 예상치 못한 오류가 발생했습니다.'
        }), 500


def calculate_and_update_preferences(user_id):
    """설문 응답을 바탕으로 사용자 선호도 계산 및 업데이트"""
    try:
        # 사용자의 모든 응답 조회
        responses = db.session.query(SurveyResponse, SurveyQuestion).join(
            SurveyQuestion, SurveyResponse.question_id == SurveyQuestion.question_id
        ).filter(SurveyResponse.user_id == user_id).all()

        if not responses:
            return None

        # 카테고리별 점수 계산
        category_scores = {}
        category_counts = {}

        for response, question in responses:
            category = question.category

            if category not in category_scores:
                category_scores[category] = 0
                category_counts[category] = 0

            # 점수 계산 (1-5 스케일을 0-1로 정규화)
            if question.question_type == 'scale':
                try:
                    score = int(response.answer_value)
                    min_val = question.options.get('min', 1)
                    max_val = question.options.get('max', 5)
                    normalized_score = (score - min_val) / (max_val - min_val)
                    category_scores[category] += normalized_score
                    category_counts[category] += 1
                except:
                    continue
            elif question.question_type == 'binary':
                score = 1.0 if response.answer_value.lower() in ['true', '1'] else 0.0
                category_scores[category] += score
                category_counts[category] += 1

        # 카테고리별 평균 계산
        preferences = {}
        for category in category_scores:
            if category_counts[category] > 0:
                preferences[category] = category_scores[category] / category_counts[category]

        # 사용자 프로필 업데이트
        user = User.query.get(user_id)
        if not user.profile:
            user.profile = UserProfile(user_id=user_id)
            db.session.add(user.profile)

        # 카테고리 매핑
        category_mapping = {
            '활동성향': 'outdoor_preference',
            '사회성향': 'social_preference',
            '창의성향': 'creative_preference',
            '학습성향': 'learning_preference',
            '신체활동': 'physical_activity'
        }

        # 예산 설정 (예산성향 카테고리에서)
        budget_responses = [r for r, q in responses if q.category == '예산성향' and q.question_type == 'choice']
        if budget_responses:
            budget_response = budget_responses[0]  # 첫 번째 예산 관련 응답 사용
            user.profile.budget_level = budget_response.answer_value

        # 선호도 업데이트
        for category, preference_field in category_mapping.items():
            if category in preferences:
                setattr(user.profile, preference_field, preferences[category])

        db.session.commit()

        # 업데이트된 프로필 반환
        return {
            'outdoor_preference': float(user.profile.outdoor_preference),
            'social_preference': float(user.profile.social_preference),
            'creative_preference': float(user.profile.creative_preference),
            'learning_preference': float(user.profile.learning_preference),
            'physical_activity': float(user.profile.physical_activity),
            'budget_level': user.profile.budget_level
        }

    except Exception as e:
        logger.error(f"Error calculating preferences for user {user_id}: {str(e)}", exc_info=True)
        return None


@survey_bp.route('/responses/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_responses(user_id):
    """
    사용자 설문 응답 조회
    GET /api/survey/responses/<user_id>
    """
    try:
        current_user_id = get_jwt_identity()

        # 본인의 응답만 조회 가능
        if current_user_id != user_id:
            return jsonify({
                'error': 'Access Denied',
                'message': '본인의 설문 응답만 조회할 수 있습니다.'
            }), 403

        # 사용자 응답 조회
        responses = db.session.query(SurveyResponse, SurveyQuestion).join(
            SurveyQuestion, SurveyResponse.question_id == SurveyQuestion.question_id
        ).filter(SurveyResponse.user_id == user_id).order_by(SurveyQuestion.question_id).all()

        if not responses:
            return jsonify({
                'status': 'success',
                'data': {
                    'responses': [],
                    'total_responses': 0,
                    'message': '아직 설문에 응답하지 않았습니다.'
                }
            }), 200

        # 응답 데이터 구성
        response_list = []
        for response, question in responses:
            response_list.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'category': question.category,
                'answer_value': response.answer_value,
                'created_at': response.created_at.isoformat() if response.created_at else None
            })

        return jsonify({
            'status': 'success',
            'data': {
                'responses': response_list,
                'total_responses': len(response_list)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting user responses: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '설문 응답 조회 중 오류가 발생했습니다.'
        }), 500