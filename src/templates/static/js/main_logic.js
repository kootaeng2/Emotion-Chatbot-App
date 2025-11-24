document.addEventListener('DOMContentLoaded', function () {
    // --- DOM 요소 가져오기 ---
    const diaryTextarea = document.getElementById('diary');
    const submitBtn = document.getElementById('submit-btn');
    const resultContainer = document.getElementById('result-container');
    const resultDiv = document.getElementById('result');
    const saveStatus = document.getElementById('save-status');
    const saveBtnContainer = document.getElementById('save-action-container');
    const saveDiaryBtn = document.getElementById('final-save-btn');

    // --- 상태 변수 ---
    let currentEmotion = null;
    let currentCandidates = [];
    let progressInterval = null;
    let diaryText = ''; // 일기 내용을 저장할 변수

    // --- [유틸리티] 추천 내용 파싱 함수 ---
    function parseRecommendation(text) {
        const contents = { acceptance: '', diversion: '' };
        if (!text) return contents;

        // 정규표현식: ## [수용] 또는 ## [전환] 태그 사이의 내용 추출
        const regex = /#+\s*\[\s*(수용|전환)\s*\]([\s\S]*?)(?=(?:#+\s*\[\s*(?:수용|전환)\s*\])|$)/gi;
        
        let match;
        while ((match = regex.exec(text)) !== null) {
            const type = match[1].trim(); // '수용' 또는 '전환'
            const content = match[2].trim();
            
            if (type === '수용') contents.acceptance = content;
            else if (type === '전환') contents.diversion = content;
        }
        return contents;
    }

    // --- [유틸리티] 로딩 바 표시 ---
    function showLoader(message) {
        resultDiv.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <p class="loading-text" style="margin-bottom: 10px; color: #666;">${message}</p>
                <div class="progress-bar-container" style="width: 100%; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; height: 8px;">
                    <div class="progress-bar" style="width: 0%; height: 100%; background-color: var(--primary-color, #6598e5); transition: width 0.1s;"></div>
                </div>
            </div>
        `;
        
        if (progressInterval) clearInterval(progressInterval);
        
        const bar = resultDiv.querySelector('.progress-bar');
        let width = 0;
        progressInterval = setInterval(() => {
            if (width < 95) {
                width += 1; 
                if(bar) bar.style.width = width + '%';
            }
        }, 50);
    }

    // --- [유틸리티] 로딩 바 중지 ---
    function stopLoader() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        const bar = resultDiv.querySelector('.progress-bar');
        if (bar) bar.style.width = '100%';
    }
    
    // --- [핵심] 결과 화면 렌더링 함수 ---
    function renderFullResult(data) {
        stopLoader();
        
        const recommendation = data.recommendation || '';
        const candidates = data.candidates || [];
        
        // 현재 감정이 없으면 1순위 감정으로 설정
        if (!currentEmotion && candidates.length > 0) {
            currentEmotion = candidates[0].emotion;
        }

        // 1. 추천 내용 파싱 (함수 내부에서 처리하여 에러 방지)
        const { acceptance, diversion } = parseRecommendation(recommendation);

        // 2. 감정 칩(선택지) 생성
        let chipsHTML = '';
        // 확신도가 낮거나(0.8 미만) 이미 후보가 있는 경우 칩 표시
        const showChips = (data.top_score < 0.8) || (candidates.length > 0); 

        if (showChips) {
             chipsHTML = `<div class="emotion-chips" style="display: flex; gap: 10px; justify-content: center; margin-bottom: 20px;">`;
             candidates.forEach(candidate => {
                const isActive = candidate.emotion === currentEmotion;
                chipsHTML += `
                    <button class="emotion-chip ${isActive ? 'active' : ''}" data-emotion="${candidate.emotion}">
                        ${candidate.emoji} ${candidate.emotion} 
                        <span class="score-badge">${Math.round(candidate.score*100)}%</span>
                    </button>
                `;
             });
             chipsHTML += `</div>`;
        }

        // 3. 전체 HTML 조립
        const contentHTML = `
            ${chipsHTML}
            <div class="rec-tabs">
                <button class="rec-tab-btn active" data-tab="acceptance">수용</button>
                <button class="rec-tab-btn" data-tab="diversion">전환</button>
            </div>
            <div id="rec-acceptance" class="rec-content active">
                ${marked.parse(acceptance || '추천 내용을 불러오지 못했습니다.')}
            </div>
            <div id="rec-diversion" class="rec-content">
                ${marked.parse(diversion || '추천 내용을 불러오지 못했습니다.')}
            </div>
        `;
        
        resultDiv.innerHTML = contentHTML;

        // 저장 버튼 표시
        if (saveBtnContainer) {
            saveBtnContainer.style.display = 'flex'; // flex로 변경 (CSS 정렬 따름)
        }
        
        // 감정 칩 클릭 이벤트 연결
        resultDiv.querySelectorAll('.emotion-chip').forEach(chip => {
            chip.addEventListener('click', handleChipClick);
        });

        // 탭 전환 이벤트 연결
        resultDiv.querySelectorAll('.rec-tab-btn').forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                resultDiv.querySelectorAll('.rec-tab-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                resultDiv.querySelectorAll('.rec-content').forEach(content => content.classList.remove('active'));
                resultDiv.querySelector(`#rec-${tab}`).classList.add('active');
            });
        });
    }
    
    // --- [이벤트 핸들러] ---

    function updateButtonState() {
        if(diaryTextarea && submitBtn) {
            submitBtn.disabled = diaryTextarea.value.trim() === '';
        }
    }
    
    // 감정 칩 클릭 시: 새로운 추천 받아오기
    async function handleChipClick(event) {
        const selectedChip = event.currentTarget;
        const selectedEmotion = selectedChip.dataset.emotion;

        if (currentEmotion === selectedEmotion) return;
        currentEmotion = selectedEmotion;

        // UI 즉시 업데이트 (활성 상태 변경)
        resultDiv.querySelectorAll('.emotion-chip').forEach(chip => {
            chip.classList.toggle('active', chip.dataset.emotion === selectedEmotion);
        });

        showLoader('새로운 추천을 생성하는 중입니다...');

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    diary: diaryTextarea.value.trim(), 
                    emotion: selectedEmotion 
                })
            });
            const data = await response.json();
            
            if (data.error) {
                stopLoader();
                resultDiv.innerHTML = `<p style="color: red;">오류: ${data.error}</p>`;
            } else {
                // 화면 갱신 (기존 후보군은 유지)
                renderFullResult({
                    recommendation: data.recommendation,
                    candidates: currentCandidates, 
                    top_score: 0 // 칩을 계속 보여주기 위해 0으로 설정
                });
            }
        } catch (error) {
            console.error('Error:', error);
            stopLoader();
            resultDiv.innerHTML = '<p style="color: red;">서버 오류가 발생했습니다.</p>';
        }
    }

    // 분석 버튼 클릭 시
    async function handleDiarySubmission() {
        diaryText = diaryTextarea.value.trim(); // 상위 스코프의 diaryText에 할당
        if (!diaryText) return;

        submitBtn.disabled = true;
        submitBtn.textContent = '분석 중...';
        
        if(saveBtnContainer) saveBtnContainer.style.display = 'none'; 

        saveStatus.textContent = '';
        showLoader('감정을 분석하고 추천을 생성하는 중입니다...');
        
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ diary: diaryText })
            });
            const data = await response.json();
            
            if (data.error) {
                stopLoader();
                resultDiv.innerHTML = `<p style="color: red;">오류: ${data.error}</p>`;
                return;
            }
            
            // 상태 업데이트 및 렌더링
            currentEmotion = data.top_emotion;
            currentCandidates = data.candidates;
            
            renderFullResult(data); // 이제 인자 하나만 넘기면 됩니다!

        } catch (error) {
            console.error('Error:', error);
            stopLoader();
            resultDiv.innerHTML = '<p style="color: red;">처리 중 서버 오류가 발생했습니다.</p>';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '다시 분석하기';
        }
    }
    // 감정별 구슬 색상 매핑
    const emotionColors = {
    '기쁨': '#FFD700', // 금색 (더 진한 노랑)
    '슬픔': '#4682B4', // 스틸블루 (더 진한 파랑)
    '분노': '#B22222', // 파이어브릭 (더 진한 빨강)
    '불안': '#8A2BE2', // 블루 바이올렛 (더 진한 보라)
    '당황': '#FF8C00', // 다크 오렌지 (더 진한 주황)
    '상처': '#2E8B57'  // 시 그린 (더 진한 초록)
};

    async function handleDiarySave() {
        const diaryBook = document.querySelector('.diary-book');
        if (!diaryBook) return;

        // 1. UI 업데이트 및 저장 요청 시작
        if (saveDiaryBtn) saveDiaryBtn.disabled = true;
        saveStatus.textContent = '기억을 저장하는 중...';

        const formData = new FormData();
        formData.append('diary', diaryText);
        formData.append('emotion', currentEmotion);
        fetch('/diary/save', {
            method: 'POST',
            body: formData
        }).then(response => response.json()).then(data => {
            if (!data.success) saveStatus.innerHTML = `<span style="color: red;">저장 실패: ${data.error}</span>`;
        }).catch(err => {
            saveStatus.innerHTML = `<span style="color: red;">저장 중 오류 발생</span>`;
            console.error(err);
        });

        // 2. 애니메이션을 위한 클론(복제) 요소 생성
        const rect = diaryBook.getBoundingClientRect();
        const clone = document.createElement('div');
        clone.style.position = 'fixed';
        clone.style.top = `${rect.top}px`;
        clone.style.left = `${rect.left}px`;
        clone.style.width = `${rect.width}px`;
        clone.style.height = `${rect.height}px`;
        clone.style.backgroundColor = '#fdfbf7'; // 원본 책 배경색
        clone.style.boxShadow = '0 30px 60px rgba(0,0,0,0.15), 0 0 0 12px #5d4037'; // 원본 책 그림자
        clone.style.borderRadius = '20px';
        clone.style.zIndex = '9999'; // 최상단에 위치

        // 감정 색상 설정
        const emotionKey = (currentEmotion || '').split(' ')[0];
        const orbColor = emotionColors[emotionKey] || '#a1c4fd';
        clone.style.setProperty('--orb-color', orbColor);
        
        document.body.appendChild(clone);

        // 3. 원본 숨기고 클론에 애니메이션 적용
        diaryBook.style.visibility = 'hidden';
        clone.classList.add('crumple-animation');

        // 4. 애니메이션 종료 후 정리 및 UI 초기화
        setTimeout(() => {                                                                                                                                                                 
            document.body.removeChild(clone); // 복제본 제거
            diaryBook.style.visibility = 'visible'; // 원래 책 다시 표시

            // 내부 UI 초기화
            diaryTextarea.value = '';
            resultDiv.innerHTML = `<div class="empty-state"><p>왼쪽 페이지에<br>분석할 일기를<br>작성해주세요.</p></div>`;
            if (saveBtnContainer) saveBtnContainer.style.display = 'none';
            saveStatus.textContent = '저장 완료! 새로운 일기를 기록해보세요.';

            updateButtonState();
            if (saveDiaryBtn) saveDiaryBtn.disabled = false;
        }, 7000); // 7초 애니메이션 시간과 일치
    }

    // --- 초기화 실행 ---
    if(diaryTextarea) diaryTextarea.addEventListener('input', updateButtonState);
    if(submitBtn) submitBtn.addEventListener('click', handleDiarySubmission);
    if(saveDiaryBtn) saveDiaryBtn.addEventListener('click', handleDiarySave);

    if(diaryTextarea) updateButtonState();
});