# src/main.py
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
# __init__에서 생성된 db, emotion_classifier, recommender 객체를 가져옵니다.
from . import db, emotion_classifier, recommender
from .models import Diary, User
from .emotion_engine import predict_emotion
import random

bp = Blueprint('main', __name__)

emotion_emoji_map = {
    '기쁨':'😄', '행복':'😊', '사랑':'❤️',
    '불안':'😟', '슬픔':'😢', '상처':'💔',
    '분노':'😠', '혐오':'🤢', '짜증':'😤',
    '놀람':'😮', '중립':'😐',
}

@bp.route("/")
def home():
    # "로그인하지 않았다면" 로그인 페이지로 보냅니다.
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    return render_template("emotion_homepage.html", username=session.get('username'))

@bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    predicted_emotion = predict_emotion(emotion_classifier, user_diary)

    try:
        user_id = session['user_id']
        new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
        db.session.add(new_diary_entry)
        db.session.commit()
    except Exception as e:
        print(f"DB 저장 오류: {e}")
        db.session.rollback()
    
    accept_recs = recommender.recommend(predicted_emotion, "수용")
    change_recs = recommender.recommend(predicted_emotion, "전환")
    
    accept_choice = random.choice(accept_recs) if accept_recs else "추천 없음"
    change_choice = random.choice(change_recs) if change_recs else "추천 없음"

    recommendation_text = (
        f"<b>[ 이 감정을 더 깊이 느끼고 싶다면... (수용) ]</b><br>"
        f"• {accept_choice}<br><br>"
        f"<b>[ 이 감정에서 벗어나고 싶다면... (전환) ]</b><br>"
        f"• {change_choice}"
    )

    response_data = {
        "emotion": predicted_emotion,
        "emoji": emotion_emoji_map.get(predicted_emotion, '🤔'),
        "recommendation": recommendation_text
    }
    return jsonify(response_data)

@bp.route('/my_diary')
def my_diary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user_diaries = Diary.query.filter_by(user_id=user_id).order_by(Diary.created_at.desc()).all()
    
    return render_template('my_diary.html', diaries=user_diaries)