# 파일 이름: train_final.py

import os
import pandas as pd
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
from sklearn.model_selection import train_test_split 
from sklearn.utils import resample 
from typing import Dict, List, Tuple
from dataclasses import dataclass
import platform
import matplotlib.pyplot as plt
import seaborn as sns

# --- Matplotlib 한글 폰트 설정 ---
try:
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # Mac OS
        plt.rc('font', family='AppleGothic')
    else: # Linux (코랩 등)
        plt.rc('font', family='NanumBarunGothic')
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"한글 폰트 설정 경고: {e}. 혼동 행렬의 라벨이 깨질 수 있습니다.")

# --- 1. 설정부 ---
@dataclass
class TrainingConfig:
    mode: str = "emotion" 
    data_dir: str = "./data"
    output_dir: str = "./results1024"
    base_model_name: str = "klue/roberta-base"
    eval_batch_size: int = 64
    num_train_epochs: int = 3 
    learning_rate: float = 2e-5
    train_batch_size: int = 16
    weight_decay: float = 0.01
    max_length: int = 128
    warmup_ratio: float = 0.1
    
    def get_model_name(self) -> str:
        if self.mode == 'emotion':
            if not os.path.exists(self.base_model_name):
                print(f"경고: 1차 학습된 NSMC 모델을 찾을 수 없습니다 ({self.base_model_name})")
                print("기본 'klue/roberta-base' 모델로 대신 학습을 시도합니다.")
                return "klue/roberta-base"
            print(f"1차 학습된 모델 로드: {self.base_model_name}")
            return self.base_model_name
        return "klue/roberta-base"
        
    def get_output_dir(self) -> str:
        # 모델 저장 경로 수정 
        return os.path.join(self.output_dir, 'emotion_model_6class_oversampled')

# --- 2. 커스텀 클래스 및 함수 ---
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

# --- 3. 데이터 로더 ---

def map_ecode_to_6class(e_code_str):
    """E코드("E18")를 6-Class("분노")로 매핑하는 함수"""
    if not isinstance(e_code_str, str) or not e_code_str.startswith('E'): return None
    try: code_num = int(e_code_str[1:]) 
    except (ValueError, TypeError): return None
    
    if 10 <= code_num <= 19: return '분노'
    elif 20 <= code_num <= 29: return '슬픔'
    elif 30 <= code_num <= 39: return '불안'
    elif 40 <= code_num <= 49: return '상처'
    elif 50 <= code_num <= 59: return '당황'
    elif 60 <= code_num <= 69: return '기쁨'
    else: return None

def load_and_process(text_file, label_file, data_dir):
    """Excel(텍스트)과 JSON(라벨)을 병합하고 전처리하는 헬퍼 함수"""
    text_path = os.path.join(data_dir, text_file)
    label_path = os.path.join(data_dir, label_file)
    try:
        df_text = pd.read_excel(text_path, header=None)
        with open(label_path, 'r', encoding='utf-8') as f:
            labels_raw = json.load(f)
    except FileNotFoundError as e:
        print(f"오류: 필수 파일을 찾을 수 없습니다: {e}")
        return pd.DataFrame()
    
    e_codes = []
    for dialogue in labels_raw:
        try: e_codes.append(dialogue['profile']['emotion']['type']) # "E18"
        except KeyError: e_codes.append(None)
    
    if len(df_text) != len(e_codes):
        min_len = min(len(df_text), len(e_codes))
        print(f"경고: {text_file}과 {label_file} 줄 수 불일치. {min_len}개로 축소합니다.")
        df_text = df_text.iloc[:min_len]
        e_codes = e_codes[:min_len]
        
    df_labels = pd.DataFrame({'e_code': e_codes})
    df_combined = pd.concat([df_text, df_labels], axis=1)
    
    dialogue_cols = [8, 9, 10, 11]
    for col in dialogue_cols:
        df_combined[col] = df_combined[col].astype(str).fillna('')
    df_combined['text'] = df_combined[dialogue_cols].apply(lambda row: ' '.join(row), axis=1)

    df_combined['cleaned_text'] = df_combined['text'].apply(clean_text)
    
    df_combined['major_emotion'] = df_combined['e_code'].apply(map_ecode_to_6class)
    
    df_combined.dropna(subset=['major_emotion', 'cleaned_text'], inplace=True)
    df_combined = df_combined[df_combined['cleaned_text'].str.strip() != '']
    
    return df_combined

