"""
Flask 메인 애플리케이션
퇴직자 맞춤 취미 추천 시스템 백엔드 API
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

# 환경 변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# CORS 설정 (프론트엔드와 통신을 위해)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'mysql+mysqlconnector://hobby_user:password123@localhost:3306/hobby_recommender'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # SQL 쿼리 로깅 (개발 시 True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# JWT 설정
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# JWT 초기화
jwt = JWTManager(app)

# JSON 인코딩 설정 (한글 지원)
app.config['JSON_AS_ASCII'] = False

# 파일 업로드 설정
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 모델 임포트 및 DB 초기화
from app.models import db
from app.models.user import User, UserProfile, SurveyQuestion, SurveyResponse
from app.models.hobby import Hobby, UserHobbyRating, Gathering
from app.models.admin import AdminUser, AdminActivityLog, UserFeedback, Announcement, UserNotification

db.init_app(app)
migrate = Migrate(app, db)

# Blueprint 등록
from app.api.users import users_bp
from app.api.auth import auth_bp
from app.api.profile import profile_bp
from app.api.survey import survey_bp
from app.api.hobbies import hobbies_bp
from app.api.recommendations import recommendations_bp
from app.api.gatherings import gatherings_bp
app.register_blueprint(users_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(survey_bp)
app.register_blueprint(hobbies_bp)
app.register_blueprint(recommendations_bp)
app.register_blueprint(gatherings_bp)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# 에러 핸들러 (예외 처리)
# ============================================

@app.errorhandler(400)
def bad_request(error):
    """잘못된 요청"""
    logger.warning(f"Bad Request: {str(error)}")
    return jsonify({
        'error': 'Bad Request',
        'message': '요청 데이터가 올바르지 않습니다.',
        'details': str(error)
    }), 400


@app.errorhandler(404)
def not_found(error):
    """리소스를 찾을 수 없음"""
    logger.warning(f"Not Found: {request.path}")
    return jsonify({
        'error': 'Not Found',
        'message': '요청한 리소스를 찾을 수 없습니다.',
        'path': request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """서버 내부 오류"""
    logger.error(f"Internal Server Error: {str(error)}", exc_info=True)
    db.session.rollback()  # 트랜잭션 롤백
    return jsonify({
        'error': 'Internal Server Error',
        'message': '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """모든 예외 처리"""
    logger.error(f"Unhandled Exception: {str(error)}", exc_info=True)
    db.session.rollback()
    return jsonify({
        'error': 'Server Error',
        'message': '예상치 못한 오류가 발생했습니다.'
    }), 500


# ============================================
# 기본 라우트
# ============================================

@app.route('/')
def index():
    """API 메인 페이지"""
    return jsonify({
        'message': '퇴직자 취미 추천 시스템 API',
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'health': '/api/health',
            'users': '/api/users',
            'hobbies': '/api/hobbies',
            'survey': '/api/survey',
            'admin': '/api/admin (관리자 전용)'
        }
    })


@app.route('/api/health')
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 확인
        from sqlalchemy import text; db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = f'error: {str(e)}'
        db_healthy = False
    
    return jsonify({
        'status': 'healthy' if db_healthy else 'unhealthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'production')
    }), 200 if db_healthy else 503


@app.route('/api/test')
def test():
    """테스트 엔드포인트"""
    try:
        # 간단한 데이터베이스 쿼리 테스트
        user_count = User.query.filter_by(is_deleted=False).count()
        hobby_count = Hobby.query.filter_by(is_deleted=False).count()
        
        return jsonify({
            'message': 'API 테스트 성공',
            'timestamp': datetime.utcnow().isoformat(),
            'database_stats': {
                'users': user_count,
                'hobbies': hobby_count
            }
        })
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return jsonify({
            'error': 'Test failed',
            'message': str(e)
        }), 500


# ============================================
# 데이터베이스 초기화 (개발 환경용)
# ============================================

@app.cli.command()
def init_db():
    """데이터베이스 테이블 생성"""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        print("✅ 데이터베이스 테이블이 생성되었습니다.")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        print(f"❌ 데이터베이스 초기화 실패: {str(e)}")


@app.cli.command()
def seed_admin():
    """기본 관리자 계정 생성"""
    try:
        # 기존 관리자 확인
        existing_admin = AdminUser.query.filter_by(username='admin').first()
        if existing_admin:
            print("⚠️ 관리자 계정이 이미 존재합니다.")
            return
        
        # 새 관리자 생성
        admin = AdminUser(
            username='admin',
            email='admin@hobby-recommender.com',
            role='super_admin',
            is_active=True
        )
        admin.set_password('admin123!')  # 반드시 변경 필요!
        
        db.session.add(admin)
        db.session.commit()
        
        logger.info("Admin user created successfully")
        print("✅ 관리자 계정이 생성되었습니다.")
        print("   Username: admin")
        print("   Password: admin123!")
        print("   ⚠️ 보안을 위해 반드시 비밀번호를 변경하세요!")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Admin creation failed: {str(e)}")
        print(f"❌ 관리자 생성 실패: {str(e)}")


# ============================================
# Before/After Request 핸들러
# ============================================

@app.before_request
def before_request():
    """요청 전 로깅"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")


@app.after_request
def after_request(response):
    """응답 후 로깅"""
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response


# ============================================
# 애플리케이션 컨텍스트 설정
# ============================================

@app.shell_context_processor
def make_shell_context():
    """Flask Shell용 컨텍스트"""
    return {
        'db': db,
        'User': User,
        'UserProfile': UserProfile,
        'SurveyQuestion': SurveyQuestion,
        'SurveyResponse': SurveyResponse,
        'Hobby': Hobby,
        'UserHobbyRating': UserHobbyRating,
        'Gathering': Gathering,
        'AdminUser': AdminUser,
        'AdminActivityLog': AdminActivityLog,
        'UserFeedback': UserFeedback,
        'Announcement': Announcement,
        'UserNotification': UserNotification
    }


# ============================================
# 메인 실행
# ============================================

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Flask 서버를 시작합니다...")
    logger.info(f"환경: {os.getenv('FLASK_ENV', 'production')}")
    logger.info(f"서버 주소: http://localhost:5000")
    logger.info("=" * 50)
    
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host='0.0.0.0',
        port=5000
    )