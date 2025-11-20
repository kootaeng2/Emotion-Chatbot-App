document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const diaryTextarea = document.getElementById('diary');
    const submitBtn = document.getElementById('submit-btn');
    const resultContainer = document.getElementById('result-container');
    const resultDiv = document.getElementById('result');
    const saveStatus = document.getElementById('save-status');
    const saveBtnContainer = document.querySelector('.save-button-container');
    const saveDiaryBtn = document.getElementById('save-diary-btn');

    // State
    let currentEmotion = null;
    let currentCandidates = [];
    let progressInterval = null;

    // --- UTILITY & RENDER FUNCTIONS ---

    function parseRecommendation(text) {
        const contents = { acceptance: '', diversion: '' };
        const regex = /#+\s*\[(수용|전환)\]([\s\S]*?)(?=#+\s*\[(수용|전환)\]|$)/g;
        let match;
        while ((match = regex.exec(text)) !== null) {
            const key = match[1] === '수용' ? 'acceptance' : 'diversion';
            contents[key] = match[2].trim();
        }
        return contents;
    }

    function showLoader(message) {
        resultDiv.innerHTML = `
            <p class="loading-text">${message}</p>
            <div class="progress-bar-container">
                <div class="progress-bar"></div>
            </div>
        `;
        // Stop any previous interval
        if (progressInterval) clearInterval(progressInterval);
        
        const bar = resultDiv.querySelector('.progress-bar');
        let width = 0;
        progressInterval = setInterval(() => {
            // Animate slowly to 95% and stay there
            if (width < 95) {
                width += 1;
                bar.style.width = width + '%';
            }
        }, 80); // Adjust interval for desired speed
    }

    function stopLoader() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        const bar = resultDiv.querySelector('.progress-bar');
        if (bar) {
            bar.style.width = '100%'; // Complete the bar before disappearing
        }
    }
    
    function renderFullResult(data) {
        stopLoader();
        const { recommendation, candidates } = data;
        const activeEmotion = data.activeEmotion || candidates[0].emotion;
        const activeCandidate = candidates.find(c => c.emotion === activeEmotion) || candidates[0];

        const { acceptance, diversion } = parseRecommendation(recommendation);

        let chipsHTML = '';
        candidates.forEach(candidate => {
            chipsHTML += `
                <button class="emotion-chip ${candidate.emotion === activeEmotion ? 'active' : ''}" data-emotion="${candidate.emotion}">
                    ${candidate.emoji} ${candidate.emotion}
                    <span class="score-badge">${Math.round(candidate.score * 100)}%</span>
                </button>
            `;
        });

        resultDiv.innerHTML = `
            <div class="result-header">
                <div class="result-title">
                    <p style="font-weight: 500; font-size: 1.1rem; margin: 0;">
                        <strong>감정 분석 결과:</strong> ${activeCandidate.emotion} ${activeCandidate.emoji}
                    </p>
                </div>
            </div>
            <div id="emotion-choice-container">
                <div id="emotion-chips">${chipsHTML}</div>
            </div>
            <div class="rec-tabs">
                <button class="rec-tab-btn active" data-tab="acceptance">수용</button>
                <button class="rec-tab-btn" data-tab="diversion">전환</button>
            </div>
            <div id="rec-acceptance" class="rec-content active">
                ${marked.parse(acceptance || '추천을 불러오지 못했습니다.')}
            </div>
            <div id="rec-diversion" class="rec-content">
                ${marked.parse(diversion || '추천을 불러오지 못했습니다.')}
            </div>
        `;
        
        const resultHeader = resultDiv.querySelector('.result-header');
        if (resultHeader) {
            resultHeader.appendChild(saveBtnContainer);
            saveBtnContainer.style.display = 'block';
        }
        
        resultDiv.querySelectorAll('.emotion-chip').forEach(chip => chip.addEventListener('click', handleChipClick));
        resultDiv.querySelectorAll('.rec-tab-btn').forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                resultDiv.querySelectorAll('.rec-tab-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                resultDiv.querySelectorAll('.rec-content').forEach(content => content.classList.remove('active'));
                resultDiv.querySelector(`#rec-${tab}`).classList.add('active');
            });
        });

        const choiceContainer = resultDiv.querySelector('#emotion-choice-container');
        if (choiceContainer && (candidates[0].score < 0.8 || true)) { // Kept true for testing
             choiceContainer.style.display = 'block';
        }
    }
    
    // --- EVENT HANDLERS ---

    function updateButtonState() {
        submitBtn.disabled = diaryTextarea.value.trim() === '';
    }
    
    async function handleChipClick(event) {
        const selectedChip = event.currentTarget;
        const selectedEmotion = selectedChip.dataset.emotion;

        if (currentEmotion === selectedEmotion) return;
        currentEmotion = selectedEmotion;

        const activeCandidate = currentCandidates.find(c => c.emotion === selectedEmotion) || {};

        // Update UI immediately
        resultDiv.querySelector('.result-title p').innerHTML = `<strong>감정 분석 결과:</strong> ${activeCandidate.emotion} ${activeCandidate.emoji}`;
        resultDiv.querySelectorAll('.emotion-chip').forEach(chip => {
            chip.classList.toggle('active', chip.dataset.emotion === selectedEmotion);
        });

        showLoader('새로운 추천을 생성하는 중입니다...');

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ diary: diaryTextarea.value.trim(), emotion: selectedEmotion })
            });
            const data = await response.json();
            stopLoader();
            if (data.error) {
                resultDiv.innerHTML = `<p style="color: red;">추천 업데이트 오류: ${data.error}</p>`;
            } else {
                renderFullResult({
                    candidates: currentCandidates,
                    activeEmotion: selectedEmotion,
                    recommendation: data.recommendation
                });
            }
        } catch (error) {
            console.error('Error fetching new recommendation:', error);
            stopLoader();
            resultDiv.innerHTML = '<p style="color: red;">추천 업데이트 중 서버 오류가 발생했습니다.</p>';
        }
    }

    async function handleDiarySubmission() {
        const diaryText = diaryTextarea.value.trim();
        if (!diaryText) return;

        submitBtn.disabled = true;
        submitBtn.textContent = '분석 중...';
        
        saveBtnContainer.style.display = 'none';
        resultContainer.appendChild(saveBtnContainer);

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
            
            renderFullResult({
                candidates: data.candidates,
                activeEmotion: data.top_emotion,
                recommendation: data.recommendation
            });

        } catch (error) {
            console.error('Error:', error);
            stopLoader();
            resultDiv.innerHTML = '<p style="color: red;">처리 중 서버 오류가 발생했습니다.</p>';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '다시 분석하기';
        }
    }

    async function handleDiarySave() {
        const diaryText = diaryTextarea.value.trim();
        if (!diaryText || !currentEmotion) {
            saveStatus.innerHTML = `<span style="color: red;">저장할 일기 내용이나 선택된 감정이 없습니다.</span>`;
            return;
        }

        saveDiaryBtn.disabled = true;
        saveDiaryBtn.textContent = '저장 중...';
        saveStatus.textContent = '';

        try {
            const formData = new FormData();
            formData.append('diary', diaryText);
            formData.append('emotion', currentEmotion);

            const response = await fetch('/diary/save', {
                method: 'POST',
                body: formData 
            });
            const data = await response.json();

            if (response.ok && data.success) {
                saveStatus.innerHTML = `<span style="color: green;">${data.success}</span>`;
            } else {
                saveStatus.innerHTML = `<span style="color: red;">오류: ${data.error || '알 수 없는 오류'}</span>`;
            }
        } catch (error) {
            console.error('Error saving diary:', error);
            saveStatus.innerHTML = `<span style="color: red;">일기 저장 중 서버 오류가 발생했습니다.</span>`;
        } finally {
            saveDiaryBtn.disabled = false;
            saveDiaryBtn.textContent = '일기 저장하기';
            setTimeout(() => { saveStatus.textContent = '' }, 4000);
        }
    }

    // --- INITIALIZATION ---

    diaryTextarea.addEventListener('input', updateButtonState);
    submitBtn.addEventListener('click', handleDiarySubmission);
    saveDiaryBtn.addEventListener('click', handleDiarySave);

    updateButtonState();
});