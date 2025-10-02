"""
사용자 관련 API 엔드포인트
회원가입, 로그인, 프로필 관리 등
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User, UserProfile
from app.models.admin import AdminActivityLog
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """사용자명 검증"""
    if not username or len(username) < 3 or len(username) > 30:
        return False, "사용자명은 3-30자 사이여야 합니다."

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "사용자명은 영문자, 숫자, 언더스코어만 사용할 수 있습니다."

    return True, ""


def validate_password(password):
    """비밀번호 강도 검증"""
    if not password or len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."

    if len(password) > 128:
        return False, "비밀번호는 128자를 초과할 수 없습니다."

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


def validate_age(age):
    """나이 검증"""
    if age is not None:
        if not isinstance(age, int) or age < 13 or age > 120:
            return False, "나이는 13세 이상 120세 이하여야 합니다."
    return True, ""


def validate_name(name, field_name):
    """이름 검증 (firstName, lastName)"""
    if not name or len(name.strip()) == 0:
        return False, f"{field_name}은(는) 필수입니다."

    if len(name) > 50:
        return False, f"{field_name}은(는) 50자를 초과할 수 없습니다."

    # 한글, 영문자, 공백만 허용
    if not re.match(r'^[a-zA-Z가-힣\s]+$', name):
        return False, f"{field_name}은(는) 한글, 영문자, 공백만 사용할 수 있습니다."

    return True, ""


@users_bp.route('/register', methods=['POST'])
def register_user():
    """
    사용자 회원가입
    POST /api/users/register
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '요청 데이터가 없습니다.'
            }), 400

        # 필수 필드 확인
        required_fields = ['username', 'email', 'password', 'confirmPassword', 'firstName', 'lastName']
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

        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        confirm_password = data['confirmPassword']
        first_name = data['firstName'].strip()
        last_name = data['lastName'].strip()
        age = data.get('age')
        gender = data.get('gender')
        location = data.get('location', '').strip()

        # 입력 검증
        validation_errors = []

        # 사용자명 검증
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            validation_errors.append({'field': 'username', 'message': error_msg})

        # 이메일 검증
        if not validate_email(email):
            validation_errors.append({'field': 'email', 'message': '올바른 이메일 형식이 아닙니다.'})

        # 비밀번호 검증
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            validation_errors.append({'field': 'password', 'message': error_msg})

        # 비밀번호 확인
        if password != confirm_password:
            validation_errors.append({'field': 'confirmPassword', 'message': '비밀번호가 일치하지 않습니다.'})

        # 이름 검증
        is_valid, error_msg = validate_name(first_name, '이름')
        if not is_valid:
            validation_errors.append({'field': 'firstName', 'message': error_msg})

        is_valid, error_msg = validate_name(last_name, '성')
        if not is_valid:
            validation_errors.append({'field': 'lastName', 'message': error_msg})

        # 나이 검증
        if age is not None:
            try:
                age = int(age)
                is_valid, error_msg = validate_age(age)
                if not is_valid:
                    validation_errors.append({'field': 'age', 'message': error_msg})
            except (ValueError, TypeError):
                validation_errors.append({'field': 'age', 'message': '나이는 숫자여야 합니다.'})

        # 성별 검증
        if gender and gender not in ['male', 'female', 'other']:
            validation_errors.append({'field': 'gender', 'message': '성별은 male, female, other 중 하나여야 합니다.'})

        # 검증 에러가 있으면 반환
        if validation_errors:
            return jsonify({
                'error': 'Validation Error',
                'message': '입력 데이터가 올바르지 않습니다.',
                'validation_errors': validation_errors
            }), 400

        # 중복 확인
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).filter_by(is_deleted=False).first()

        if existing_user:
            if existing_user.email == email:
                return jsonify({
                    'error': 'Conflict',
                    'message': '이미 등록된 이메일입니다.'
                }), 409
            else:
                return jsonify({
                    'error': 'Conflict',
                    'message': '이미 사용 중인 사용자명입니다.'
                }), 409

        # 새 사용자 생성
        new_user = User(
            username=username,
            email=email,
            age=age,
            gender=gender,
            location=location if location else None
        )

        # 비밀번호 설정
        try:
            new_user.set_password(password)
        except ValueError as e:
            logger.error(f"Password hashing failed for user {username}: {str(e)}")
            return jsonify({
                'error': 'Server Error',
                'message': '비밀번호 처리 중 오류가 발생했습니다.'
            }), 500

        # 데이터베이스에 저장
        try:
            db.session.add(new_user)
            db.session.commit()

            # 기본 사용자 프로필 생성 (선택사항)
            user_profile = UserProfile(
                user_id=new_user.user_id,
                outdoor_preference=0.5,
                social_preference=0.5,
                creative_preference=0.5,
                learning_preference=0.5,
                physical_activity=0.5,
                budget_level='medium'
            )
            db.session.add(user_profile)
            db.session.commit()

            logger.info(f"New user registered: {username} (ID: {new_user.user_id})")

            # 응답 데이터 (비밀번호 제외)
            user_data = {
                'user_id': new_user.user_id,
                'username': new_user.username,
                'email': new_user.email,
                'age': new_user.age,
                'gender': new_user.gender,
                'location': new_user.location,
                'email_verified': new_user.email_verified,
                'created_at': new_user.created_at.isoformat() if new_user.created_at else None
            }

            return jsonify({
                'status': 'success',
                'message': '회원가입이 완료되었습니다.',
                'data': {
                    'user': user_data
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during user registration: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Database Error',
                'message': '사용자 등록 중 데이터베이스 오류가 발생했습니다.'
            }), 500

    except ValueError as e:
        logger.error(f"Validation error in user registration: {str(e)}")
        return jsonify({
            'error': 'Validation Error',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error in user registration: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'error': 'Server Error',
            'message': '예상치 못한 오류가 발생했습니다.'
        }), 500


@users_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """
    사용자명/이메일 중복 확인
    POST /api/users/check-availability
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '요청 데이터가 없습니다.'
            }), 400

        username = data.get('username')
        email = data.get('email')

        result = {}

        if username:
            username = username.strip()
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                result['username'] = {'available': False, 'message': error_msg}
            else:
                existing_user = User.query.filter_by(username=username, is_deleted=False).first()
                result['username'] = {
                    'available': existing_user is None,
                    'message': '사용 가능한 사용자명입니다.' if existing_user is None else '이미 사용 중인 사용자명입니다.'
                }

        if email:
            email = email.strip().lower()
            if not validate_email(email):
                result['email'] = {'available': False, 'message': '올바른 이메일 형식이 아닙니다.'}
            else:
                existing_user = User.query.filter_by(email=email, is_deleted=False).first()
                result['email'] = {
                    'available': existing_user is None,
                    'message': '사용 가능한 이메일입니다.' if existing_user is None else '이미 등록된 이메일입니다.'
                }

        return jsonify({
            'status': 'success',
            'data': result
        }), 200

    except Exception as e:
        logger.error(f"Error in availability check: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '중복 확인 중 오류가 발생했습니다.'
        }), 500