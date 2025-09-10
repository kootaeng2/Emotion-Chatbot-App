# src/app.py 백업용

# ---------------------------------
# 1. 라이브러리 및 모듈 임포트
# ---------------------------------
from .models import User,Diary  # db관련 모델
import os
import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# '현재 폴더에 있는' 모듈들을 상대 경로로 임포트
from .emotion_engine import load_emotion_classifier, predict_emotion
from .recommender import Recommender

# ---------------------------------
# 2. Flask 앱 초기화 및 기본 설정
# ---------------------------------
app = Flask(__name__)

# 데이터베이스 파일 경로 설정
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 세션 데이터를 암호화하기 위한 시크릿 키 (⚠️ 실제 배포 시에는 더 복잡한 값으로 변경하세요!)
app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'

# 데이터베이스 객체 생성
db = SQLAlchemy(app)

# ---------------------------------
# 3. 데이터베이스 모델 정의
# ---------------------------------
class User(db.Model):
    """사용자 정보 저장을 위한 모델"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """비밀번호를 해싱하여 저장"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """해시된 비밀번호와 입력된 비밀번호를 비교"""
        return check_password_hash(self.password_hash, password)

# ---------------------------------
# 4. AI 엔진 및 추천기 초기 로딩
# ---------------------------------
print("AI 챗봇 서버를 준비 중입니다...")
emotion_classifier = load_emotion_classifier()
recommender = Recommender()
emotion_emoji_map = {
    '기쁨': '😄', '행복': '😊', '사랑': '❤️',
    '불안': '😟', '슬픔': '😢', '상처': '💔',
    '분노': '😠', '혐오': '🤢', '짜증': '😤',
    '놀람': '😮',
    '중립': '😐',
}
print("✅ AI 챗봇 서버가 성공적으로 준비되었습니다.")

# ---------------------------------
# 5. 라우트(Routes) 정의
# ---------------------------------

# --- 사용자 인증 관련 라우트 ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            return "이미 존재하는 사용자 이름입니다."
            
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            return "로그인 정보가 올바르지 않습니다."
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# --- 메인 애플리케이션 라우트 ---
@app.route("/")
def home():
    """메인 페이지. 로그인하지 않은 경우 로그인 페이지로 이동."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # 로그인한 사용자의 이름을 템플릿으로 전달
    return render_template("emotion_homepage.html", username=session.get('username'))

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """일기 분석 및 콘텐츠 추천 API."""
    # API 요청도 로그인된 사용자만 가능하도록 체크
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    predicted_emotion = predict_emotion(emotion_classifier, user_diary)

    # --- 여기에 DB 저장 로직 추가 ---
    try:
        user_id = session['user_id']
        # 새로운 Diary 객체를 만들어 DB에 저장합니다.
        new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
        db.session.add(new_diary_entry)
        db.session.commit()
    except Exception as e:
        # DB 저장 중 오류가 발생하면 서버 로그에 기록합니다.
        print(f"DB 저장 오류: {e}")
        db.session.rollback() # 오류 발생 시 작업을 되돌립니다.
   
    accept_recs = recommender.recommend(predicted_emotion, "수용")
    
    return jsonify(response_data)
    
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

# ---------------------------------
# 6. 애플리케이션 실행
# ---------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all() # (선택사항) 앱 실행 시 DB가 없으면 자동으로 생성.
    app.run(debug=True)