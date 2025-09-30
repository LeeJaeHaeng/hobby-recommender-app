from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# CORS 설정 (프론트엔드와 통신을 위해)
CORS(app, origins=['http://localhost:3000'])

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://hobby_user:password123@localhost:3306/hobby_recommender')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# 데이터베이스 초기화
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 기본 라우트
@app.route('/')
def hello():
    """메인 엔드포인트"""
    return jsonify({
        'message': '퇴직자 취미 추천 시스템 API',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            '/': 'API 정보',
            '/api/health': '헬스 체크',
            '/api/test': '테스트 엔드포인트'
        }
    })

@app.route('/api/health')
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 확인
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = f'disconnected: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test')
def test():
    """테스트 엔드포인트"""
    return jsonify({
        'message': 'API 테스트 성공',
        'timestamp': datetime.now().isoformat()
    })

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Flask 서버를 시작합니다...")
    logger.info("서버 주소: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)