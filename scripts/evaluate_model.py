# 파일 이름: evaluate.py

import torch
import pandas as pd
# 'from pyexpat import model' 라인은 완전히 삭제합니다.
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import os
import json
import re
import platform
import matplotlib.pyplot as plt
import seaborn as sns

# --- Matplotlib 한글 폰트 설정 (이전과 동일) ---
try:
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # Mac OS
        plt.rc('font', family='AppleGothic')
    else: # Linux
        plt.rc('font', family='NanumBarunGothic')
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("한글 폰트 설정에 실패했습니다. 그래프의 라벨이 깨질 수 있습니다.")

# --- 헬퍼(Helper) 함수 및 클래스 정의 (이전과 동일) ---
class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item
    def __len__(self):
        return len(self.labels)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

# --- train_final.py와 동일한 데이터 처리 로직 전체를 여기에 추가 ---
def map_ecode_to_major_emotion(ecode):
    """E코드를 대분류 감정으로 매핑하는 함수"""
    try:
        code_num = int(ecode[1:])
    except (ValueError, TypeError):
        return None
    
    # 이 부분은 train_final.py와 완전히 동일해야 합니다.
    if 10 <= code_num <= 19: return '분노'
    elif 20 <= code_num <= 29: return '슬픔'
    elif 30 <= code_num <= 39: return '불안'
    elif 40 <= code_num <= 49: return '상처'
    elif 50 <= code_num <= 59: return '당황'
    elif 60 <= code_num <= 69: return '기쁨'
    else: return None

def load_and_process_validation_data(file_path='./data/'):
    """JSON을 로드하고 레이블을 통합/처리하는 완전한 함수"""
    val_label_path = os.path.join(file_path, 'validation-label.json')
    try:
        with open(val_label_path, 'r', encoding='utf-8') as f:
            validation_data_raw = json.load(f)
    except FileNotFoundError:
        print(f"오류: 평가용 라벨 파일 '{val_label_path}'를 찾을 수 없습니다.")
        return None
        
    data = [{'text': " ".join(d['talk']['content'].values()), 'emotion': d['profile']['emotion']['type']} for d in validation_data_raw]
    df_val = pd.DataFrame(data)

    df_val['major_emotion'] = df_val['emotion'].apply(map_ecode_to_major_emotion)
    df_val.dropna(subset=['major_emotion'], inplace=True)
    
    def clean_text(text):
        return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)
    df_val['cleaned_text'] = df_val['text'].apply(clean_text)
    
    return df_val

# --- 메인 평가 로직 ---
def evaluate_saved_model():
    """저장된 모델을 불러와 성능 평가 및 혼동 행렬을 생성하는 메인 함수"""
    
    MODEL_PATH = "./results/emotion_model_final"  # 경로는 results1으로 유지
    print(f"'{MODEL_PATH}' 경로의 모델을 평가합니다.")

    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        loaded_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        loaded_model.config.problem_type = "single_label_classification"
    except OSError:
        print(f"오류: '{MODEL_PATH}' 경로에서 모델 또는 토크나이저를 찾을 수 없습니다.")
        return

    df_val = load_and_process_validation_data()
    if df_val is None or df_val.empty: 
        print("처리 후 평가 데이터가 없습니다.")
        return

    # --- 👇👇👇 미정의 변수들을 여기서 정의합니다 👇👇👇 ---
    label2id = loaded_model.config.label2id
    id2label = loaded_model.config.id2label

    df_val['label_id'] = df_val['major_emotion'].map(label2id)
    df_val.dropna(subset=['label_id'], inplace=True)

    val_labels = df_val['label_id'].tolist()
    val_texts = df_val['cleaned_text'].tolist()
    
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
    # --- 👆👆👆 변수 정의 완료 👆👆👆 ---
    
    val_dataset = EmotionDataset(val_encodings, val_labels)

    training_args = TrainingArguments(
        output_dir="./results1/temp_eval",
        report_to="none"
    )

    trainer = Trainer(
        model=loaded_model, 
        args=training_args,
        compute_metrics=compute_metrics
    )

    print("평가를 시작합니다...")
    results = trainer.evaluate(eval_dataset=val_dataset)
    print("\n--- 최종 평가 결과 ---")
    print(results)
    
    print("\n--- 혼동 행렬 생성 ---")
    predictions = trainer.predict(val_dataset)
    y_pred = predictions.predictions.argmax(-1)
    y_true = predictions.label_ids

    labels = [id2label[i] for i in sorted(id2label.keys())]
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('예측 라벨 (Predicted Label)')
    plt.ylabel('실제 라벨 (True Label)')
    plt.title('Confusion Matrix')
    
    cm_path = os.path.join(MODEL_PATH, "confusion_matrix.png")
    plt.savefig(cm_path)
    print(f"혼동 행렬이 {cm_path}에 저장되었습니다.")
    
if __name__ == "__main__":
    evaluate_saved_model()