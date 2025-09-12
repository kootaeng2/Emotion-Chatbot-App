from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# 전역 SQLAlchemy 객체 생성
db = SQLAlchemy()

def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 팩토리 함수.
    """
    app = Flask(__name__)
    
    # 1. 영구 저장소에 데이터베이스 경로 설정
    # Hugging Face Spaces의 '/data'는 persistent_storage 요청 시 생성되는 쓰기 가능한 공간입니다.
    db_path = '/data/database.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # 2. 기타 Flask 앱 설정
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session' # 실제 배포 시에는 더 복잡한 키로 변경하는 것이 좋습니다.
    
    # 3. SQLAlchemy 인스턴스를 Flask 앱에 초기화
    db.init_app(app)

    # 4. 블루프린트(분리된 기능들) 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # 5. 앱 컨텍스트 안에서 데이터베이스 테이블 생성
    # 앱이 시작될 때 models.py에 정의된 테이블들이 없다면 자동으로 생성합니다.
    with app.app_context():
        # models를 이 안에서 임포트하여 순환 참조 문제를 방지합니다.
        from . import models 
        db.create_all()
        
    return app