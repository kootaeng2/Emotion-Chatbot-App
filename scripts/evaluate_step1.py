# 파일 이름: evaluate_step1.py
# 1단계 모델을 불러와서 평가 및 혼동 행렬만 다시 생성하는 스크립트

import os
import pandas as pd
from dataclasses import dataclass
import json
import re
import torch
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import platform
import matplotlib.pyplot as plt
import seaborn as sns

# train_final.py와 동일한 클래스 및 함수들
# (데이터 로딩, 메트릭 계산 등)
# -----------------------------------------------------------------
@dataclass
class TrainingConfig:
    mode: str = "emotion" 
    data_dir: str = "./data"
    output_dir: str = "./results1024"
    # [수정] 1차 NSMC 모델 경로 (사용자님 경로로)
    base_model_name: str = r"E:\Emotion\results\nsmc_model" 
    eval_batch_size: int = 64
    max_length: int = 128
    
    def get_step1_model_dir(self) -> str:
        # [수정] 이미 훈련된 1단계 모델의 "best_model" 폴더를 지정
        return os.path.join(self.output_dir, 'emotion_model_step1_3class', 'best_model')

class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    return {'accuracy': acc, 'f1': f1}

def clean_text(text: str) -> str:
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', str(text))

def map_ecode_to_6class(e_code_str):
    if not isinstance(e_code_str, str) or not e_code_str.startswith('E'): return None
    try: code_num = int(e_code_str[1:]) 
    except (ValueError, TypeError): return None
    if 0 <= code_num <= 9:   return '기쁨' 
    elif 10 <= code_num <= 19: return '분노'
    elif 20 <= code_num <= 29: return '슬픔'
    elif 30 <= code_num <= 39: return '불안'
    elif 40 <= code_num <= 49: return '상처'
    elif 50 <= code_num <= 59: return '당황'
    else: return None 

def map_6_to_3_groups(emotion_6_class):
    if emotion_6_class == '슬픔': return '그룹1(슬픔)'
    elif emotion_6_class in ['불안', '상처']: return '그룹2(불안,상처)'
    elif emotion_6_class in ['분노', '당황', '기쁨']: return '그룹3(분노,당황,기쁨)'
    else: return None 

def load_and_process(text_file, label_file, data_dir):
    text_path = os.path.join(data_dir, text_file)
    label_path = os.path.join(data_dir, label_file)
    try:
        df_text = pd.read_excel(text_path, header=0)
        with open(label_path, 'r', encoding='utf-8') as f:
            labels_raw = json.load(f)
    except FileNotFoundError as e:
        print(f"오류: 필수 파일을 찾을 수 없습니다: {e}")
        return pd.DataFrame()
    e_codes = []
    for dialogue in labels_raw:
        try: e_codes.append(dialogue['profile']['emotion']['type'])
        except KeyError: e_codes.append(None)
    if len(df_text) != len(e_codes):
        min_len = min(len(df_text), len(e_codes))
        df_text = df_text.iloc[:min_len]
        e_codes = e_codes[:min_len]
    df_labels = pd.DataFrame({'e_code': e_codes})
    df_combined = pd.concat([df_text, df_labels], axis=1)
    dialogue_cols = [col for col in df_combined.columns if '문장' in str(col)]
    for col in dialogue_cols:
        df_combined[col] = df_combined[col].astype(str).fillna('')
    df_combined['text'] = df_combined[dialogue_cols].apply(lambda row: ' '.join(row), axis=1)
    df_combined['cleaned_text'] = df_combined['text'].apply(clean_text)
    df_combined['major_emotion'] = df_combined['e_code'].apply(map_ecode_to_6class)
    df_combined.dropna(subset=['major_emotion'], inplace=True)
    df_combined['group_emotion'] = df_combined['major_emotion'].apply(map_6_to_3_groups)
    df_combined.dropna(subset=['group_emotion', 'cleaned_text'], inplace=True)
    df_combined = df_combined[df_combined['cleaned_text'].str.strip() != '']
    return df_combined

def get_test_data(config: TrainingConfig) -> pd.DataFrame:
    """[수정] Test Set만 불러오는 함수"""
    print("Loading TEST set (from validation-origin.xlsx + test.json)...")
    df_test = load_and_process(
        "validation-origin.xlsx",  
        "test.json",               
        config.data_dir
    )
    if df_test.empty:
        print("오류: Test 데이터 로딩 실패.")
        return pd.DataFrame()
    print(f"Test data loaded: {len(df_test)} rows")
    return df_test
