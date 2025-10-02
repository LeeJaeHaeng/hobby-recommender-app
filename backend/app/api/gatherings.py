"""
모임/동아리 관련 API 엔드포인트
모임 목록 조회, 생성, 수정, 삭제 등
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.hobby import Hobby, Gathering
from app.models.user import User
import logging
from sqlalchemy import and_, or_, desc

logger = logging.getLogger(__name__)

gatherings_bp = Blueprint('gatherings', __name__, url_prefix='/api/gatherings')


@gatherings_bp.route('', methods=['GET'])
def get_gatherings():
    """
    모임 목록 조회 (필터링 지원)
    GET /api/gatherings?hobby_id=1&region=서울&meeting_type=offline&page=1&per_page=20
    """
    try:
        # 쿼리 파라미터
        hobby_id = request.args.get('hobby_id', type=int)
        region = request.args.get('region')
        meeting_type = request.args.get('meeting_type')
        search = request.args.get('search')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 페이지네이션 제한
        per_page = min(per_page, 100)

        # 기본 쿼리
        query = Gathering.query

        # 활성 모임만 조회 (기본)
        if is_active:
            query = query.filter(Gathering.is_active == True)

        # 취미 ID 필터
        if hobby_id:
            query = query.filter(Gathering.hobby_id == hobby_id)

        # 지역 필터
        if region:
            query = query.filter(Gathering.region.ilike(f'%{region}%'))

        # 모임 유형 필터
        if meeting_type:
            query = query.filter(Gathering.meeting_type == meeting_type)

        # 검색 (모임명, 설명)
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Gathering.name.ilike(search_pattern),
                    Gathering.description.ilike(search_pattern)
                )
            )

        # 페이지네이션
        pagination = query.order_by(desc(Gathering.created_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # 결과 구성 (취미 정보 포함)
        gatherings = []
        for gathering in pagination.items:
            gathering_dict = gathering.to_dict()

            # 관련 취미 정보 추가
            hobby = Hobby.query.filter_by(
                hobby_id=gathering.hobby_id,
                is_deleted=False
            ).first()

            if hobby:
                gathering_dict['hobby'] = {
                    'hobby_id': hobby.hobby_id,
                    'name': hobby.name,
                    'category': hobby.category
                }
            else:
                gathering_dict['hobby'] = None

            gatherings.append(gathering_dict)

        return jsonify({
            'status': 'success',
            'data': {
                'gatherings': gatherings,
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
        logger.error(f"모임 목록 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '모임 목록 조회 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('/<int:gathering_id>', methods=['GET'])
def get_gathering_detail(gathering_id):
    """
    모임 상세 조회
    GET /api/gatherings/<gathering_id>
    """
    try:
        gathering = Gathering.query.filter_by(gathering_id=gathering_id).first()

        if not gathering:
            return jsonify({
                'error': 'Gathering Not Found',
                'message': '모임을 찾을 수 없습니다.'
            }), 404

        # 상세 정보 구성
        gathering_dict = gathering.to_dict()

        # 관련 취미 상세 정보 추가
        hobby = Hobby.query.filter_by(
            hobby_id=gathering.hobby_id,
            is_deleted=False
        ).first()

        if hobby:
            gathering_dict['hobby'] = hobby.to_dict(include_stats=True)
        else:
            gathering_dict['hobby'] = None

        return jsonify({
            'status': 'success',
            'data': gathering_dict
        }), 200

    except Exception as e:
        logger.error(f"모임 상세 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '모임 상세 조회 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('', methods=['POST'])
@jwt_required()
def create_gathering():
    """
    모임 생성
    POST /api/gatherings
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 입력 검증
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '모임 정보가 필요합니다.'
            }), 400

        # 필수 필드 검증
        required_fields = ['hobby_id', 'name', 'region']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({
                'error': 'Bad Request',
                'message': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'
            }), 400

        # 취미 존재 확인
        hobby = Hobby.query.filter_by(
            hobby_id=data['hobby_id'],
            is_deleted=False
        ).first()

        if not hobby:
            return jsonify({
                'error': 'Hobby Not Found',
                'message': '존재하지 않는 취미입니다.'
            }), 404

        # 사용자 확인
        user = User.query.filter_by(user_id=current_user_id, is_deleted=False).first()
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': '사용자를 찾을 수 없습니다.'
            }), 404

        # 모임 유형 검증
        meeting_type = data.get('meeting_type', 'offline')
        if meeting_type not in ['online', 'offline', 'hybrid']:
            return jsonify({
                'error': 'Bad Request',
                'message': 'meeting_type은 online, offline, hybrid 중 하나여야 합니다.'
            }), 400

        # 모임 생성
        new_gathering = Gathering(
            hobby_id=data['hobby_id'],
            name=data['name'],
            description=data.get('description'),
            location=data.get('location'),
            region=data['region'],
            meeting_type=meeting_type,
            schedule_info=data.get('schedule_info'),
            member_count=data.get('member_count', 0),
            contact_info=data.get('contact_info'),
            website_url=data.get('website_url'),
            is_active=data.get('is_active', True)
        )

        db.session.add(new_gathering)
        db.session.commit()

        logger.info(f"사용자 {current_user_id}가 모임 '{new_gathering.name}' 생성 (ID: {new_gathering.gathering_id})")

        # 생성된 모임 정보 반환
        gathering_dict = new_gathering.to_dict()
        gathering_dict['hobby'] = {
            'hobby_id': hobby.hobby_id,
            'name': hobby.name,
            'category': hobby.category
        }

        return jsonify({
            'status': 'success',
            'message': '모임이 성공적으로 생성되었습니다.',
            'data': gathering_dict
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"모임 생성 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '모임 생성 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('/<int:gathering_id>', methods=['PUT'])
@jwt_required()
def update_gathering(gathering_id):
    """
    모임 정보 수정
    PUT /api/gatherings/<gathering_id>
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': '수정할 정보가 필요합니다.'
            }), 400

        # 모임 조회
        gathering = Gathering.query.filter_by(gathering_id=gathering_id).first()

        if not gathering:
            return jsonify({
                'error': 'Gathering Not Found',
                'message': '모임을 찾을 수 없습니다.'
            }), 404

        # 수정 가능한 필드들
        updatable_fields = [
            'name', 'description', 'location', 'region',
            'meeting_type', 'schedule_info', 'member_count',
            'contact_info', 'website_url', 'is_active'
        ]

        # meeting_type 검증
        if 'meeting_type' in data:
            if data['meeting_type'] not in ['online', 'offline', 'hybrid']:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'meeting_type은 online, offline, hybrid 중 하나여야 합니다.'
                }), 400

        # 필드 업데이트
        updated_fields = []
        for field in updatable_fields:
            if field in data:
                setattr(gathering, field, data[field])
                updated_fields.append(field)

        if not updated_fields:
            return jsonify({
                'error': 'Bad Request',
                'message': '수정할 필드가 없습니다.'
            }), 400

        db.session.commit()

        logger.info(f"사용자 {current_user_id}가 모임 {gathering_id} 수정: {updated_fields}")

        # 업데이트된 모임 정보 반환
        gathering_dict = gathering.to_dict()
        hobby = Hobby.query.filter_by(hobby_id=gathering.hobby_id, is_deleted=False).first()
        if hobby:
            gathering_dict['hobby'] = {
                'hobby_id': hobby.hobby_id,
                'name': hobby.name,
                'category': hobby.category
            }

        return jsonify({
            'status': 'success',
            'message': '모임 정보가 성공적으로 수정되었습니다.',
            'data': {
                'gathering': gathering_dict,
                'updated_fields': updated_fields
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"모임 수정 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '모임 수정 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('/<int:gathering_id>', methods=['DELETE'])
@jwt_required()
def delete_gathering(gathering_id):
    """
    모임 삭제 (비활성화)
    DELETE /api/gatherings/<gathering_id>
    """
    try:
        current_user_id = get_jwt_identity()

        # 모임 조회
        gathering = Gathering.query.filter_by(gathering_id=gathering_id).first()

        if not gathering:
            return jsonify({
                'error': 'Gathering Not Found',
                'message': '모임을 찾을 수 없습니다.'
            }), 404

        # 실제 삭제 대신 비활성화
        gathering.is_active = False
        db.session.commit()

        logger.info(f"사용자 {current_user_id}가 모임 {gathering_id} 삭제 (비활성화)")

        return jsonify({
            'status': 'success',
            'message': '모임이 성공적으로 삭제되었습니다.'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"모임 삭제 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '모임 삭제 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('/regions', methods=['GET'])
def get_regions():
    """
    사용 가능한 지역 목록 조회
    GET /api/gatherings/regions
    """
    try:
        # 활성 모임들의 지역 목록
        from sqlalchemy import func

        regions = db.session.query(
            Gathering.region,
            func.count(Gathering.gathering_id).label('count')
        ).filter(
            Gathering.is_active == True
        ).group_by(
            Gathering.region
        ).order_by(
            desc(func.count(Gathering.gathering_id))
        ).all()

        region_list = [
            {
                'region': region,
                'count': count
            }
            for region, count in regions
        ]

        return jsonify({
            'status': 'success',
            'data': {
                'regions': region_list,
                'total_regions': len(region_list)
            }
        }), 200

    except Exception as e:
        logger.error(f"지역 목록 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '지역 목록 조회 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('/hobby/<int:hobby_id>', methods=['GET'])
def get_gatherings_by_hobby(hobby_id):
    """
    특정 취미의 모임 목록 조회
    GET /api/gatherings/hobby/<hobby_id>?region=서울&page=1
    """
    try:
        # 취미 존재 확인
        hobby = Hobby.query.filter_by(hobby_id=hobby_id, is_deleted=False).first()
        if not hobby:
            return jsonify({
                'error': 'Hobby Not Found',
                'message': '취미를 찾을 수 없습니다.'
            }), 404

        # 쿼리 파라미터
        region = request.args.get('region')
        meeting_type = request.args.get('meeting_type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)

        # 쿼리 구성
        query = Gathering.query.filter_by(
            hobby_id=hobby_id,
            is_active=True
        )

        if region:
            query = query.filter(Gathering.region.ilike(f'%{region}%'))

        if meeting_type:
            query = query.filter(Gathering.meeting_type == meeting_type)

        # 페이지네이션
        pagination = query.order_by(desc(Gathering.member_count)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # 결과 구성
        gatherings = [gathering.to_dict() for gathering in pagination.items]

        return jsonify({
            'status': 'success',
            'data': {
                'hobby': hobby.to_dict(include_stats=True),
                'gatherings': gatherings,
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
        logger.error(f"취미별 모임 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '취미별 모임 조회 중 오류가 발생했습니다.'
        }), 500


@gatherings_bp.route('/popular', methods=['GET'])
def get_popular_gatherings():
    """
    인기 모임 조회 (회원 수 기준)
    GET /api/gatherings/popular?limit=10
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)

        # 회원 수가 많은 순으로 조회
        gatherings = Gathering.query.filter_by(
            is_active=True
        ).order_by(
            desc(Gathering.member_count)
        ).limit(limit).all()

        # 결과 구성 (취미 정보 포함)
        popular_gatherings = []
        for gathering in gatherings:
            gathering_dict = gathering.to_dict()

            # 관련 취미 정보
            hobby = Hobby.query.filter_by(
                hobby_id=gathering.hobby_id,
                is_deleted=False
            ).first()

            if hobby:
                gathering_dict['hobby'] = {
                    'hobby_id': hobby.hobby_id,
                    'name': hobby.name,
                    'category': hobby.category
                }

            popular_gatherings.append(gathering_dict)

        return jsonify({
            'status': 'success',
            'data': {
                'gatherings': popular_gatherings,
                'total': len(popular_gatherings)
            }
        }), 200

    except Exception as e:
        logger.error(f"인기 모임 조회 오류: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Server Error',
            'message': '인기 모임 조회 중 오류가 발생했습니다.'
        }), 500
