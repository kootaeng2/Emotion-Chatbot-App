# models.py
# db관련한 모델 코드
# User, Diary 모델정의

from . import db
from werkzeug.security import generate_password_hash, check_password_hash # 비밀번호 해싱(암호화, *처리해줌)
import uuid

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default =lambda :str(uuid.uuid4())) # UUID 형식의 고유 ID, 유저는 문자열로 넣을수 있다. 
    username = db.Column(db.String(80), unique=True, nullable=False)                    # 사용자의 이름은 희귀하고, 공백은 없음
    password_hash = db.Column(db.String(128), nullable=False)                           
    # User가 삭제되면, 관련된 모든 Diary도 함께 삭제되도록 cascade 옵션 추가
    diaries = db.relationship('Diary', backref='author', lazy=True, cascade="all, delete-orphan")
    # 비밀번호를 해싱하여 저장
    def set_password(self, password):
      self.password_hash = generate_password_hash(password)                           
    # 해시된 비밀번호와 입력된 비밀번호를 비교
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)                        
    # 유저 호출명 확인
    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"
    
class Diary(db.Model):
    id = db.Column(db.String(36), primary_key=True, default =lambda :str(uuid.uuid4())) # UUID 형식의 고유 ID
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)        # 작성자 ID (User 모델과 연관)
    content = db.Column(db.Text, nullable=False)                                        # 일기 내용
    emotion = db.Column(db.String(20), nullable=False)                                  # 감정 라벨
    timestamp = db.Column(db.DateTime, server_default=db.func.now())                    # 작성 시간 (기본값: 현재 시간)

    user = db.relationship('User', backref=db.backref('diaries', lazy=True))            # User 모델과의 관계 설정