def get_data(config: TrainingConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Train/Val/Test 3-Set을 로드하고, Train Set에 Oversampling을 적용
    """
    if config.mode != 'emotion':
        print("이 스크립트는 'emotion' 모드 전용입니다.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    print("--- 감정 데이터 로딩 (Train/Validation/Test) ---")
    
    df_full_train = load_and_process("training-origin.xlsx", "training-label.json", config.data_dir)
    df_test = load_and_process("validation-origin.xlsx", "test.json", config.data_dir)
    
    if df_full_train.empty or df_test.empty:
        print("오류: 데이터 로딩 실패.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    print(f"Full Train data loaded: {len(df_full_train)} rows")
    print(f"Test data loaded: {len(df_test)} rows")

    print("Splitting Full Train into New Train (90%) and New Validation (10%)...")
    df_train, df_val = train_test_split(
        df_full_train,
        test_size=0.1,  
        random_state=42, 
        stratify=df_full_train['major_emotion'] 
    )
    
    print("\n--- [Oversampling] New Train 6-Class (원본 분포) ---")
    print(df_train['major_emotion'].value_counts())

    # --- [오버샘플링 시작] ---
    print("\n--- '기쁨' 클래스 오버샘플링 적용 중 ---")
    
    # 1. '기쁨'과 나머지 분리
    df_train_joy = df_train[df_train['major_emotion'] == '기쁨']
    df_train_others = df_train[df_train['major_emotion'] != '기쁨']
    
    # 2. '기쁨'을 제외한 5개 클래스의 평균 개수 계산
    target_count = int(df_train_others['major_emotion'].value_counts().mean())
    print(f"  '기쁨' 원본: {len(df_train_joy)}개")
    print(f"  다른 클래스 평균(타겟): {target_count}개")
    
    # 3. '기쁨'을 타겟 개수만큼 복제 (with replacement)
    df_joy_oversampled = resample(
        df_train_joy,
        replace=True,
        n_samples=target_count, # 타겟 개수
        random_state=42
    )
    
    # 4. 나머지 데이터와 복제된 '기쁨' 데이터를 다시 합침
    df_train = pd.concat([df_train_others, df_joy_oversampled])
    
    # 5. 데이터셋을 다시 섞어줌
    df_train = df_train.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- [Oversampling] New Train 6-Class (최종 분포) ---")
    print(df_train['major_emotion'].value_counts())
    # --- [오버샘플링 끝] ---
    
    print(f"\nNew Train set (Oversampled) size: {len(df_train)}")
    print(f"New Validation set (Original) size: {len(df_val)}")
    
    return df_train, df_val, df_test

# --- 4. 메인 실행 함수 ---
def run_training():
    config = TrainingConfig()
    
    df_train, df_val, df_test = get_data(config)
    
    if df_train.empty or df_val.empty or df_test.empty:
        print("\n오류: 데이터가 비어있어 훈련을 중단합니다.")
        return

    text_column = 'cleaned_text'
    label_column_str = 'major_emotion' 
    
    model_name_to_load = config.get_model_name()
    tokenizer = AutoTokenizer.from_pretrained(model_name_to_load)

    unique_labels = sorted(df_train[label_column_str].unique())
    label_to_id = {label: i for i, label in enumerate(unique_labels)}
    id_to_label = {i: label for label, i in label_to_id.items()}
    
    print(f"\n라벨 인코딩 맵 (6-Class): {label_to_id}")
    
    df_train['label'] = df_train[label_column_str].map(label_to_id)
    df_val['label'] = df_val[label_column_str].map(label_to_id) 
    df_test['label'] = df_test[label_column_str].map(label_to_id)

    print("데이터셋 토크나이징 중...")
    train_encodings = tokenizer(list(df_train[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    val_encodings = tokenizer(list(df_val[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    test_encodings = tokenizer(list(df_test[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    
    train_dataset = EmotionDataset(train_encodings, df_train['label'].tolist())
    val_dataset = EmotionDataset(val_encodings, df_val['label'].tolist())
    test_dataset = EmotionDataset(test_encodings, df_test['label'].tolist())
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    
    print("모델 로딩 중...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name_to_load,
        num_labels=len(unique_labels),
        id2label=id_to_label,
        label2id=label_to_id,
        ignore_mismatched_sizes=True 
    ).to(device)

    output_dir = config.get_output_dir()
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.train_batch_size,
        per_device_eval_batch_size=config.eval_batch_size,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        eval_strategy="epoch",      
        save_strategy="epoch",
        load_best_model_at_end=True,     
        metric_for_best_model="accuracy", 
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,      
        compute_metrics=compute_metrics
    )
    
    print(f"\n 6-Class (Oversampled) 모델 훈련을 시작합니다...")
    trainer.train()
    print("\n 모델 훈련 완료!")

    final_model_path = os.path.join(output_dir, "best_model")
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"최종 모델(Best)과 토크나이저가 {final_model_path} 경로에 저장되었습니다.")
    
    print("\n--- (1) Validation Set 평가 (모의고사) ---")
    val_results = trainer.evaluate(eval_dataset=val_dataset)
    print(f"최종 Validation 평가 결과: {val_results}")
    
    results_path = os.path.join(output_dir, "validation_evaluation_results.json")
    with open(results_path, "w", encoding='utf-8') as f:
        json.dump(val_results, f, indent=4, ensure_ascii=False)
    print(f"Validation 평가 결과가 {results_path}에 저장되었습니다.")

    print("\n--- (2) Test Set 최종 평가 (수능) ---")
    test_predictions = trainer.predict(test_dataset)
    test_metrics = test_predictions.metrics
    print(f"최종 Test 평가 결과: {test_metrics}")

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
        plt.title('Confusion Matrix (TEST Set - 6-Class Oversampled)')
        
        cm_path = os.path.join(output_dir, "TEST_confusion_matrix.png")
        plt.savefig(cm_path)
        print(f"Test Set 혼동 행렬이 {cm_path}에 저장되었습니다.")
    except Exception as e:
        print(f"\n!!! 오류: 혼동 행렬 생성 실패: {e} !!!")
        print("matplotlib, seaborn 라이브러리가 설치되었는지 확인하세요.")

if __name__ == "__main__":
    print("--- 6-Class (Oversampling) 감정 분류 모델 학습 시작 ---")
    run_training()