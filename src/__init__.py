from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Hugging Face Spaces Secret에서 DATABASE_URL을 읽어옵니다.
    db_uri = os.environ.get('DATABASE_URL')
    
    # Supabase URI의 'postgres://'를 SQLAlchemy가 인식하는 'postgresql://'로 변경합니다.
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    app.emotion_classifier = load_emotion_classifier()
    app.recommender = Recommender()

    with app.app_context():
        from . import models
        db.create_all()
        
    return app