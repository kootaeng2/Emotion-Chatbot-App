document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('submit-btn');
    const diaryTextarea = document.getElementById('diary');
    const resultDiv = document.getElementById('result');
    const saveStatus = document.getElementById('save-status');
    const emotionEmojiMap = {
        '분노': '😠', '불안': '😟', '슬픔': '😢',
        '당황': '😮', '기쁨': '😄', '상처': '💔',
    };

    function updateButtonState() {
        analyzeBtn.disabled = diaryTextarea.value.trim() === '';
    }

    diaryTextarea.addEventListener('input', () => {
        updateButtonState();
        resultDiv.innerHTML = '<p>이곳에 감정 분석 및 추천 결과가 표시됩니다.</p>';
    });

    analyzeBtn.addEventListener('click', async () => {
        const diary = diaryTextarea.value.trim();
        if (!diary) return;

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = '분석 및 저장 중...';
        resultDiv.innerHTML = '<p>감정을 분석하고 추천을 생성하는 중입니다...</p>';
        saveStatus.textContent = '';

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ diary })
            });
            const data = await response.json();

            if (data.error) {
                resultDiv.innerHTML = `<p style="color: red;">오류: ${data.error}</p>`;
            } else {
                let recommendationText = data.recommendation || '';
                let acceptanceContent = '';
                let diversionContent = '';
                
                const diversionMarker = '## [전환]';
                const acceptanceMarker = '## [수용]';

                let diversionIndex = recommendationText.indexOf(diversionMarker);
                let acceptanceIndex = recommendationText.indexOf(acceptanceMarker);

                if (acceptanceIndex !== -1) {
                    let acceptanceStart = acceptanceIndex + acceptanceMarker.length;
                    if (diversionIndex !== -1) {
                        acceptanceContent = recommendationText.substring(acceptanceStart, diversionIndex).trim();
                    } else {
                        acceptanceContent = recommendationText.substring(acceptanceStart).trim();
                    }
                }

                if (diversionIndex !== -1) {
                    diversionContent = recommendationText.substring(diversionIndex + diversionMarker.length).trim();
                }

                resultDiv.innerHTML = `
                    <p style="font-weight: 500; font-size: 1.1rem;">
                        <strong>감정 분석 결과:</strong> ${data.emotion} ${data.emoji}
                    </p>
                    <div class="rec-tabs">
                        <button class="rec-tab-btn active" data-tab="acceptance">수용</button>
                        <button class="rec-tab-btn" data-tab="diversion">전환</button>
                    </div>
                    <div id="rec-acceptance" class="rec-content active">
                        ${marked.parse(acceptanceContent || '추천을 불러오지 못했습니다.')}
                    </div>
                    <div id="rec-diversion" class="rec-content">
                        ${marked.parse(diversionContent || '추천을 불러오지 못했습니다.')}
                    </div>
                `;

                resultDiv.querySelectorAll('.rec-tab-btn').forEach(button => {
                    button.addEventListener('click', () => {
                        const tab = button.dataset.tab;
                        resultDiv.querySelectorAll('.rec-tab-btn').forEach(btn => btn.classList.remove('active'));
                        button.classList.add('active');

                        resultDiv.querySelectorAll('.rec-content').forEach(content => content.classList.remove('active'));
                        resultDiv.querySelector(`#rec-${tab}`).classList.add('active');
                    });
                });

                saveStatus.innerHTML = '<span style="color: green;">일기가 성공적으로 저장되었습니다!</span>';
                setTimeout(() => { saveStatus.textContent = '' }, 3000);
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = '<p style="color: red;">처리 중 서버 오류가 발생했습니다.</p>';
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = '분석 및 저장';
        }
    });

    updateButtonState();
});