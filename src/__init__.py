# src/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    db_path = '/data/database.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)

    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # with app.app_context()를 사용하여 앱이 시작될 때 DB 테이블을 생성합니다.
    with app.app_context():
        # --- ▼▼▼▼▼ 수정 부분: 오류 방어 코드 추가 ▼▼▼▼▼ ---
        try:
            db.create_all()
            print("✅ 데이터베이스 테이블 생성을 시도했습니다 (성공 또는 이미 존재).")
        except Exception as e:
            # 부팅 시점에 DB 오류가 발생하더라도 앱이 다운되지 않도록 로그만 남깁니다.
            print(f"🔥🔥🔥 부팅 시 DB 테이블 생성 실패! 원인: {e}")
        # --- ▲▲▲▲▲ 수정 부분 끝 ▲▲▲▲▲ ---
        
    return app