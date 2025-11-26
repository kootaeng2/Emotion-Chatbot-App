document.addEventListener('DOMContentLoaded', function() {
    // --- Emotion Map ---
    const emotionMap = {
        '기쁨': { emoji: '😄', dotClass: 'dot-기쁨', itemClass: 'item-기쁨' },
        '슬픔': { emoji: '😢', dotClass: 'dot-슬픔', itemClass: 'item-슬픔' },
        '분노': { emoji: '😠', dotClass: 'dot-분노', itemClass: 'item-분노' },
        '불안': { emoji: '😟', dotClass: 'dot-불안', itemClass: 'item-불안' },
        '당황': { emoji: '😮', dotClass: 'dot-당황', itemClass: 'item-당황' },
        '상처': { emoji: '💔', dotClass: 'dot-상처', itemClass: 'item-상처' },
        'default': { emoji: '🤔', dotClass: 'dot-default', itemClass: 'item-default' }
    };

    // --- DOM Elements ---
    const currentYearEl = document.getElementById('current-year');
    const prevYearBtn = document.getElementById('prev-year');
    const nextYearBtn = document.getElementById('next-year');
    const monthList = document.querySelector('.month-list');
    const calendarMonthTitle = document.getElementById('calendar-month-title');
    const diaryListContainer = document.getElementById('diary-list-container');
    
    // --- State ---
    let diaryDataByDate = {};
    let currentYear, currentMonth;
    let fp; // flatpickr instance

    // --- Functions ---
    async function fetchDiaries(year, month) {
        try {
            const response = await fetch(`/api/diaries?year=${year}&month=${month}`);
            if (!response.ok) throw new Error('Diary data failed to load.');
            const diaries = await response.json();
            
            diaryDataByDate = {}; 
            diaries.forEach(diary => {
                diaryDataByDate[diary.date] = diaryDataByDate[diary.date] || [];
                diaryDataByDate[diary.date].push(diary);
            });
            return diaries;
        } catch (error) {
            console.error(error);
            return [];
        }
    }

    function renderTimeline(dateStr) {
        const diaries = diaryDataByDate[dateStr] || [];
        diaryListContainer.innerHTML = '';
        if (diaries.length === 0) {
            diaryListContainer.innerHTML = '<div class="placeholder"><p>작성된 일기가 없습니다.</p></div>';
            return;
        }
        diaries.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        diaries.forEach(diary => {
            const emotionInfo = emotionMap[diary.emotion] || emotionMap.default;
            const item = document.createElement('div');
            item.className = `timeline-item ${emotionInfo.itemClass}`;
            const time = new Date(diary.createdAt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
            item.innerHTML = `
                <div class="item-header">
                    <span class="item-time">${time}</span>
                    <span class="item-emotion">${emotionInfo.emoji}</span>
                </div>
                <div class="item-content"><p>${diary.content.replace(/\n/g, '<br>')}</p></div>
            `;
            diaryListContainer.appendChild(item);
        });
    }

    function updateUI(year, month) { // month is 0-indexed
        currentYear = year;
        currentMonth = month;
        currentYearEl.textContent = year;
        calendarMonthTitle.textContent = new Date(year, month).toLocaleString('en-US', { month: 'long' });
        document.querySelectorAll('.month-item').forEach(item => {
            item.classList.toggle('active', parseInt(item.dataset.month) === month);
        });
    }
    
    async function handleDateChange(year, month) { // month is 0-indexed
        updateUI(year, month);
        await fetchDiaries(year, month + 1);
        if (fp) fp.redraw();
    }

    // --- Initializer ---
    function initializeCalendar() {
        fp = flatpickr("#calendar", {
            inline: true,
            dateFormat: "Y-m-d",
            locale: "en",
            onReady: async (selectedDates, dateStr, instance) => {
                const today = new Date();
                await handleDateChange(today.getFullYear(), today.getMonth());
                instance.setDate(today, true);
            },
            onChange: (selectedDates, dateStr, instance) => {
                if (selectedDates.length > 0) renderTimeline(dateStr);
            },
            onMonthChange: async (selectedDates, dateStr, instance) => {
                await handleDateChange(instance.currentYear, instance.currentMonth);
            },
            onYearChange: async (selectedDates, dateStr, instance) => {
                await handleDateChange(instance.currentYear, instance.currentMonth);
            },
            onDayCreate: (dObj, dStr, fp, dayElem) => {
                const date = flatpickr.formatDate(dayElem.dateObj, "Y-m-d");
                const diariesForDay = diaryDataByDate[date];
                if (diariesForDay && diariesForDay.length > 0) {
                    const latestDiary = diariesForDay[diariesForDay.length - 1];
                    const emotionInfo = emotionMap[latestDiary.emotion] || emotionMap.default;
                    const dot = document.createElement('div');
                    dot.className = `emotion-dot ${emotionInfo.dotClass}`;
                    dayElem.appendChild(dot);
                }
            }
        });
    }

    // --- Event Listeners ---
    monthList.addEventListener('click', (e) => {
        if (e.target.classList.contains('month-item')) {
            const month = parseInt(e.target.dataset.month);
            if (month !== currentMonth) fp.changeMonth(month - currentMonth);
        }
    });

    prevYearBtn.addEventListener('click', () => fp.changeYear(fp.currentYear - 1));
    nextYearBtn.addEventListener('click', () => fp.changeYear(fp.currentYear + 1));
    
    // --- Initial Load ---
    initializeCalendar();
});