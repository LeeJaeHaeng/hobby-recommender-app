"""
취미 추천 관련 API 엔드포인트
사용자 맞춤 추천, 인기 취미, 유사 취미 등
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.hobby import Hobby, UserHobbyRating
from app.models.user import User, UserProfile
import logging
from sqlalchemy import func, desc, and_
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')


def calculate_hobby_score(hobby, user_profile):
    """
    사용자 프로필과 취미 특성을 기반으로 매칭 점수 계산
    점수 범위: 0.0 ~ 1.0
    """
    score = 0.0
    weights = 0.0

    # 1. 실내/외 선호도 (가중치: 0.2)
    outdoor_pref = float(user_profile.outdoor_preference) if user_profile.outdoor_preference else 0.5
    if hobby.indoor_outdoor == 'outdoor':
        score += outdoor_pref * 0.2
        weights += 0.2
    elif hobby.indoor_outdoor == 'indoor':
        score += (1 - outdoor_pref) * 0.2
        weights += 0.2
    else:  # both
        score += 0.15  # 중립적인 점수
        weights += 0.2

    # 2. 사회성/개인 선호도 (가중치: 0.2)
    social_pref = float(user_profile.social_preference) if user_profile.social_preference else 0.5
    if hobby.social_individual == 'social':
        score += social_pref * 0.2
        weights += 0.2
    elif hobby.social_individual == 'individual':
        score += (1 - social_pref) * 0.2
        weights += 0.2
    else:  # both
        score += 0.15
        weights += 0.2

    # 3. 창의성 (가중치: 0.15)
    creative_pref = float(user_profile.creative_preference) if user_profile.creative_preference else 0.5
    # creativity_level을 0~1로 정규화 (1~5 -> 0~1)
    creativity_normalized = (hobby.creativity_level - 1) / 4.0
    # 차이가 적을수록 높은 점수
    creativity_diff = abs(creative_pref - creativity_normalized)
    score += (1 - creativity_diff) * 0.15
    weights += 0.15

    # 4. 학습 성향 (가중치: 0.1)
    # 학습 선호도가 높으면 난이도 높은 취미 선호
    learning_pref = float(user_profile.learning_preference) if user_profile.learning_preference else 0.5
    difficulty_normalized = (hobby.difficulty_level - 1) / 4.0
    learning_diff = abs(learning_pref - difficulty_normalized)
    score += (1 - learning_diff) * 0.1
    weights += 0.1

    # 5. 신체 활동 (가중치: 0.2)
    physical_pref = float(user_profile.physical_activity) if user_profile.physical_activity else 0.5
    physical_normalized = (hobby.physical_intensity - 1) / 4.0
    physical_diff = abs(physical_pref - physical_normalized)
    score += (1 - physical_diff) * 0.2
    weights += 0.2

    # 6. 예산 (가중치: 0.15)
    budget_score = 0
    if user_profile.budget_level == hobby.required_budget:
        budget_score = 1.0
    elif (user_profile.budget_level == 'high' and hobby.required_budget == 'medium') or \
         (user_profile.budget_level == 'medium' and hobby.required_budget == 'low'):
        budget_score = 0.7  # 여유가 있으면 낮은 예산도 괜찮음
    elif (user_profile.budget_level == 'low' and hobby.required_budget == 'medium'):
        budget_score = 0.3  # 예산 초과는 낮은 점수
    else:  # low -> high 또는 그 반대
        budget_score = 0.1

    score += budget_score * 0.15
    weights += 0.15

    # 정규화
    if weights > 0:
        final_score = score / weights
    else:
        final_score = 0.5

    return round(final_score, 4)


def get_collaborative_filtering_score(user_id, hobby_id, top_k=10):
    """
    협업 필터링 기반 점수 계산
    유사한 평가를 한 사용자들의 선호도를 기반으로 점수 계산
    """
    try:
        # 현재 사용자가 평가한 취미들
        user_ratings = UserHobbyRating.query.filter_by(user_id=user_id).all()

        if not user_ratings:
            return 0.0

        user_rated_hobbies = {r.hobby_id: r.rating for r in user_ratings}

        # 이미 평가한 취미는 제외
        if hobby_id in user_rated_hobbies:
            return 0.0

        # 유사한 사용자 찾기 (같은 취미를 평가한 사용자들)
        similar_users = db.session.query(
            UserHobbyRating.user_id,
            func.avg(UserHobbyRating.rating).label('avg_rating')
        ).filter(
            UserHobbyRating.hobby_id.in_(user_rated_hobbies.keys()),
            UserHobbyRating.user_id != user_id
        ).group_by(
            UserHobbyRating.user_id
        ).limit(top_k).all()

        if not similar_users:
            return 0.0

        # 유사 사용자들이 해당 취미에 준 평점 평균
        similar_user_ids = [u.user_id for u in similar_users]
        hobby_ratings = db.session.query(
            func.avg(UserHobbyRating.rating).label('avg_rating')
        ).filter(
            UserHobbyRating.hobby_id == hobby_id,
            UserHobbyRating.user_id.in_(similar_user_ids)
        ).first()

        if hobby_ratings and hobby_ratings.avg_rating:
            # 1~5점을 0~1로 정규화
            normalized_score = (float(hobby_ratings.avg_rating) - 1) / 4.0
            return normalized_score

        return 0.0

    except Exception as e:
        logger.error(f"협업 필터링 점수 계산 오류: {str(e)}")
        return 0.0


@recommendations_bp.route('', methods=['GET'])
@jwt_required()
def get_personalized_recommendations():
    """
    사용자 맞춤 취미 추천
    GET /api/recommendations?limit=10&exclude_rated=true
    """
    try:
        current_user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        exclude_rated = request.args.get('exclude_rated', 'true').lower() == 'true'

        # 최대 50개로 제한
        limit = min(limit, 50)

        # 사용자 및 프로필 조회
        user = User.query.filter_by(user_id=current_user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 프로필이 없으면 설문 응답 필요
        if not user.profile:
            return jsonify({
                'error': 'Profile Not Found',
                'message': '프로필이 없습니다. 먼저 설문에 응답해주세요.',
                'action_required': '설문 응답',
                'survey_endpoint': '/api/survey/questions'
            }), 400

        # 사용자가 이미 평가한 취미 목록
        rated_hobby_ids = []
        if exclude_rated:
            rated_hobbies = UserHobbyRating.query.filter_by(user_id=current_user_id).all()
            rated_hobby_ids = [r.hobby_id for r in rated_hobbies]

        # 활성 취미 조회
        query = Hobby.query.filter_by(is_deleted=False)
        if rated_hobby_ids:
            query = query.filter(~Hobby.hobby_id.in_(rated_hobby_ids))

        hobbies = query.all()

        if not hobbies:
            return jsonify({
                'status': 'success',
                'message': '추천할 취미가 없습니다.',
                'data': {
                    'recommendations': [],
                    'total': 0
                }
            }), 200

        # 각 취미에 대해 점수 계산
        recommendations = []
        for hobby in hobbies:
            # 1. 프로필 기반 점수 (가중치 70%)
            profile_score = calculate_hobby_score(hobby, user.profile)

            # 2. 협업 필터링 점수 (가중치 20%)
            cf_score = get_collaborative_filtering_score(current_user_id, hobby.hobby_id)

            # 3. 인기도 점수 (가중치 10%)
            avg_rating = hobby.get_average_rating()
            rating_count = hobby.get_rating_count()
            # 베이지안 평균 사용 (평가 수가 적으면 페널티)
            popularity_score = 0
            if rating_count > 0:
                m = 5  # 최소 평가 수
                C = 3.0  # 전체 평균 평점 (가정)
                popularity_score = (rating_count / (rating_count + m) * avg_rating +
                                   m / (rating_count + m) * C) / 5.0

            # 최종 점수 계산
            final_score = (profile_score * 0.7 +
                          cf_score * 0.2 +
                          popularity_score * 0.1)

            recommendations.append({
                'hobby': hobby.to_dict(include_stats=True),
                'recommendation_score': round(final_score, 4),
                'match_percentage': round(final_score * 100, 1),
                'score_breakdown': {
                    'profile_match': round(profile_score, 4),
                    'collaborative_filtering': round(cf_score, 4),
                    'popularity': round(popularity_score, 4)
                }
            })

        # 점수 순으로 정렬
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)

        # 상위 N개만 반환
        top_recommendations = recommendations[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': top_recommendations,
                'total': len(top_recommendations),
                'user_profile': user.profile.to_dict()
            }
        }), 200

    except Exception as e:
        logger.error(f"맞춤 추천 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '추천 조회 중 오류가 발생했습니다.'
        }), 500


@recommendations_bp.route('/popular', methods=['GET'])
def get_popular_hobbies():
    """
    인기 취미 조회 (평점 및 평가 수 기반)
    GET /api/recommendations/popular?limit=10&period=all
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        period = request.args.get('period', 'all')  # all, week, month

        limit = min(limit, 50)

        # 기본 쿼리
        query = db.session.query(
            Hobby,
            func.avg(UserHobbyRating.rating).label('avg_rating'),
            func.count(UserHobbyRating.rating_id).label('rating_count')
        ).outerjoin(
            UserHobbyRating, Hobby.hobby_id == UserHobbyRating.hobby_id
        ).filter(
            Hobby.is_deleted == False
        ).group_by(
            Hobby.hobby_id
        )

        # 기간 필터 (추후 구현)
        # if period == 'week':
        #     # 최근 7일
        # elif period == 'month':
        #     # 최근 30일

        results = query.all()

        # 베이지안 평균으로 정렬
        popular_hobbies = []
        m = 5  # 최소 평가 수
        C = 3.0  # 전체 평균 평점

        for hobby, avg_rating, rating_count in results:
            if avg_rating is None:
                avg_rating = 0
                rating_count = 0

            # 베이지안 평균 계산
            if rating_count > 0:
                bayesian_avg = (rating_count / (rating_count + m) * float(avg_rating) +
                               m / (rating_count + m) * C)
            else:
                bayesian_avg = C

            popular_hobbies.append({
                'hobby': hobby.to_dict(include_stats=True),
                'avg_rating': round(float(avg_rating), 2) if avg_rating else 0,
                'rating_count': rating_count,
                'popularity_score': round(bayesian_avg, 2)
            })

        # 인기도 순으로 정렬
        popular_hobbies.sort(key=lambda x: x['popularity_score'], reverse=True)

        # 상위 N개
        top_popular = popular_hobbies[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'popular_hobbies': top_popular,
                'total': len(top_popular),
                'period': period
            }
        }), 200

    except Exception as e:
        logger.error(f"인기 취미 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '인기 취미 조회 중 오류가 발생했습니다.'
        }), 500


