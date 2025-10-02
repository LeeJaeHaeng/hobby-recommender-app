"""
SQLAlchemy 모델 패키지
모든 데이터베이스 모델을 정의하고 관리합니다.
"""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 인스턴스 (app.py에서 초기화됨)
db = SQLAlchemy()

# 모델 임포트 (순환 참조 방지를 위해 여기서 임포트)
from .user import User, UserProfile, SurveyQuestion, SurveyResponse
from .hobby import Hobby, UserHobbyRating, Gathering
from .admin import AdminUser, AdminActivityLog, UserFeedback, Announcement, UserNotification

__all__ = [
    'db',
    'User',
    'UserProfile',
    'SurveyQuestion',
    'SurveyResponse',
    'Hobby',
    'UserHobbyRating',
    'Gathering',
    'AdminUser',
    'AdminActivityLog',
    'UserFeedback',
    'Announcement',
    'UserNotification'
]