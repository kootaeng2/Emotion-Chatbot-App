# src/models.py
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy.sql import func

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # --- ▼▼▼▼▼ 수정 부분 ▼▼▼▼▼ ---
    # password_hash 컬럼의 길이를 128에서 256으로 늘려줍니다.
    password_hash = db.Column(db.String(256), nullable=False)
    # --- ▲▲▲▲▲ 수정 부분 끝 ▲▲▲▲▲ ---

    diaries = db.relationship('Diary', backref='author', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Diary(db.Model):
    # (Diary 모델은 수정할 필요 없습니다.)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())