# 파일 이름: train_final_v2.py
# 
# [v2 변경 사항]
# 1. 훈련/검증/테스트 데이터 분리 (90% / 10% / 기존 검증셋)
# 2. 'cosine' 학습률 스케줄러 적용
# 3. '수동 클래스 가중치' 적용 (TODO 섹션 확인)

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
from sklearn.model_selection import train_test_split # 데이터 분리
from sklearn.utils import class_weight
from torch.nn import CrossEntropyLoss
from typing import Dict, List, Tuple
from dataclasses import dataclass
import platform
import matplotlib.pyplot as plt
import seaborn as sns

# --- Matplotlib 한글 폰트 설정 (로컬 PC용) ---
try:
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # Mac OS
        plt.rc('font', family='AppleGothic')
    else: # Linux (코랩 등)
        plt.rc('font', family='NanumBarunGothic')
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("한글 폰트 설정에 실패했습니다. 혼동 행렬의 라벨이 깨질 수 있습니다.")


# --- 1. 설정부 ---
@dataclass
class TrainingConfig:
    mode: str = "emotion" 
    data_dir: str = "./data"
    output_dir: str = "./results"
    base_model_name: str = "klue/roberta-base"
    eval_batch_size: int = 64
    num_train_epochs: int = 10
    learning_rate: float = 1e-5
    train_batch_size: int = 16
    weight_decay: float = 0.01
    max_length: int = 128
    warmup_ratio: float = 0.1
    
    def get_model_name(self) -> str:
        # 감정 모드일 땐 항상 klue/roberta-base 원본을 사용
        return self.base_model_name
        
    def get_output_dir(self) -> str:
        # v2 모델 저장 경로
        return os.path.join(self.output_dir, 'emotion_model_v2_manual')

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

class CustomTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.loss_fct = CrossEntropyLoss(weight=class_weights)
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss = self.loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    return {'accuracy': acc, 'f1': f1}

def clean_text(text: str) -> str:
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', str(text))

