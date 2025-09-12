from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from . import db
from .models import User, Diary
import logging
from .emotion_engine import predict_emotion # load_emotion_classifier는 이제 필요 없습니다.
# from .recommender import Recommender # Recommender도 여기서 직접 생성하지 않습니다.
import random

bp = Blueprint('main', __name__)

# --- ▼▼▼▼▼ 핵심 수정 부분 ▼▼▼▼▼ ---
# 아래 두 줄을 삭제합니다. __init__.py에서 처리하기 때문입니다.
# emotion_classifier = load_emotion_classifier()
# recommender = Recommender()
# --- ▲▲▲▲▲ 핵심 수정 부분 끝 ▲▲▲▲▲ ---

# emotion_emoji_map은 그대로 둡니다.
emotion_emoji_map = {
    'E10': '😄', # 기쁨
    'E14': '😢', # 슬픔
    'E13': '😠', # 분노
    'E12': '😟', # 불안
    'E15': '😮', # 놀람
    'E16': '😐', # 중립
}

@bp.route('/')
def home():
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

    # --- ▼▼▼▼▼ 핵심 수정 부분 ▼▼▼▼▼ ---
    # current_app을 통해 안전하게 로드된 모델과 추천기를 가져옵니다.
    predicted_emotion = predict_emotion(current_app.emotion_classifier, user_diary)
    # --- ▲▲▲▲▲ 핵심 수정 부분 끝 ▲▲▲▲▲ ---

    try:
        user_id = session['user_id']
        new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
        db.session.add(new_diary_entry)
        db.session.commit()
    except Exception as e:
        logging.exception("DB 저장 오류 발생!")
        db.session.rollback()
    
    # --- ▼▼▼▼▼ 핵심 수정 부분 ▼▼▼▼▼ ---
    accept_recs = current_app.recommender.recommend(predicted_emotion, "수용")
    change_recs = current_app.recommender.recommend(predicted_emotion, "전환")
    # --- ▲▲▲▲▲ 핵심 수정 부분 끝 ▲▲▲▲▲ ---
    
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