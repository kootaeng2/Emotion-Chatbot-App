document.addEventListener('DOMContentLoaded', function () {
    // --- DOM 요소 가져오기 ---
    const diaryTextarea = document.getElementById('diary');
    const submitBtn = document.getElementById('submit-btn');
    const resultContainer = document.getElementById('result-container');
    const resultDiv = document.getElementById('result');
    const saveStatus = document.getElementById('save-status');
    const saveBtnContainer = document.getElementById('save-action-container');
    const saveDiaryBtn = document.getElementById('final-save-btn');
    const diaryBook = document.querySelector('.diary-book');
    const leftPage = diaryBook.querySelector('.left-page');
    const rightPage = diaryBook.querySelector('.right-page');


    // --- 상태 변수 ---
    let currentEmotion = null;
    let currentCandidates = [];
    let progressInterval = null;
    let diaryText = ''; // 일기 내용을 저장할 변수

    // --- [유틸리티] 추천 내용 파싱 함수 ---
    function parseRecommendation(text) {
        const contents = { acceptance: '', diversion: '' };
        if (!text) return contents;
        const regex = /#+\s*\[\s*(수용|전환)\s*\]([\s\S]*?)(?=(?:#+\s*\[\s*(?:수용|전환)\s*\])|$)/gi;
        let match;
        while ((match = regex.exec(text)) !== null) {
            const type = match[1].trim();
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
        if (!currentEmotion && candidates.length > 0) {
            currentEmotion = candidates[0].emotion;
        }
        const { acceptance, diversion } = parseRecommendation(recommendation);
        let chipsHTML = '';
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
        if (saveBtnContainer) {
            saveBtnContainer.style.display = 'flex';
        }
        resultDiv.querySelectorAll('.emotion-chip').forEach(chip => {
            chip.addEventListener('click', handleChipClick);
        });
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
    
    async function handleChipClick(event) {
        const selectedChip = event.currentTarget;
        const selectedEmotion = selectedChip.dataset.emotion;
        if (currentEmotion === selectedEmotion) return;
        currentEmotion = selectedEmotion;
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
                renderFullResult({
                    recommendation: data.recommendation,
                    candidates: currentCandidates, 
                    top_score: 0
                });
            }
        } catch (error) {
            console.error('Error:', error);
            stopLoader();
            resultDiv.innerHTML = '<p style="color: red;">서버 오류가 발생했습니다.</p>';
        }
    }

    async function handleDiarySubmission() {
        diaryText = diaryTextarea.value.trim();
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
            currentEmotion = data.top_emotion;
            currentCandidates = data.candidates;
            renderFullResult(data);
        } catch (error) {
            console.error('Error:', error);
            stopLoader();
            resultDiv.innerHTML = '<p style="color: red;">처리 중 서버 오류가 발생했습니다.</p>';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '다시 분석하기';
        }
    }

    const emotionColors = {
        '기쁨': '#FFD700', '슬픔': '#4682B4', '분노': '#B22222',
        '불안': '#8A2BE2', '당황': '#FF8C00', '상처': '#2E8B57'
    };

    function playFullAnimation(element, orbColor, duration) {
        const keyframes = [
            { top: 'calc(50vh - 25px)', left: 'calc(50vw - 25px)', transform: 'scale(1)', offset: 0 },
            { top: 'calc(100vh - 80px)', left: 'calc(50vw - 25px)', transform: 'scale(1.2, 0.8)', offset: 0.1 },
            { top: '60vh', left: '58vw', transform: 'scale(1, 1)', offset: 0.25 },
            { top: 'calc(100vh - 80px)', left: '68vw', transform: 'scale(1.15, 0.85)', offset: 0.40 },
            { top: '75vh', left: '76vw', transform: 'scale(1, 1)', offset: 0.55 },
            { top: 'calc(100vh - 80px)', left: '83vw', transform: 'scale(1.1, 0.9)', offset: 0.65 },
            { top: '85vh', left: '89vw', transform: 'scale(1, 1)', offset: 0.75 },
            { top: 'calc(100vh - 80px)', left: '94vw', transform: 'scale(1.05, 0.95)', offset: 0.85 },
            { top: '90vh', left: '96.5vw', transform: 'scale(1, 1)', offset: 0.92 },
            { top: 'calc(100vh - 80px)', left: '98vw', transform: 'scale(1.02, 0.98)', offset: 0.96 },
            { top: 'calc(100vh - 80px)', left: 'calc(100vw - 80px)', transform: 'scale(1, 1)', offset: 1 }
        ];
        const options = { duration: duration, easing: 'ease-in-out', fill: 'forwards' };
        return element.animate(keyframes, options);
    }

    async function handleDiarySave() {
        if (!diaryBook) return;
        if (document.querySelector('.js-animating')) return;

        if (saveDiaryBtn) saveDiaryBtn.disabled = true;
        saveStatus.textContent = '기억을 저장하는 중...';

        const formData = new FormData();
        formData.append('diary', diaryText);
        formData.append('emotion', currentEmotion);
        fetch('/diary/save', {
            method: 'POST',
            body: formData
        }).then(response => response.json()).then(data => {
            if (data.error) {
                 saveStatus.innerHTML = `<span style="color: red;">저장 실패: ${data.error}</span>`;
            }
        }).catch(err => {
            saveStatus.innerHTML = `<span style="color: red;">저장 중 오류 발생</span>`;
            console.error(err);
        });

        const bookFoldDuration = 1500;
        const bounceDuration = 5000;
        const emotionKey = (currentEmotion || '기쁨').split(' ')[0];
        const orbColor = emotionColors[emotionKey] || '#a1c4fd';

        const animElement = document.createElement('div');
        animElement.classList.add('js-animating-orb');
        animElement.style.position = 'fixed';
        animElement.style.zIndex = '9999';
        animElement.style.width = '50px';
        animElement.style.height = '50px';
        animElement.style.borderRadius = '50%';
        animElement.style.background = `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.5), ${orbColor} 80%)`;
        animElement.style.boxShadow = `0 0 35px ${orbColor}, inset 3px 3px 8px rgba(0,0,0,0.4), inset -3px -3px 8px rgba(255,255,255,0.7)`;
        animElement.style.top = 'calc(50vh - 25px)';
        animElement.style.left = 'calc(50vw - 25px)';
        animElement.style.opacity = '0';
        animElement.style.transform = 'scale(0)';
        document.body.appendChild(animElement);

        diaryBook.classList.add('js-animating');
        const bookRect = diaryBook.getBoundingClientRect();
        const translateX = (window.innerWidth / 2) - (bookRect.left + bookRect.width / 2);
        const translateY = (window.innerHeight / 2) - (bookRect.top + bookRect.height / 2);

        const bookToOrbKeyframes = [
            { transform: 'translate(0, 0) scale(1)', opacity: 1, backgroundColor: '#fdfbf7', borderRadius: '20px' },
            { backgroundColor: orbColor, borderRadius: '50%', offset: 0.7 },
            { transform: `translate(${translateX}px, ${translateY}px) scale(0)`, opacity: 0, backgroundColor: orbColor, borderRadius: '50%' }
        ];
        const animOptions = { duration: bookFoldDuration, easing: 'ease-in-out', fill: 'forwards' };
        const bookAnimation = diaryBook.animate(bookToOrbKeyframes, animOptions);

        const orbAppearKeyframes = [
            { transform: 'scale(0)', opacity: 0 },
            { transform: 'scale(1)', opacity: 1, offset: 0.8 },
            { transform: 'scale(1)', opacity: 1 }
        ];
        animElement.animate(orbAppearKeyframes, { duration: bookFoldDuration, easing: 'ease-out', fill: 'forwards' });

        bookAnimation.onfinish = () => {
            diaryBook.style.visibility = 'hidden';
            const bounceAnimation = playFullAnimation(animElement, orbColor, bounceDuration);
            bounceAnimation.onfinish = () => {
                if (document.body.contains(animElement)) document.body.removeChild(animElement);
                window.location.href = '/my_diary';
            };
        };
    }

    // --- 초기화 실행 ---
    if(diaryTextarea) diaryTextarea.addEventListener('input', updateButtonState);
    if(submitBtn) submitBtn.addEventListener('click', handleDiarySubmission);
    if(saveDiaryBtn) saveDiaryBtn.addEventListener('click', handleDiarySave);

    if(diaryTextarea) updateButtonState();
});
