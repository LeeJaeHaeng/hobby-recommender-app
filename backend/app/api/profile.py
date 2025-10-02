"""
사용자 프로필 관리 API 엔드포인트
프로필 조회, 수정, 비밀번호 변경 등
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User, UserProfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

profile_bp = Blueprint('profile', __name__, url_prefix='/api/users')


def validate_age(age):
    """나이 검증"""
    if age is not None:
        if not isinstance(age, int) or age < 13 or age > 120:
            return False, "나이는 13세 이상 120세 이하여야 합니다."
    return True, ""


def validate_password(password):
    """비밀번호 강도 검증"""
    if not password or len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."

    if len(password) > 128:
        return False, "비밀번호는 128자를 초과할 수 없습니다."

    import re
    # 대소문자, 숫자, 특수문자 포함 확인
    if not re.search(r'[a-z]', password):
        return False, "비밀번호에 소문자가 포함되어야 합니다."

    if not re.search(r'[A-Z]', password):
        return False, "비밀번호에 대문자가 포함되어야 합니다."

    if not re.search(r'\d', password):
        return False, "비밀번호에 숫자가 포함되어야 합니다."

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호에 특수문자가 포함되어야 합니다."

    return True, ""


@profile_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """
    사용자 프로필 조회
    GET /api/users/<user_id>
    """
    try:
        current_user_id = get_jwt_identity()

        # 본인의 프로필만 조회 가능 (관리자 권한은 추후 구현)
        if current_user_id != user_id:
            return jsonify({
                'error': 'Access Denied',
                'message': '본인의 프로필만 조회할 수 있습니다.'
            }), 403

        # 사용자 조회
        user = User.query.filter_by(user_id=user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 사용자 데이터 구성
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'gender': user.gender,
            'location': user.location,
            'email_verified': user.email_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }

        # 프로필 정보 추가
        if user.profile:
            user_data['profile'] = {
                'outdoor_preference': float(user.profile.outdoor_preference),
                'social_preference': float(user.profile.social_preference),
                'creative_preference': float(user.profile.creative_preference),
                'learning_preference': float(user.profile.learning_preference),
                'physical_activity': float(user.profile.physical_activity),
                'budget_level': user.profile.budget_level
            }

        return jsonify({
            'status': 'success',
            'data': {
                'user': user_data
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '사용자 프로필 조회 중 오류가 발생했습니다.'
        }), 500


@profile_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_profile(user_id):
    """
    사용자 프로필 수정
    PUT /api/users/<user_id>
    """
    try:
        current_user_id = get_jwt_identity()

        # 본인의 프로필만 수정 가능
        if current_user_id != user_id:
            return jsonify({
                'error': 'Access Denied',
                'message': '본인의 프로필만 수정할 수 있습니다.'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '요청 데이터가 없습니다.'
            }), 400

        # 사용자 조회
        user = User.query.filter_by(user_id=user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 수정 가능한 필드들
        updatable_fields = ['age', 'gender', 'location']
        validation_errors = []
        updated_fields = []

        for field in updatable_fields:
            if field in data:
                value = data[field]

                if field == 'age':
                    if value is not None:
                        try:
                            age = int(value)
                            is_valid, error_msg = validate_age(age)
                            if not is_valid:
                                validation_errors.append({'field': field, 'message': error_msg})
                            else:
                                user.age = age
                                updated_fields.append(field)
                        except (ValueError, TypeError):
                            validation_errors.append({'field': field, 'message': '나이는 숫자여야 합니다.'})
                    else:
                        user.age = None
                        updated_fields.append(field)

                elif field == 'gender':
                    if value and value not in ['male', 'female', 'other']:
                        validation_errors.append({'field': field, 'message': '성별은 male, female, other 중 하나여야 합니다.'})
                    else:
                        user.gender = value
                        updated_fields.append(field)

                elif field == 'location':
                    if value:
                        if len(value.strip()) > 100:
                            validation_errors.append({'field': field, 'message': '지역명은 100자를 초과할 수 없습니다.'})
                        else:
                            user.location = value.strip()
                            updated_fields.append(field)
                    else:
                        user.location = None
                        updated_fields.append(field)

        # 프로필 선호도 업데이트
        profile_fields = ['outdoor_preference', 'social_preference', 'creative_preference',
                         'learning_preference', 'physical_activity', 'budget_level']

        profile_updates = {}
        for field in profile_fields:
            if field in data:
                value = data[field]

                if field == 'budget_level':
                    if value not in ['low', 'medium', 'high']:
                        validation_errors.append({'field': field, 'message': '예산 수준은 low, medium, high 중 하나여야 합니다.'})
                    else:
                        profile_updates[field] = value
                else:
                    # 선호도 값 (0.0 ~ 1.0)
                    try:
                        pref_value = float(value)
                        if not (0.0 <= pref_value <= 1.0):
                            validation_errors.append({'field': field, 'message': '선호도는 0.0과 1.0 사이의 값이어야 합니다.'})
                        else:
                            profile_updates[field] = pref_value
                    except (ValueError, TypeError):
                        validation_errors.append({'field': field, 'message': '선호도는 숫자여야 합니다.'})

        # 검증 에러가 있으면 반환
        if validation_errors:
            return jsonify({
                'error': 'Validation Error',
                'message': '입력 데이터가 올바르지 않습니다.',
                'validation_errors': validation_errors
            }), 400

        # 수정할 내용이 없으면 반환
        if not updated_fields and not profile_updates:
            return jsonify({
                'error': 'Bad Request',
                'message': '수정할 데이터가 없습니다.'
            }), 400

        try:
            # 사용자 기본 정보 업데이트
            if updated_fields:
                user.updated_at = datetime.utcnow()

            # 프로필 정보 업데이트
            if profile_updates:
                if not user.profile:
                    # 프로필이 없으면 생성
                    user_profile = UserProfile(
                        user_id=user.user_id,
                        outdoor_preference=0.5,
                        social_preference=0.5,
                        creative_preference=0.5,
                        learning_preference=0.5,
                        physical_activity=0.5,
                        budget_level='medium'
                    )
                    db.session.add(user_profile)
                    db.session.flush()  # user.profile 관계 설정을 위해

                # 프로필 업데이트
                for field, value in profile_updates.items():
                    setattr(user.profile, field, value)

                updated_fields.extend(profile_updates.keys())

            db.session.commit()

            logger.info(f"User profile updated: {user.username} (ID: {user.user_id}), fields: {updated_fields}")

            # 업데이트된 사용자 데이터 반환
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'age': user.age,
                'gender': user.gender,
                'location': user.location,
                'email_verified': user.email_verified,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }

            # 프로필 정보 추가
            if user.profile:
                user_data['profile'] = {
                    'outdoor_preference': float(user.profile.outdoor_preference),
                    'social_preference': float(user.profile.social_preference),
                    'creative_preference': float(user.profile.creative_preference),
                    'learning_preference': float(user.profile.learning_preference),
                    'physical_activity': float(user.profile.physical_activity),
                    'budget_level': user.profile.budget_level
                }

            return jsonify({
                'status': 'success',
                'message': '프로필이 성공적으로 업데이트되었습니다.',
                'data': {
                    'user': user_data,
                    'updated_fields': updated_fields
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during profile update: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Database Error',
                'message': '프로필 업데이트 중 데이터베이스 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error during profile update: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '프로필 업데이트 중 예상치 못한 오류가 발생했습니다.'
        }), 500


@profile_bp.route('/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    """
    비밀번호 변경
    PUT /api/users/<user_id>/password
    """
    try:
        current_user_id = get_jwt_identity()

        # 본인의 비밀번호만 변경 가능
        if current_user_id != user_id:
            return jsonify({
                'error': 'Access Denied',
                'message': '본인의 비밀번호만 변경할 수 있습니다.'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '요청 데이터가 없습니다.'
            }), 400

        # 필수 필드 확인
        required_fields = ['current_password', 'new_password', 'confirm_password']
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        if missing_fields:
            return jsonify({
                'error': 'Validation Error',
                'message': '필수 필드가 누락되었습니다.',
                'missing_fields': missing_fields
            }), 400

        current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        # 사용자 조회
        user = User.query.filter_by(user_id=user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 현재 비밀번호 확인
        if not user.check_password(current_password):
            return jsonify({
                'error': 'Authentication Failed',
                'message': '현재 비밀번호가 올바르지 않습니다.'
            }), 401

        # 새 비밀번호 검증
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'error': 'Validation Error',
                'message': error_msg
            }), 400

        # 새 비밀번호 확인
        if new_password != confirm_password:
            return jsonify({
                'error': 'Validation Error',
                'message': '새 비밀번호가 일치하지 않습니다.'
            }), 400

        # 현재 비밀번호와 같은지 확인
        if user.check_password(new_password):
            return jsonify({
                'error': 'Validation Error',
                'message': '새 비밀번호는 현재 비밀번호와 달라야 합니다.'
            }), 400

        try:
            # 비밀번호 업데이트
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"Password changed for user: {user.username} (ID: {user.user_id})")

            return jsonify({
                'status': 'success',
                'message': '비밀번호가 성공적으로 변경되었습니다.'
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during password change: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Database Error',
                'message': '비밀번호 변경 중 데이터베이스 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error during password change: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '비밀번호 변경 중 예상치 못한 오류가 발생했습니다.'
        }), 500