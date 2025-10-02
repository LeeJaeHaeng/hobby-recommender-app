"""
사용자 관련 모델
User, UserProfile, SurveyQuestion, SurveyResponse
"""

from datetime import datetime
from . import db
from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """사용자 기본 정보"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    age = db.Column(db.Integer)
    gender = db.Column(db.Enum('male', 'female', 'other'))
    location = db.Column(db.String(100))
    
    # 보안 필드
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), index=True)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    # 소프트 삭제
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    survey_responses = db.relationship('SurveyResponse', backref='user', cascade='all, delete-orphan')
    hobby_ratings = db.relationship('UserHobbyRating', backref='user', cascade='all, delete-orphan')
    notifications = db.relationship('UserNotification', backref='user', cascade='all, delete-orphan')
    feedback = db.relationship('UserFeedback', backref='user')
    
    def set_password(self, password):
        """비밀번호 해싱"""
        try:
            self.password_hash = generate_password_hash(password)
        except Exception as e:
            raise ValueError(f"비밀번호 설정 실패: {str(e)}")
    
    def check_password(self, password):
        """비밀번호 검증"""
        try:
            if not self.password_hash:
                return False
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            return False
    
    def is_account_locked(self):
        """계정 잠금 상태 확인"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def to_dict(self, include_sensitive=False):
        """딕셔너리 변환 (API 응답용)"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email if include_sensitive else self.email.split('@')[0] + '@***',
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserProfile(db.Model):
    """사용자 성향 프로필 (설문 분석 결과)"""
    __tablename__ = 'user_profiles'
    
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # 성향 점수 (0.00 ~ 1.00)
    outdoor_preference = db.Column(db.Numeric(3, 2), default=0)
    social_preference = db.Column(db.Numeric(3, 2), default=0)
    creative_preference = db.Column(db.Numeric(3, 2), default=0)
    learning_preference = db.Column(db.Numeric(3, 2), default=0)
    physical_activity = db.Column(db.Numeric(3, 2), default=0)
    
    budget_level = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 제약조건 (체크)
    __table_args__ = (
        CheckConstraint('outdoor_preference >= 0 AND outdoor_preference <= 1', name='chk_outdoor_pref'),
        CheckConstraint('social_preference >= 0 AND social_preference <= 1', name='chk_social_pref'),
        CheckConstraint('creative_preference >= 0 AND creative_preference <= 1', name='chk_creative_pref'),
        CheckConstraint('learning_preference >= 0 AND learning_preference <= 1', name='chk_learning_pref'),
        CheckConstraint('physical_activity >= 0 AND physical_activity <= 1', name='chk_physical_act'),
    )
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'profile_id': self.profile_id,
            'user_id': self.user_id,
            'outdoor_preference': float(self.outdoor_preference) if self.outdoor_preference else 0,
            'social_preference': float(self.social_preference) if self.social_preference else 0,
            'creative_preference': float(self.creative_preference) if self.creative_preference else 0,
            'learning_preference': float(self.learning_preference) if self.learning_preference else 0,
            'physical_activity': float(self.physical_activity) if self.physical_activity else 0,
            'budget_level': self.budget_level,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'


class SurveyQuestion(db.Model):
    """설문 질문"""
    __tablename__ = 'survey_questions'
    
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('scale', 'choice', 'binary'), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    options = db.Column(db.JSON)  # {"min": 1, "max": 5} 또는 {"options": ["A", "B"]}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    responses = db.relationship('SurveyResponse', backref='question', cascade='all, delete-orphan')
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'question_id': self.question_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'category': self.category,
            'options': self.options
        }
    
    def __repr__(self):
        return f'<SurveyQuestion {self.question_id}: {self.category}>'


class SurveyResponse(db.Model):
    """설문 응답"""
    __tablename__ = 'survey_responses'
    
    response_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.question_id', ondelete='CASCADE'), nullable=False)
    answer_value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_user_question', 'user_id', 'question_id'),
    )
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'response_id': self.response_id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'answer_value': self.answer_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SurveyResponse user={self.user_id} question={self.question_id}>'