@recommendations_bp.route('/similar/<int:hobby_id>', methods=['GET'])
def get_similar_hobbies(hobby_id):
    """
    유사한 취미 추천
    GET /api/recommendations/similar/<hobby_id>?limit=5
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        limit = min(limit, 20)

        # 기준 취미 조회
        base_hobby = Hobby.query.filter_by(hobby_id=hobby_id, is_deleted=False).first()
        if not base_hobby:
            return jsonify({
                'error': 'Hobby Not Found',
                'message': '취미를 찾을 수 없습니다.'
            }), 404

        # 다른 취미들 조회
        other_hobbies = Hobby.query.filter(
            Hobby.hobby_id != hobby_id,
            Hobby.is_deleted == False
        ).all()

        if not other_hobbies:
            return jsonify({
                'status': 'success',
                'data': {
                    'base_hobby': base_hobby.to_dict(include_stats=True),
                    'similar_hobbies': [],
                    'total': 0
                }
            }), 200

        # 유사도 계산
        similar_hobbies = []
        for hobby in other_hobbies:
            similarity_score = calculate_hobby_similarity(base_hobby, hobby)

            similar_hobbies.append({
                'hobby': hobby.to_dict(include_stats=True),
                'similarity_score': round(similarity_score, 4),
                'similarity_percentage': round(similarity_score * 100, 1)
            })

        # 유사도 순으로 정렬
        similar_hobbies.sort(key=lambda x: x['similarity_score'], reverse=True)

        # 상위 N개
        top_similar = similar_hobbies[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'base_hobby': base_hobby.to_dict(include_stats=True),
                'similar_hobbies': top_similar,
                'total': len(top_similar)
            }
        }), 200

    except Exception as e:
        logger.error(f"유사 취미 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '유사 취미 조회 중 오류가 발생했습니다.'
        }), 500


def calculate_hobby_similarity(hobby1, hobby2):
    """
    두 취미 간의 유사도 계산
    범위: 0.0 ~ 1.0
    """
    similarity = 0.0
    weights = 0.0

    # 1. 카테고리 일치 (가중치 0.3)
    if hobby1.category == hobby2.category:
        similarity += 0.3
    weights += 0.3

    # 2. 실내/외 일치 (가중치 0.15)
    if hobby1.indoor_outdoor == hobby2.indoor_outdoor:
        similarity += 0.15
    elif 'both' in [hobby1.indoor_outdoor, hobby2.indoor_outdoor]:
        similarity += 0.1
    weights += 0.15

    # 3. 사회성/개인 일치 (가중치 0.15)
    if hobby1.social_individual == hobby2.social_individual:
        similarity += 0.15
    elif 'both' in [hobby1.social_individual, hobby2.social_individual]:
        similarity += 0.1
    weights += 0.15

    # 4. 예산 유사도 (가중치 0.1)
    budget_map = {'low': 1, 'medium': 2, 'high': 3}
    budget_diff = abs(budget_map.get(hobby1.required_budget, 2) -
                     budget_map.get(hobby2.required_budget, 2))
    budget_similarity = (2 - budget_diff) / 2  # 0~1
    similarity += budget_similarity * 0.1
    weights += 0.1

    # 5. 난이도 유사도 (가중치 0.1)
    difficulty_diff = abs(hobby1.difficulty_level - hobby2.difficulty_level)
    difficulty_similarity = (4 - difficulty_diff) / 4  # 0~1
    similarity += difficulty_similarity * 0.1
    weights += 0.1

    # 6. 신체 강도 유사도 (가중치 0.1)
    physical_diff = abs(hobby1.physical_intensity - hobby2.physical_intensity)
    physical_similarity = (4 - physical_diff) / 4
    similarity += physical_similarity * 0.1
    weights += 0.1

    # 7. 창의성 유사도 (가중치 0.1)
    creativity_diff = abs(hobby1.creativity_level - hobby2.creativity_level)
    creativity_similarity = (4 - creativity_diff) / 4
    similarity += creativity_similarity * 0.1
    weights += 0.1

    if weights > 0:
        return similarity / weights
    return 0.0


@recommendations_bp.route('/category/<category>', methods=['GET'])
def get_recommendations_by_category(category):
    """
    카테고리별 추천 취미
    GET /api/recommendations/category/<category>?limit=10
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)

        # 해당 카테고리의 취미들 조회 (평점 높은 순)
        hobbies = db.session.query(
            Hobby,
            func.avg(UserHobbyRating.rating).label('avg_rating'),
            func.count(UserHobbyRating.rating_id).label('rating_count')
        ).outerjoin(
            UserHobbyRating, Hobby.hobby_id == UserHobbyRating.hobby_id
        ).filter(
            Hobby.category == category,
            Hobby.is_deleted == False
        ).group_by(
            Hobby.hobby_id
        ).all()

        if not hobbies:
            return jsonify({
                'error': 'No Hobbies Found',
                'message': f'{category} 카테고리에 취미가 없습니다.'
            }), 404

        # 베이지안 평균으로 정렬
        recommendations = []
        m = 5
        C = 3.0

        for hobby, avg_rating, rating_count in hobbies:
            if avg_rating is None:
                avg_rating = 0
                rating_count = 0

            if rating_count > 0:
                bayesian_avg = (rating_count / (rating_count + m) * float(avg_rating) +
                               m / (rating_count + m) * C)
            else:
                bayesian_avg = C

            recommendations.append({
                'hobby': hobby.to_dict(include_stats=True),
                'avg_rating': round(float(avg_rating), 2) if avg_rating else 0,
                'rating_count': rating_count,
                'score': round(bayesian_avg, 2)
            })

        recommendations.sort(key=lambda x: x['score'], reverse=True)
        top_recommendations = recommendations[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'category': category,
                'recommendations': top_recommendations,
                'total': len(top_recommendations)
            }
        }), 200

    except Exception as e:
        logger.error(f"카테고리별 추천 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '카테고리별 추천 조회 중 오류가 발생했습니다.'
        }), 500
