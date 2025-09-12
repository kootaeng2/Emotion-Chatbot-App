from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# db 객체를 먼저 생성하되, 아직 앱에 연결하지 않습니다.
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 데이터베이스 경로 설정
    db_path = '/data/database.db'
    
    # 데이터베이스 파일이 위치할 디렉터리 경로
    db_dir = os.path.dirname(db_path)
    # 앱이 시작될 때 디렉터리가 존재하는지 확인하고 없으면 생성합니다.
    # 이 작업은 파일I/O가 비교적 안전한 시점에 수행됩니다.
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    
    # db 객체를 Flask 앱에 초기화(연결)합니다.
    db.init_app(app)

    # 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # with app.app_context()를 사용하여 앱 컨텍스트 안에서 테이블을 생성합니다.
    with app.app_context():
        db.create_all()
        
    return app