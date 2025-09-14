# src/main.py
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request, current_app
from . import db
from .models import Diary, User
from .emotion_engine import predict_emotion 
import random
import logging 

bp = Blueprint('main', __name__)

# recommender.py와 동일하게 E코드를 key로 사용하도록 통일합니다.
emotion_emoji_map = {
    '분노': '😠', '불안': '😟', '슬픔': '😢',
    '평온': '😐', '당황': '😮', '기쁨': '😄',
}

@bp.route("/")
def home():
    logging.warning(f"--- 메인 페이지 접속 시도: 현재 세션 상태: {session} ---")
    if 'user_id' not in session:
        logging.warning("세션에 'user_id'가 없어 로그인 페이지로 리다이렉트합니다.")
        return redirect(url_for('auth.login'))
        
    logging.warning("✅ 세션 확인 성공! 메인 페이지를 렌더링합니다.")
    return render_template("emotion_homepage.html", username=session.get('username'))


@bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    predicted_emotion = predict_emotion(current_app.emotion_classifier, user_diary)

    try:
        user_id = session['user_id']
        new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
        db.session.add(new_diary_entry)
        db.session.commit()
    except Exception as e:
        logging.exception("DB 저장 오류 발생!")
        db.session.rollback()
    
    accept_recs = current_app.recommender.recommend(predicted_emotion, "수용")
    change_recs = current_app.recommender.recommend(predicted_emotion, "전환")
    
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