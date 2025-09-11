# src/main.py
# 기존 app.py에서 main과 관련해서 분리

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Diary
from .emotion_engine import load_emotion_classifier, predict_emotion
from .recommender import Recommender
import random

bp=Blueprint('main', __name__)

emotion_classifier=load_emotion_classifier() # 'emotion_clssifier' -> 'emotion_classifier' 오타 수정
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
    # ❗️ 로직을 "로그인하지 않았다면"으로 수정합니다.
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template("emotion_homepage.html", username=session.get('username'))

# (api_recommend, my_diary 함수는 그대로 유지)
@bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    """AJAX 요청을 통해 일기를 받아, 감정을 분석하고, DB에 저장한 뒤, 추천을 반환하는 API"""
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    # __init__.py에서 로드된 AI 엔진을 사용하여 감정 분석
    predicted_emotion = predict_emotion(emotion_classifier, user_diary)

    try:
        # 현재 세션의 사용자 ID를 가져와서 Diary 객체에 저장
        user_id = session['user_id']
        new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
        db.session.add(new_diary_entry)
        db.session.commit()
    except Exception as e:
        print(f"DB 저장 오류: {e}")
        db.session.rollback()
    
    # __init__.py에서 로드된 추천기를 사용하여 콘텐츠 추천
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
    """로그인한 사용자의 과거 일기 목록을 보여주는 페이지"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # 현재 사용자의 모든 일기를 DB에서 조회 (최신순으로 정렬)
    user_id = session['user_id']
    user_diaries = Diary.query.filter_by(user_id=user_id).order_by(Diary.created_at.desc()).all()
    
    # 조회된 일기 목록을 템플릿으로 전달하여 페이지를 렌더링
    return render_template('my_diary.html', diaries=user_diaries)