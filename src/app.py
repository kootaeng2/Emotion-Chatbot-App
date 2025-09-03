# app.py (수정 후 최종 버전)

from flask import Flask, render_template, request, jsonify
# '현재 폴더에 있는' 이라는 의미로 파일 이름 앞에 점(.)을 추가합니다.
from .emotion_engine import load_emotion_classifier, predict_emotion
from .recommender import Recommender
import random

app = Flask(__name__)

# --- (이하 나머지 코드는 모두 동일) ---
print("AI 챗봇 서버를 준비 중입니다...")
# ...

app = Flask(__name__)

print("AI 챗봇 서버를 준비 중입니다...")
# 서버가 시작될 때 AI 엔진과 추천기를 각각 한 번씩만 로드합니다.
emotion_classifier = load_emotion_classifier()
recommender = Recommender()
# 웹페이지에 감정별 이모지를 보내주기 위한 딕셔너리입니다.
emotion_emoji_map = {
    '기쁨': '😄', '행복': '😊', '사랑': '❤️',
    '불안': '😟', '슬픔': '😢', '상처': '💔',
    '분노': '😠', '혐오': '🤢', '짜증': '😤',
    '놀람': '😮',
    '중립': '😐',
}
print("✅ AI 챗봇 서버가 성공적으로 준비되었습니다.")

@app.route("/")
def home():
    """웹 브라우저가 처음 접속했을 때 보여줄 메인 페이지를 설정합니다."""
    # templates 폴더 안에 있는 emotion_homepage.html 파일을 화면에 보여줍니다.
    return render_template("emotion_homepage.html")

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """웹페이지의 '추천 받기' 버튼 클릭 요청을 처리하는 부분입니다."""
    # 1. 웹페이지로부터 사용자가 입력한 일기 내용을 받습니다.
    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    # 2. emotion_engine을 사용해 감정을 예측합니다.
    predicted_emotion = predict_emotion(emotion_classifier, user_diary)
    
    # 3. recommender를 사용해 '수용'과 '전환' 추천을 모두 받습니다.
    accept_recs = recommender.recommend(predicted_emotion, "수용")
    change_recs = recommender.recommend(predicted_emotion, "전환")
    
    # 4. 각 추천 목록에서 랜덤으로 하나씩 선택합니다. (결과가 없을 경우를 대비)
    accept_choice = random.choice(accept_recs) if accept_recs else "추천 없음"
    change_choice = random.choice(change_recs) if change_recs else "추천 없음"

    # 5. 웹페이지에 보여줄 최종 텍스트를 조합합니다.
    recommendation_text = (
        f"<b>[ 이 감정을 더 깊이 느끼고 싶다면... (수용) ]</b><br>"
        f"• {accept_choice}<br><br>"
        f"<b>[ 이 감정에서 벗어나고 싶다면... (전환) ]</b><br>"
        f"• {change_choice}"
    )

    # 6. 최종 결과를 JSON 형태로 웹페이지에 돌려줍니다.
    response_data = {
        "emotion": predicted_emotion,
        "emoji": emotion_emoji_map.get(predicted_emotion, '🤔'),
        "recommendation": recommendation_text
    }
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)