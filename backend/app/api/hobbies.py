"""
취미 관련 API 엔드포인트
취미 목록 조회, 상세 조회, 평가 등
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.hobby import Hobby, UserHobbyRating
from app.models.user import User
import logging
from sqlalchemy import or_, and_, func

logger = logging.getLogger(__name__)

hobbies_bp = Blueprint('hobbies', __name__, url_prefix='/api/hobbies')


@hobbies_bp.route('', methods=['GET'])
def get_hobbies():
    """
    취미 목록 조회 (필터링, 검색 지원)
    GET /api/hobbies?category=...&search=...&indoor_outdoor=...&social_individual=...&budget=...&difficulty_min=...&difficulty_max=...&page=1&per_page=20
    """
    try:
        # 쿼리 파라미터
        category = request.args.get('category')
        search = request.args.get('search')
        indoor_outdoor = request.args.get('indoor_outdoor')
        social_individual = request.args.get('social_individual')
        budget = request.args.get('budget')
        difficulty_min = request.args.get('difficulty_min', type=int)
        difficulty_max = request.args.get('difficulty_max', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 기본 쿼리 (삭제되지 않은 취미만)
        query = Hobby.query.filter_by(is_deleted=False)

        # 카테고리 필터
        if category:
            query = query.filter(Hobby.category == category)

        # 검색 (이름 또는 설명에서 검색)
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Hobby.name.ilike(search_pattern),
                    Hobby.description.ilike(search_pattern)
                )
            )

        # 실내/외 필터
        if indoor_outdoor:
            query = query.filter(
                or_(
                    Hobby.indoor_outdoor == indoor_outdoor,
                    Hobby.indoor_outdoor == 'both'
                )
            )

        # 사회성/개인 필터
        if social_individual:
            query = query.filter(
                or_(
                    Hobby.social_individual == social_individual,
                    Hobby.social_individual == 'both'
                )
            )

        # 예산 필터
        if budget:
            query = query.filter(Hobby.required_budget == budget)

        # 난이도 필터
        if difficulty_min is not None:
            query = query.filter(Hobby.difficulty_level >= difficulty_min)
        if difficulty_max is not None:
            query = query.filter(Hobby.difficulty_level <= difficulty_max)

        # 페이지네이션
        per_page = min(per_page, 100)  # 최대 100개
        pagination = query.order_by(Hobby.hobby_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # 결과 구성
        hobbies = [hobby.to_dict(include_stats=True) for hobby in pagination.items]

        return jsonify({
            'status': 'success',
            'data': {
                'hobbies': hobbies,
                'pagination': {
                    'current_page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting hobbies: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '취미 목록 조회 중 오류가 발생했습니다.'
        }), 500


@hobbies_bp.route('/<int:hobby_id>', methods=['GET'])
def get_hobby_detail(hobby_id):
    """
    취미 상세 조회
    GET /api/hobbies/<hobby_id>
    """
    try:
        hobby = Hobby.query.filter_by(hobby_id=hobby_id, is_deleted=False).first()

        if not hobby:
            return jsonify({
                'error': 'Hobby Not Found',
                'message': '취미를 찾을 수 없습니다.'
            }), 404

        # 상세 정보 구성
        hobby_data = hobby.to_dict(include_stats=True)

        # 최근 리뷰 5개 추가 (옵션)
        recent_reviews = UserHobbyRating.query.filter_by(
            hobby_id=hobby_id
        ).filter(
            UserHobbyRating.review_text.isnot(None),
            UserHobbyRating.review_text != ''
        ).order_by(
            UserHobbyRating.created_at.desc()
        ).limit(5).all()

        hobby_data['recent_reviews'] = [
            {
                'rating': review.rating,
                'review_text': review.review_text,
                'experienced': review.experienced,
                'created_at': review.created_at.isoformat() if review.created_at else None
            }
            for review in recent_reviews
        ]

        return jsonify({
            'status': 'success',
            'data': hobby_data
        }), 200

    except Exception as e:
        logger.error(f"Error getting hobby detail: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '취미 상세 조회 중 오류가 발생했습니다.'
        }), 500


@hobbies_bp.route('/<int:hobby_id>/rate', methods=['POST'])
@jwt_required()
def rate_hobby(hobby_id):
    """
    취미 평가 (평점 등록/수정)
    POST /api/hobbies/<hobby_id>/rate
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 입력 검증
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '평가 데이터가 필요합니다.'
            }), 400

        rating = data.get('rating')
        review_text = data.get('review_text')
        experienced = data.get('experienced', False)

        # rating 필수 검증
        if rating is None:
            return jsonify({
                'error': 'Bad Request',
                'message': 'rating 값이 필요합니다.'
            }), 400

        # rating 범위 검증 (1-5)
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'rating은 1과 5 사이의 값이어야 합니다.'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Bad Request',
                'message': 'rating은 정수여야 합니다.'
            }), 400

        # 취미 존재 확인
        hobby = Hobby.query.filter_by(hobby_id=hobby_id, is_deleted=False).first()
        if not hobby:
            return jsonify({
                'error': 'Hobby Not Found',
                'message': '취미를 찾을 수 없습니다.'
            }), 404

        # 사용자 확인
        user = User.query.filter_by(user_id=current_user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 기존 평가가 있는지 확인
        existing_rating = UserHobbyRating.query.filter_by(
            user_id=current_user_id,
            hobby_id=hobby_id
        ).first()

        if existing_rating:
            # 기존 평가 업데이트
            existing_rating.rating = rating
            existing_rating.review_text = review_text
            existing_rating.experienced = experienced
            message = '평가가 성공적으로 수정되었습니다.'
        else:
            # 새 평가 생성
            new_rating = UserHobbyRating(
                user_id=current_user_id,
                hobby_id=hobby_id,
                rating=rating,
                review_text=review_text,
                experienced=experienced
            )
            db.session.add(new_rating)
            message = '평가가 성공적으로 등록되었습니다.'

        db.session.commit()

        # 업데이트된 평점 정보
        hobby_data = hobby.to_dict(include_stats=True)

        logger.info(f"User {current_user_id} rated hobby {hobby_id} with {rating} stars")

        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'hobby_id': hobby_id,
                'hobby_name': hobby.name,
                'rating': rating,
                'review_text': review_text,
                'experienced': experienced,
                'updated_stats': {
                    'average_rating': hobby_data['average_rating'],
                    'rating_count': hobby_data['rating_count']
                }
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rating hobby: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '취미 평가 중 오류가 발생했습니다.'
        }), 500


