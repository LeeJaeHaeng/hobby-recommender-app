"""
인증 관련 API 엔드포인트
로그인, 로그아웃, 토큰 갱신 등
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models import db
from app.models.user import User
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_login_input(data):
    """로그인 입력 데이터 검증"""
    errors = []

    if not data:
        errors.append({'field': 'general', 'message': '요청 데이터가 없습니다.'})
        return errors

    # 이메일 또는 사용자명 확인
    identifier = data.get('email') or data.get('username')
    if not identifier:
        errors.append({'field': 'identifier', 'message': '이메일 또는 사용자명을 입력해주세요.'})

    # 비밀번호 확인
    password = data.get('password')
    if not password:
        errors.append({'field': 'password', 'message': '비밀번호를 입력해주세요.'})

    return errors


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    사용자 로그인
    POST /api/auth/login
    """
    try:
        data = request.get_json()

        # 입력 검증
        validation_errors = validate_login_input(data)
        if validation_errors:
            return jsonify({
                'error': 'Validation Error',
                'message': '입력 데이터가 올바르지 않습니다.',
                'validation_errors': validation_errors
            }), 400

        # 이메일 또는 사용자명으로 로그인 시도
        identifier = data.get('email') or data.get('username')
        password = data.get('password')
        remember_me = data.get('remember_me', False)

        # 사용자 조회 (이메일 또는 사용자명으로)
        user = None
        if '@' in identifier:
            # 이메일로 조회
            user = User.query.filter_by(email=identifier.lower().strip(), is_deleted=False).first()
        else:
            # 사용자명으로 조회
            user = User.query.filter_by(username=identifier.strip(), is_deleted=False).first()

        # 사용자 존재 여부 및 비밀번호 확인
        if not user or not user.check_password(password):
            # 보안을 위해 구체적인 오류 정보를 제공하지 않음
            return jsonify({
                'error': 'Authentication Failed',
                'message': '이메일/사용자명 또는 비밀번호가 올바르지 않습니다.'
            }), 401

        # 계정 잠금 확인
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            return jsonify({
                'error': 'Account Locked',
                'message': f'계정이 잠겨있습니다. {user.account_locked_until.strftime("%Y-%m-%d %H:%M")}에 다시 시도해주세요.'
            }), 423

        # 로그인 성공 - 실패 횟수 초기화
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        user.account_locked_until = None

        # JWT 토큰 생성
        # remember_me가 True면 토큰 유효기간 연장
        if remember_me:
            expires_delta = timedelta(days=30)
        else:
            expires_delta = timedelta(hours=24)

        access_token = create_access_token(
            identity=user.user_id,
            expires_delta=expires_delta,
            additional_claims={
                'username': user.username,
                'email': user.email,
                'type': 'access'
            }
        )

        refresh_token = create_refresh_token(
            identity=user.user_id,
            expires_delta=timedelta(days=30)
        )

        try:
            db.session.commit()
            logger.info(f"User logged in successfully: {user.username} (ID: {user.user_id})")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during login: {str(e)}")
            return jsonify({
                'error': 'Database Error',
                'message': '로그인 처리 중 오류가 발생했습니다.'
            }), 500

        # 응답 데이터 구성
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'gender': user.gender,
            'location': user.location,
            'email_verified': user.email_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }

        return jsonify({
            'status': 'success',
            'message': '로그인이 완료되었습니다.',
            'data': {
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(expires_delta.total_seconds())
            }
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'error': 'Server Error',
            'message': '로그인 처리 중 예상치 못한 오류가 발생했습니다.'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    액세스 토큰 갱신
    POST /api/auth/refresh
    """
    try:
        current_user_id = get_jwt_identity()

        # 사용자 존재 확인
        user = User.query.filter_by(user_id=current_user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 새 액세스 토큰 생성
        new_access_token = create_access_token(
            identity=user.user_id,
            additional_claims={
                'username': user.username,
                'email': user.email,
                'type': 'access'
            }
        )

        logger.info(f"Access token refreshed for user: {user.username} (ID: {user.user_id})")

        return jsonify({
            'status': 'success',
            'message': '토큰이 갱신되었습니다.',
            'data': {
                'access_token': new_access_token,
                'token_type': 'Bearer'
            }
        }), 200

    except Exception as e:
        logger.error(f"Error during token refresh: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '토큰 갱신 중 오류가 발생했습니다.'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    현재 로그인한 사용자 정보 조회
    GET /api/auth/me
    """
    try:
        current_user_id = get_jwt_identity()

        # 사용자 조회
        user = User.query.filter_by(user_id=current_user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 사용자 프로필 정보 포함
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'gender': user.gender,
            'location': user.location,
            'email_verified': user.email_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }

        # 프로필 정보 추가
        if user.profile:
            user_data['profile'] = {
                'outdoor_preference': user.profile.outdoor_preference,
                'social_preference': user.profile.social_preference,
                'creative_preference': user.profile.creative_preference,
                'learning_preference': user.profile.learning_preference,
                'physical_activity': user.profile.physical_activity,
                'budget_level': user.profile.budget_level
            }

        return jsonify({
            'status': 'success',
            'data': {
                'user': user_data
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '사용자 정보 조회 중 오류가 발생했습니다.'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    로그아웃 (토큰 블랙리스트 처리)
    POST /api/auth/logout
    """
    try:
        # 현재는 클라이언트 측에서 토큰을 삭제하도록 안내
        # 추후 Redis를 사용한 토큰 블랙리스트 구현 예정

        current_user_id = get_jwt_identity()
        logger.info(f"User logged out: ID {current_user_id}")

        return jsonify({
            'status': 'success',
            'message': '로그아웃이 완료되었습니다. 클라이언트에서 토큰을 삭제해주세요.'
        }), 200

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '로그아웃 처리 중 오류가 발생했습니다.'
        }), 500