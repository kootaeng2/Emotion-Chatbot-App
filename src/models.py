# models.py
# db관련한 모델 코드
# User, Diary 모델정의

from . import db
from werkzeug.security import generate_password_hash, check_password_hash # 비밀번호 해싱(암호화, *처리해줌)
import uuid

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default =lambda :str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # User가 Diary와의 관계를 정의하고, Diary에서는 'author'를 통해 User에 접근합니다.
    diaries = db.relationship('Diary', backref='author', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"
    
class Diary(db.Model):
    id = db.Column(db.String(36), primary_key=True, default =lambda :str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

