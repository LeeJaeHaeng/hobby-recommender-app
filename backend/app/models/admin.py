"""
관리자 관련 모델
AdminUser, AdminActivityLog, UserFeedback, Announcement, UserNotification
"""

from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class AdminUser(db.Model):
    """관리자 계정"""
    __tablename__ = 'admin_users'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum('super_admin', 'content_manager', 'support'), default='content_manager')
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    activity_logs = db.relationship('AdminActivityLog', backref='admin', cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='creator')
    feedback_responses = db.relationship('UserFeedback', foreign_keys='UserFeedback.responded_by', backref='responder')
    
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
        except Exception:
            return False
    
    def has_permission(self, required_role):
        """권한 확인"""
        role_hierarchy = {
            'support': 1,
            'content_manager': 2,
            'super_admin': 3
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AdminUser {self.username} ({self.role})>'


class AdminActivityLog(db.Model):
    """관리자 활동 로그"""
    __tablename__ = 'admin_activity_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.admin_id', ondelete='CASCADE'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, VIEW
    target_table = db.Column(db.String(50), nullable=False, index=True)
    target_id = db.Column(db.Integer)
    action_details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_admin_action', 'admin_id', db.text('created_at DESC')),
        db.Index('idx_target', 'target_table', 'target_id'),
    )
    
    @staticmethod
    def log_action(admin_id, action_type, target_table, target_id=None, details=None, ip_address=None, user_agent=None):
        """활동 로그 기록 헬퍼 메서드"""
        try:
            log = AdminActivityLog(
                admin_id=admin_id,
                action_type=action_type,
                target_table=target_table,
                target_id=target_id,
                action_details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(log)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"로그 기록 실패: {str(e)}")
            return False
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'log_id': self.log_id,
            'admin_id': self.admin_id,
            'action_type': self.action_type,
            'target_table': self.target_table,
            'target_id': self.target_id,
            'action_details': self.action_details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AdminActivityLog {self.action_type} on {self.target_table}>'


class UserFeedback(db.Model):
    """사용자 피드백/문의"""
    __tablename__ = 'user_feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    feedback_type = db.Column(db.Enum('bug', 'suggestion', 'question', 'complaint'), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'in_progress', 'resolved', 'closed'), default='pending', index=True)
    priority = db.Column(db.Enum('low', 'medium', 'high', 'urgent'), default='medium')
    admin_response = db.Column(db.Text)
    responded_by = db.Column(db.Integer, db.ForeignKey('admin_users.admin_id', ondelete='SET NULL'))
    responded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_user=False):
        """딕셔너리 변환"""
        data = {
            'feedback_id': self.feedback_id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type,
            'subject': self.subject,
            'content': self.content,
            'status': self.status,
            'priority': self.priority,
            'admin_response': self.admin_response,
            'responded_by': self.responded_by,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_user and self.user:
            data['user_info'] = {
                'username': self.user.username,
                'email': self.user.email
            }
        
        return data
    
    def __repr__(self):
        return f'<UserFeedback {self.feedback_id}: {self.subject}>'


class Announcement(db.Model):
    """공지사항"""
    __tablename__ = 'announcements'
    
    announcement_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.Enum('notice', 'update', 'maintenance', 'event'), default='notice')
    is_published = db.Column(db.Boolean, default=False, index=True)
    is_pinned = db.Column(db.Boolean, default=False, index=True)
    view_count = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime, index=True)
    expires_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.admin_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_published', 'is_published', db.text('published_at DESC')),
        db.Index('idx_pinned', 'is_pinned', db.text('published_at DESC')),
    )
    
    def is_active(self):
        """공지사항이 유효한지 확인"""
        if not self.is_published:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def increment_view_count(self):
        """조회수 증가"""
        try:
            self.view_count += 1
            db.session.commit()
        except Exception:
            db.session.rollback()
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'announcement_id': self.announcement_id,
            'title': self.title,
            'content': self.content,
            'announcement_type': self.announcement_type,
            'is_published': self.is_published,
            'is_pinned': self.is_pinned,
            'view_count': self.view_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active()
        }
    
    def __repr__(self):
        return f'<Announcement {self.title}>'


class UserNotification(db.Model):
    """사용자 알림"""
    __tablename__ = 'user_notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    notification_type = db.Column(db.Enum('recommendation', 'gathering', 'announcement', 'system'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_user_unread', 'user_id', 'is_read', db.text('created_at DESC')),
    )
    
    def mark_as_read(self):
        """읽음 표시"""
        try:
            if not self.is_read:
                self.is_read = True
                self.read_at = datetime.utcnow()
                db.session.commit()
        except Exception:
            db.session.rollback()
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'link_url': self.link_url,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<UserNotification {self.notification_id} for user {self.user_id}>'