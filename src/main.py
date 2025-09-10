# src/main.py
# 기존 app.py에서 main과 관련해서 분리

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Diary
from .emotion_engine import load_emotion_classifier, predict_emotion
from .recommender import Recommender
import random

bp=Blueprint('main', __name__)

emotion_clssifier=load_emotion_classifier()
recommender=Recommender()
emotion_emoji_map={
    '기쁨':'😄', '행복':'😊', '사랑':'❤️',
    '불안':'😟', '슬픔':'😢', '상처':'💔',
    '분노':'😠', '혐오':'🤢', '짜증':'😤',
    '놀람':'😮',
    '중립':'😐',
    '공포':'😱'
}

@bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('auth.login'))
    return render_template("emotion_homepage.html", username=session.get('username'))