@hobbies_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    사용 가능한 카테고리 목록 조회
    GET /api/hobbies/categories
    """
    try:
        # 활성 취미들의 카테고리 목록
        categories = db.session.query(
            Hobby.category,
            func.count(Hobby.hobby_id).label('count')
        ).filter_by(
            is_deleted=False
        ).group_by(
            Hobby.category
        ).order_by(
            Hobby.category
        ).all()

        category_list = [
            {
                'category': category,
                'count': count
            }
            for category, count in categories
        ]

        return jsonify({
            'status': 'success',
            'data': {
                'categories': category_list,
                'total_categories': len(category_list)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '카테고리 목록 조회 중 오류가 발생했습니다.'
        }), 500


@hobbies_bp.route('/<int:hobby_id>/ratings', methods=['GET'])
def get_hobby_ratings(hobby_id):
    """
    특정 취미의 모든 평가 조회
    GET /api/hobbies/<hobby_id>/ratings?page=1&per_page=20
    """
    try:
        # 취미 존재 확인
        hobby = Hobby.query.filter_by(hobby_id=hobby_id, is_deleted=False).first()
        if not hobby:
            return jsonify({
                'error': 'Hobby Not Found',
                'message': '취미를 찾을 수 없습니다.'
            }), 404

        # 페이지네이션 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # 최대 100개

        # 평가 조회 (최신순)
        pagination = UserHobbyRating.query.filter_by(
            hobby_id=hobby_id
        ).order_by(
            UserHobbyRating.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # 결과 구성
        ratings = [
            {
                'rating_id': rating.rating_id,
                'rating': rating.rating,
                'review_text': rating.review_text,
                'experienced': rating.experienced,
                'created_at': rating.created_at.isoformat() if rating.created_at else None
            }
            for rating in pagination.items
        ]

        return jsonify({
            'status': 'success',
            'data': {
                'hobby_id': hobby_id,
                'hobby_name': hobby.name,
                'ratings': ratings,
                'pagination': {
                    'current_page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'statistics': {
                    'average_rating': hobby.get_average_rating(),
                    'total_ratings': hobby.get_rating_count()
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting hobby ratings: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '평가 목록 조회 중 오류가 발생했습니다.'
        }), 500
