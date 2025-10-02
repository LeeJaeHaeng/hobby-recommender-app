"""
취미 관련 모델
Hobby, UserHobbyRating, Gathering
"""

from datetime import datetime
from . import db
from sqlalchemy import CheckConstraint


class Hobby(db.Model):
    """취미 마스터 테이블"""
    __tablename__ = 'hobbies'
    
    hobby_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # 난이도 및 강도 (1~5)
    difficulty_level = db.Column(db.Integer, default=1)
    physical_intensity = db.Column(db.Integer, default=1)
    creativity_level = db.Column(db.Integer, default=1)
    
    # 속성
    indoor_outdoor = db.Column(db.Enum('indoor', 'outdoor', 'both'), default='both')
    social_individual = db.Column(db.Enum('social', 'individual', 'both'), default='both')
    required_budget = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    time_commitment = db.Column(db.String(50))
    
    # 미디어
    tutorial_video_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    
    # 소프트 삭제
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    ratings = db.relationship('UserHobbyRating', backref='hobby', cascade='all, delete-orphan')
    gatherings = db.relationship('Gathering', backref='hobby', cascade='all, delete-orphan')
    
    # 제약조건
    __table_args__ = (
        CheckConstraint('difficulty_level >= 1 AND difficulty_level <= 5', name='chk_difficulty'),
        CheckConstraint('physical_intensity >= 1 AND physical_intensity <= 5', name='chk_physical'),
        CheckConstraint('creativity_level >= 1 AND creativity_level <= 5', name='chk_creativity'),
        db.Index('idx_hobby_attributes', 'indoor_outdoor', 'social_individual', 'required_budget', 'difficulty_level'),
        db.Index('idx_hobbies_active', 'is_deleted', 'category'),
    )
    
    def get_average_rating(self):
        """평균 평점 계산"""
        try:
            if not self.ratings:
                return 0.0
            total = sum(r.rating for r in self.ratings)
            return round(total / len(self.ratings), 2)
        except Exception as e:
            return 0.0
    
    def get_rating_count(self):
        """평가 개수"""
        try:
            return len(self.ratings)
        except Exception:
            return 0
    
    def to_dict(self, include_stats=False):
        """딕셔너리 변환"""
        data = {
            'hobby_id': self.hobby_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'difficulty_level': self.difficulty_level,
            'physical_intensity': self.physical_intensity,
            'creativity_level': self.creativity_level,
            'indoor_outdoor': self.indoor_outdoor,
            'social_individual': self.social_individual,
            'required_budget': self.required_budget,
            'time_commitment': self.time_commitment,
            'tutorial_video_url': self.tutorial_video_url,
            'image_url': self.image_url
        }
        
        if include_stats:
            data['average_rating'] = self.get_average_rating()
            data['rating_count'] = self.get_rating_count()
        
        return data
    
    def __repr__(self):
        return f'<Hobby {self.name}>'


class UserHobbyRating(db.Model):
    """사용자의 취미 평가"""
    __tablename__ = 'user_hobby_ratings'
    
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    hobby_id = db.Column(db.Integer, db.ForeignKey('hobbies.hobby_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1~5
    review_text = db.Column(db.Text)
    experienced = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 복합 인덱스 및 제약조건
    __table_args__ = (
        db.UniqueConstraint('user_id', 'hobby_id', name='unique_user_hobby'),
        db.Index('idx_hobby_rating', 'hobby_id', 'rating'),
        db.Index('idx_user_rating_activity', 'user_id', db.text('created_at DESC')),
        CheckConstraint('rating >= 1 AND rating <= 5', name='chk_rating_range'),
    )
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'rating_id': self.rating_id,
            'user_id': self.user_id,
            'hobby_id': self.hobby_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'experienced': self.experienced,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<UserHobbyRating user={self.user_id} hobby={self.hobby_id} rating={self.rating}>'


class Gathering(db.Model):
    """모임/동아리 정보"""
    __tablename__ = 'gatherings'
    
    gathering_id = db.Column(db.Integer, primary_key=True)
    hobby_id = db.Column(db.Integer, db.ForeignKey('hobbies.hobby_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    region = db.Column(db.String(50), index=True)
    meeting_type = db.Column(db.Enum('online', 'offline', 'hybrid'), default='offline')
    schedule_info = db.Column(db.Text)
    member_count = db.Column(db.Integer, default=0)
    contact_info = db.Column(db.String(200))
    website_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_gathering_location', 'hobby_id', 'region', 'is_active'),
    )
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'gathering_id': self.gathering_id,
            'hobby_id': self.hobby_id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'region': self.region,
            'meeting_type': self.meeting_type,
            'schedule_info': self.schedule_info,
            'member_count': self.member_count,
            'contact_info': self.contact_info,
            'website_url': self.website_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Gathering {self.name}>'