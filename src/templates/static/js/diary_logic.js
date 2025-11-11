document.addEventListener('DOMContentLoaded', function() {
    const emotionEmojiMap = {
        '분노': '😠', '불안': '😟', '슬픔': '😢',
        '당황': '😮', '기쁨': '😄', '상처': '💔',
    };
    const diaryDisplay = document.getElementById('diary-display');
    let diaryDataByDate = {};
    let fp;

    const initialDisplayHTML = diaryDisplay.innerHTML;

    function renderDiaryDetail(diary, container) {
        container.innerHTML = ''; // Clear previous detail

        const header = document.createElement('div');
        header.className = 'diary-header';
        header.innerHTML = `
            <div class="diary-date">${diary.createdAt}</div>
            <div class="diary-emotion">${diary.emotion} ${emotionEmojiMap[diary.emotion] || '🤔'}</div>
        `;

        const body = document.createElement('div');
        body.className = 'diary-body';
        
        let recommendationText = diary.recommendation || '';
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

        body.innerHTML = `
            <div class="diary-section">
                <h3>나의 일기</h3>
                <div class="diary-content">${diary.content}</div>
            </div>
            <div class="diary-section">
                <h3>AI 추천</h3>
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
            </div>
        `;
        
        container.appendChild(header);
        container.appendChild(body);

        container.querySelectorAll('.rec-tab-btn').forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                container.querySelectorAll('.rec-tab-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                container.querySelectorAll('.rec-content').forEach(content => content.classList.remove('active'));
                container.querySelector(`#rec-${tab}`).classList.add('active');
            });
        });
    }

    async function handleDelete(diaryId, dateStr) {
        if (!confirm('정말로 이 일기를 삭제하시겠습니까?')) return;

        try {
            const response = await fetch(`/diary/delete/${diaryId}`, { method: 'DELETE' });
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || '삭제에 실패했습니다.');
            }

            diaryDataByDate[dateStr] = diaryDataByDate[dateStr].filter(d => d.id !== diaryId);
            if (diaryDataByDate[dateStr].length === 0) {
                delete diaryDataByDate[dateStr];
            }

            renderDayView(diaryDataByDate[dateStr] || null, dateStr);
            fp.redraw();

        } catch (error) {
            console.error('Delete error:', error);
            alert(error.message);
        }
    }

    function renderDayView(diaries, dateStr) {
        diaryDisplay.innerHTML = '';
        diaryDisplay.classList.remove('placeholder');

        if (!diaries || diaries.length === 0) {
            diaryDisplay.innerHTML = initialDisplayHTML;
            diaryDisplay.classList.add('placeholder');
            return;
        }

        const listContainer = document.createElement('div');
        listContainer.id = 'diary-list-container';

        const detailContainer = document.createElement('div');
        detailContainer.id = 'diary-detail-container';

        diaries.forEach((diary, index) => {
            const item = document.createElement('div');
            item.className = 'diary-list-item';
            item.dataset.diaryId = diary.id;

            const time = new Date(diary.createdAt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

            item.innerHTML = `
                <span class="list-item-emoji">${emotionEmojiMap[diary.emotion] || '🤔'}</span>
                <span class="list-item-time">${time}</span>
                <button class="delete-btn" title="삭제">&times;</button>
            `;

            item.querySelector('.delete-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                handleDelete(diary.id, dateStr);
            });

            item.addEventListener('click', () => {
                document.querySelectorAll('.diary-list-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                renderDiaryDetail(diary, detailContainer);
            });

            listContainer.appendChild(item);
        });

        diaryDisplay.appendChild(listContainer);
        diaryDisplay.appendChild(detailContainer);

        if (diaries.length > 0) {
            const latestDiary = diaries[diaries.length - 1];
            listContainer.querySelector(`.diary-list-item[data-diary-id='${latestDiary.id}']`).classList.add('active');
            renderDiaryDetail(latestDiary, detailContainer);
        }
    }

    async function fetchDiaries(year, month, instance) {
        try {
            const response = await fetch(`/api/diaries?year=${year}&month=${month}`);
            if (!response.ok) throw new Error('일기 데이터 로딩 실패');
            const diaries = await response.json();
            
            diaryDataByDate = {};
            diaries.forEach(diary => {
                if (!diaryDataByDate[diary.date]) {
                    diaryDataByDate[diary.date] = [];
                }
                diaryDataByDate[diary.date].push(diary);
            });

            if (instance) instance.redraw();
        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    }

    fp = flatpickr("#calendar", {
        inline: true,
        dateFormat: "Y-m-d",
        locale: flatpickr.l10ns.ko,
        onMonthChange: (d, s, i) => fetchDiaries(i.currentYear, i.currentMonth + 1, i),
        onYearChange: (d, s, i) => fetchDiaries(i.currentYear, i.currentMonth + 1, i),
        onDayCreate: (dObj, dStr, fp, dayElem) => {
            const dayNumber = dayElem.innerHTML;
            dayElem.innerHTML = '';

            const contentWrapper = document.createElement('div');
            contentWrapper.className = 'day-content-wrapper';
            
            const numberSpan = document.createElement('span');
            numberSpan.className = 'day-number';
            numberSpan.textContent = dayNumber;
            contentWrapper.appendChild(numberSpan);

            const emojiSpan = document.createElement("span");
            emojiSpan.className = "emotion-emoji";

            const y = dayElem.dateObj.getFullYear();
            const m = String(dayElem.dateObj.getMonth() + 1).padStart(2, '0');
            const d = String(dayElem.dateObj.getDate()).padStart(2, '0');
            const date = `${y}-${m}-${d}`;

            if (diaryDataByDate[date] && diaryDataByDate[date].length > 0) {
                const diariesForDay = diaryDataByDate[date];
                const latestDiary = diariesForDay[diariesForDay.length - 1];
                const emoji = emotionEmojiMap[latestDiary.emotion] || '🤔';
                emojiSpan.textContent = emoji;
            } else {
                emojiSpan.innerHTML = '&nbsp;';
            }
            
            contentWrapper.appendChild(emojiSpan);
            dayElem.appendChild(contentWrapper);
        },
        onChange: (selectedDates, dateStr, instance) => {
            const diariesForDay = diaryDataByDate[dateStr] || null;
            renderDayView(diariesForDay, dateStr);
        }
    });

    // Initial Load
    fetchDiaries(new Date().getFullYear(), new Date().getMonth() + 1, fp);
});