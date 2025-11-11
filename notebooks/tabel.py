import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# --- Matplotlib 한글 폰트 설정 ---
try:
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # Mac OS
        plt.rc('font', family='AppleGothic')
    else: # Linux (코랩 등)
        # Colab 등에서 실행 시, 먼저 !sudo apt-get install -y fonts-nanum 실행 필요
        plt.rc('font', family='NanumBarunGothic')
    
    plt.rcParams['axes.unicode_minus'] = False
    print("한글 폰트가 설정되었습니다.")
except Exception as e:
    print(f"한글 폰트 설정에 실패했습니다: {e}")

# --- 1. JSON 파일 로드 및 파싱 ---
# [변경] v2 훈련의 trainer_state.json 경로로 수정
file_path = r'E:\Emotion\results\emotion_model_v2_manual\checkpoint-29050\trainer_state.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    log_history = data.get('log_history', [])
    
    # 학습 로그와 평가 로그 분리
    train_logs = []
    eval_logs = []
    
    for item in log_history:
        if 'eval_loss' in item:
            eval_logs.append(item)
        elif 'loss' in item:
            train_logs.append(item)
            
    if not eval_logs:
        print("파일에서 평가 로그('eval_loss' 포함)를 찾을 수 없습니다.")
    else:
        # DataFrame으로 변환
        df_train = pd.DataFrame(train_logs).sort_values(by='epoch')
        df_eval = pd.DataFrame(eval_logs).sort_values(by='epoch')

        # --- 2. 최적 모델 정보 찾기 ---
        best_step = data.get('best_global_step')
        best_epoch_log = next((item for item in eval_logs if item['step'] == best_step), None)
        best_epoch = best_epoch_log['epoch'] if best_epoch_log else None

        # --- 3. 그래프 생성 (1행 2열) ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        # --- 3-1. Loss 그래프 (Train vs Validation) ---
        ax1.plot(df_train['epoch'], df_train['loss'], 'o-', label='Train Loss (학습 손실)', alpha=0.7)
        ax1.plot(df_eval['epoch'], df_eval['eval_loss'], 's--', label='Validation Loss (검증 손실)', linewidth=2, markersize=8)
        ax1.set_title('모델 학습 과정 (Loss)', fontsize=16)
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, linestyle=':')
        
        if best_epoch:
            ax1.axvline(x=best_epoch, color='red', linestyle=':', linewidth=2, 
                        label=f'Best Model (Epoch {best_epoch:g})')
            # 최고점 텍스트 추가 (최저 Loss가 아닌 Best Model의 Epoch 기준)
            best_val_loss = next((e['eval_loss'] for e in eval_logs if e['epoch'] == best_epoch), None)
            if best_val_loss:
                ax1.plot(best_epoch, best_val_loss, 'r*', markersize=15) # 최고 지점 마커
                ax1.text(best_epoch, best_val_loss * 1.05, f'Best @ Epoch {best_epoch:g}', 
                         color='red', horizontalalignment='center', fontsize=12)

        # --- 3-2. Metrics 그래프 (Validation Accuracy vs F1-Score) ---
        ax2.plot(df_eval['epoch'], df_eval['eval_accuracy'] * 100, 'o-', 
                 label='Validation Accuracy (검증 정확도)', linewidth=2, markersize=8)
        ax2.plot(df_eval['epoch'], df_eval['eval_f1'] * 100, 's--', 
                 label='Validation F1-Score (검증 F1)', linewidth=2, markersize=8)
        ax2.set_title('모델 평가 지표 (Accuracy & F1-Score)', fontsize=16)
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Score (%)', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, linestyle=':')

        if best_epoch:
            ax2.axvline(x=best_epoch, color='red', linestyle=':', linewidth=2, 
                        label=f'Best Model (Epoch {best_epoch:g})')
            # 최고점 텍스트 추가 (Accuracy 기준)
            best_acc = best_epoch_log['eval_accuracy'] * 100
            ax2.plot(best_epoch, best_acc, 'r*', markersize=15) # 최고 지점 마커
            ax2.text(best_epoch, best_acc * 0.99, f'Best Acc: {best_acc:.2f}%', 
                       color='red', horizontalalignment='center', verticalalignment='top', fontsize=12)

        # 그래프 레이아웃 정리 및 파일로 저장
        plt.tight_layout()
        plt.savefig('training_visualization_graph.png', dpi=300)
        print("\n'training_visualization_graph.png' 파일로 그래프가 저장되었습니다.")

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 경로를 다시 확인해주세요.")
except Exception as e:
    print(f"데이터 처리 중 오류가 발생했습니다: {e}")