# -----------------------------------------------------------------


def run_evaluation():
    # --- 1. 한글 폰트 설정 ---
    try:
        if platform.system() == 'Windows':
            plt.rc('font', family='Malgun Gothic')
        elif platform.system() == 'Darwin': # Mac OS
            plt.rc('font', family='AppleGothic')
        else: # Linux (코랩 등)
            plt.rc('font', family='NanumBarunGothic')
        plt.rcParams['axes.unicode_minus'] = False
        print("한글 폰트 설정 완료.")
    except Exception as e:
        print(f"한글 폰트 설정 경고: {e}. 혼동 행렬의 라벨이 깨질 수 있습니다.")

    config = TrainingConfig()
    
    # --- 2. 모델 및 토크나이저 로드 ---
    model_dir = config.get_step1_model_dir()
    output_dir = os.path.dirname(model_dir) # .../emotion_model_step1_3class
    
    if not os.path.exists(model_dir):
        print(f"오류: 훈련된 모델을 찾을 수 없습니다: {model_dir}")
        print("train_final.py를 먼저 실행하세요.")
        return

    print(f"저장된 1단계 모델 로드: {model_dir}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)

    # --- 3. 테스트 데이터 로드 및 전처리 ---
    df_test = get_test_data(config)
    if df_test.empty: return

    # 라벨 인코딩 (모델 config에서 불러오기)
    label_to_id = model.config.label2id
    id_to_label = model.config.id2label
    print(f"모델의 라벨 맵 로드: {label_to_id}")

    df_test['label'] = df_test['group_emotion'].map(label_to_id)
    
    # NaN 라벨이 있는지 확인 (test.json에 훈련 시 없던 라벨이 있을 경우)
    if df_test['label'].isnull().any():
        print("경고: Test set에 훈련 시 없던 라벨이 있습니다. 해당 데이터는 평가에서 제외됩니다.")
        df_test.dropna(subset=['label'], inplace=True)
        
    df_test['label'] = df_test['label'].astype(int)

    test_encodings = tokenizer(list(df_test['cleaned_text']), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    test_dataset = EmotionDataset(test_encodings, df_test['label'].tolist())

    # --- 4. Trainer 설정 (평가 전용) ---
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_eval_batch_size=config.eval_batch_size,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        compute_metrics=compute_metrics
    )

    # --- 5. 평가 실행 및 혼동 행렬 생성 ---
    print("\n--- (2) Test Set 최종 평가 (수능) ---")
    test_predictions = trainer.predict(test_dataset)
    test_metrics = test_predictions.metrics
    print(f"최종 Test 평가 결과: {test_metrics}")

    # (이 부분은 이미 성공했으므로 중복 저장)
    results_path = os.path.join(output_dir, "TEST_evaluation_results.json")
    with open(results_path, "w", encoding='utf-8') as f:
        json.dump(test_metrics, f, indent=4, ensure_ascii=False)
    print(f"*** 최종 Test 평가 결과가 {results_path}에 저장되었습니다. ***")

    print("\n--- 혼동 행렬 생성 (Test Set) ---")
    try:
        y_pred = test_predictions.predictions.argmax(-1)
        y_true = test_predictions.label_ids

        labels = [id_to_label[i] for i in sorted(id_to_label.keys())]
        cm = confusion_matrix(y_true, y_pred, labels=[label_to_id[l] for l in labels])
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
        plt.xlabel('예측 라벨 (Predicted Label)')
        plt.ylabel('실제 라벨 (True Label)')
        plt.title('Confusion Matrix (TEST Set - 3 Groups)')
        
        cm_path = os.path.join(output_dir, "TEST_confusion_matrix.png")
        plt.savefig(cm_path)
        print(f"Test Set 혼동 행렬이 {cm_path}에 저장되었습니다.")
        print("--- 평가 및 혼동 행렬 생성 완료 ---")

    except Exception as e:
        print("\n!!! 치명적 오류: 혼동 행렬 생성 실패 !!!")
        print(f"오류 메시지: {e}")
        print("matplotlib, seaborn, 또는 한글 폰트 설정을 확인하세요.")


if __name__ == "__main__":
    run_evaluation()