# --- 3. 데이터 로더 ([변경] Train/Val/Test 분리) ---
def get_data(config: TrainingConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if config.mode == 'nsmc':
      raise ValueError("이 스크립트는 'emotion' 모드 전용입니다.")

    elif config.mode == 'emotion':
        print("--- 감정 데이터 로딩 (Train/Val/Test 분리) ---")
        
        # (내부 함수) JSON 파일 로드 및 라벨 매핑
        def load_and_map_labels(file_name):
            def map_ecode_to_major_emotion(ecode):
                try: code_num = int(ecode[1:])
                except: return None
                
                if 10 <= code_num <= 19: return '분노'
                elif 20 <= code_num <= 29: return '슬픔'
                elif 30 <= code_num <= 39: return '불안'
                elif 40 <= code_num <= 49: return '상처'
                elif 50 <= code_num <= 59: return '당황'
                elif 60 <= code_num <= 69: return '기쁨'
                else: return None

            with open(os.path.join(config.data_dir, file_name), 'r', encoding='utf-8') as f:
                raw = json.load(f)
            data = [{'text': " ".join(d['talk']['content'].values()), 'emotion': d['profile']['emotion']['type']} for d in raw]
            df = pd.DataFrame(data)
            df['major_emotion'] = df['emotion'].apply(map_ecode_to_major_emotion)
            df.dropna(subset=['major_emotion'], inplace=True)
            df['cleaned_text'] = df['text'].apply(clean_text)
            return df
        
        # 1. Test Set 로드 (기존 validation-label.json 사용)
        df_test = load_and_map_labels("test.json")
        
        # 2. Train Set 로드 (기존 training-label.json 사용)
        df_train_full = load_and_map_labels("training-label.json")
        
        # 3. Train Set을 9:1로 분리 (신규 Train / 신규 Validation)
        label_column_str = 'major_emotion'
        
        df_train, df_val = train_test_split(
            df_train_full,
            test_size=0.1,  # 10%를 Validation으로 사용
            random_state=42, # 결과 재현을 위해 고정
            stratify=df_train_full[label_column_str] # 클래스 비율을 유지하며 분리
        )
        
        print(f"  총 원본 훈련 데이터: {len(df_train_full)}개")
        print(f"  [신규] 훈련(Train)용: {len(df_train)}개 (90%)")
        print(f"  [신규] 검증(Validation)용: {len(df_val)}개 (10%)")
        print(f"  [최종] 테스트(Test)용: {len(df_test)}개 ")
        
        return df_train, df_val, df_test
    else:
        raise ValueError(f"지원하지 않는 모드입니다: {config.mode}")

# --- 4. 메인 실행 함수 ---
def run_training():
    config = TrainingConfig()
    
    # 1. 데이터 준비 (3개 세트를 받음)
    df_train, df_val, df_test = get_data(config)
    
    text_column = 'cleaned_text'
    label_column_str = 'major_emotion'
    
    # 2. 토크나이저 및 라벨 인코딩
    tokenizer = AutoTokenizer.from_pretrained(config.get_model_name())

    # [중요] 라벨 순서는 '신규 훈련 데이터(df_train)' 기준으로 생성
    unique_labels = sorted(df_train[label_column_str].unique())
    label_to_id = {label: i for i, label in enumerate(unique_labels)}
    id_to_label = {i: label for label, i in label_to_id.items()}
    
    print("\n--- 생성된 라벨 순서 (0~5) ---")
    print(unique_labels) # ['기쁨', '당황', '분노', '불안', '상처', '슬픔']
    print("------------------------------")

    df_train['label'] = df_train[label_column_str].map(label_to_id)
    df_val['label'] = df_val[label_column_str].map(label_to_id)
    df_test['label'] = df_test[label_column_str].map(label_to_id)

    # 3. 데이터셋 생성 및 클래스 가중치 계산
    train_encodings = tokenizer(list(df_train[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    val_encodings = tokenizer(list(df_val[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    
    train_dataset = EmotionDataset(train_encodings, df_train['label'].tolist())
    val_dataset = EmotionDataset(val_encodings, df_val['label'].tolist())
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    # 클래스 가중치 계산 (신규 훈련 데이터 기준)
    manual_weights_list = [6.00, 4.50, 0.85, 1.80, 1.80, 0.92] 
    class_weights = torch.tensor(manual_weights_list, dtype=torch.float).to(device)
    
    print(f"--- 수동 적용된 클래스 가중치 ---")
    print(f"{class_weights.tolist()}")
    print(f"---------------------------------")


    # 4. 모델 로딩
    model = AutoModelForSequenceClassification.from_pretrained(
        config.get_model_name(),
        num_labels=len(unique_labels),
        id2label=id_to_label,
        label2id=label_to_id,
        ignore_mismatched_sizes=True 
    ).to(device)

    # 5. 훈련 실행
    training_args = TrainingArguments(
        output_dir=config.get_output_dir(),
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
        lr_scheduler_type="cosine",  
        report_to="none"
    )

    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,      
        compute_metrics=compute_metrics,
        class_weights=class_weights
    )
    
    print(f"\n '[신규 분리 데이터]'로 모델 훈련을 시작합니다...")
    trainer.train()
    print("\n 모델 훈련 완료!")

    output_dir = config.get_output_dir()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"최종 모델과 토크나이저가 {output_dir} 경로에 저장되었습니다.")
    
    # 훈련 중 사용한 검증 데이터(10%)에 대한 평가 결과
    print("\n--- 신규 Validation Set(10%) 평가 결과 (참고용) ---")
    results = trainer.evaluate() # 기본값 (eval_dataset)
    print(results)

    # --- [핵심 변경] 최종 Test Set으로 '진짜 성능' 평가 ---
    print("\n" + "="*50)
    print("--- 최종 Test Set으로 '진짜 성능' 평가 시작 ---")
    print("="*50)
    
    # Test Set을 위한 데이터셋 생성
    test_encodings = tokenizer(list(df_test[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    test_dataset = EmotionDataset(test_encodings, df_test['label'].tolist())

    # trainer.predict()를 사용하여 Test Set에 대한 예측 수행
    test_predictions = trainer.predict(test_dataset)
    
    # compute_metrics 함수를 재사용하여 '진짜 성능' 계산
    final_metrics = compute_metrics(test_predictions)
    
    print(f"*** 최종 Test Set '진짜' 성능 결과 ***")
    print(f"  - 최종 Accuracy: {final_metrics['accuracy']:.4f}")
    print(f"  - 최종 F1-Score (Weighted): {final_metrics['f1']:.4f}")
    print("="*50)

    results_path = os.path.join(output_dir, "final_test_results.json")
    with open(results_path, "w", encoding='utf-8') as f:
        json.dump(final_metrics, f, indent=4, ensure_ascii=False)
    print(f"최종 테스트 결과가 {results_path}에 저장되었습니다.")

    # --- Test Set 기준 혼동 행렬 생성 ---
    print("\n--- Test Set 기준 혼동 행렬 생성 ---")
    y_pred = test_predictions.predictions.argmax(-1)
    y_true = test_predictions.label_ids

    labels = [id_to_label[i] for i in sorted(id_to_label.keys())]
    cm = confusion_matrix(y_true, y_pred, labels=[label_to_id[l] for l in labels])
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('예측 라벨 (Predicted Label)')
    plt.ylabel('실제 라벨 (True Label)')
    plt.title('Test Set Confusion Matrix')
    
    cm_path = os.path.join(output_dir, "final_test_confusion_matrix.png")
    plt.savefig(cm_path)
    print(f"최종 혼동 행렬이 {cm_path}에 저장되었습니다.")

if __name__ == "__main__":
    run_training()