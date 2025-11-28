document.addEventListener('DOMContentLoaded', () => {
    // --- Emotion Map ---
    const emotionMap = {
        '기쁨': { emoji: '😄', bgClass: 'bg-기쁨', itemClass: 'item-기쁨' },
        '슬픔': { emoji: '😢', bgClass: 'bg-슬픔', itemClass: 'item-슬픔' },
        '분노': { emoji: '😠', bgClass: 'bg-분노', itemClass: 'item-분노' },
        '불안': { emoji: '😟', bgClass: 'bg-불안', itemClass: 'item-불안' },
        '당황': { emoji: '😮', bgClass: 'bg-당황', itemClass: 'item-당황' },
        '상처': { emoji: '💔', bgClass: 'bg-상처', itemClass: 'item-상처' },
        'default': { emoji: '🤔', bgClass: 'bg-default', itemClass: 'item-default' }
    };

    // --- DOM Elements ---
    const currentYearEl = document.getElementById('current-year');
    const prevYearBtn = document.getElementById('prev-year');
    const nextYearBtn = document.getElementById('next-year');
    const monthList = document.querySelector('.month-list');
    const calendarMonthTitle = document.getElementById('calendar-month-title');
    const diaryListContainer = document.getElementById('diary-list-container');
    console.log("diaryListContainer element:", diaryListContainer); // 요소 확인 로그
    const recModalOverlay = document.getElementById('rec-modal-overlay');
    const recModalTitle = document.getElementById('rec-modal-title');
    const recModalBody = document.getElementById('rec-modal-body');
    const recModalCloseBtn = document.getElementById('rec-modal-close');
    
    // --- State ---
    let diaryDataByDate = {};
    let currentYear, currentMonth;
    let fp; // flatpickr instance
    let lastFetchedYear = null; // 월별 카운트를 마지막으로 가져온 연도

    // --- Functions ---

    async function updateMonthlyCounts(year) {
        if (year === lastFetchedYear) return; // 이미 해당 연도의 데이터를 가져왔으면 실행 안함

        try {
            const response = await fetch(`/api/diaries/counts?year=${year}`);
            if (!response.ok) throw new Error('Failed to load diary counts.');
            const counts = await response.json();
            
            document.querySelectorAll('.month-item').forEach(item => {
                const month_key = (parseInt(item.dataset.month) + 1).toString(); // 월 번호를 문자열로 변환
                const countSpan = item.querySelector('.diary-count');
                const count = counts[month_key] || 0; // 문자열 키로 접근
                
                if (count > 0) {
                    countSpan.textContent = count;
                } else {
                    countSpan.textContent = '';
                }
            });
            lastFetchedYear = year; // 마지막으로 가져온 연도 기록
        } catch (error) {
            console.error("Error fetching diary counts:", error);
        }
    }

    async function fetchDiaries(year, month) {
        try {
            console.log(`Fetching diaries for year: ${year}, month: ${month}`);
            const response = await fetch(`/api/diaries?year=${year}&month=${month}`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Diary data failed to load. Status: ${response.status}, Message: ${errorText}`);
            }
            const diaries = await response.json();
            console.log("Received diaries:", diaries);
            
            diaryDataByDate = {}; 
            diaries.forEach(diary => {
                // Ensure diary.date is valid before assignment
                if (diary.date) {
                    diaryDataByDate[diary.date] = diaryDataByDate[diary.date] || [];
                    diaryDataByDate[diary.date].push(diary);
                } else {
                    console.warn("Diary item with missing date:", diary);
                }
            });
            console.log("Processed diaryDataByDate:", diaryDataByDate);
            return diaries;
        } catch (error) {
            console.error("Error in fetchDiaries:", error);
            // display a user-friendly error message on the UI
            diaryListContainer.innerHTML = `<div class="placeholder"><p>일기를 불러오는 중 오류가 발생했습니다.</p><p style="font-size: 0.8em; color: #666;">${error.message}</p></div>`;
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
            item.dataset.diary = JSON.stringify(diary); // 전체 diary 객체 저장
            const time = new Date(diary.createdAt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

            item.innerHTML = `
                <div class="item-header">
                    <span class="item-time">${time}</span>
                    <div class="item-controls">
                        <span class="item-emotion">${emotionInfo.emoji}</span>
                        <button class="delete-diary-btn" data-diary-id="${diary.id}">삭제</button>
                    </div>
                </div>
                <div class="item-content">
                    <p>${diary.content.replace(/\n/g, '<br>')}</p>
                </div>
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
        await updateMonthlyCounts(year); // 연도가 바뀔 때마다 카운트 업데이트
        await fetchDiaries(year, month + 1);
        if (fp) fp.redraw();
    }

    const parseRecs = (text) => {
        const contents = { 수용: '', 전환: '' };
        if (!text) return contents;
        const regex = /#+\s*\[\s*(수용|공감|전환|환기)\s*\]([\s\S]*?)(?=(?:#+\s*\[\s*(?:수용|공감|전환|환기)\s*\])|$)/gi;
        let match;
        while ((match = regex.exec(text)) !== null) {
            const type = match[1].trim();
            let content = match[2].trim();
            if (type === '수용' || type === '공감') contents.수용 = content;
            else if (type === '전환' || type === '환기') contents.전환 = content;
        }
        return contents;
    };

    const parseAndClean = (markdown) => {
        if (!markdown) return '<p class="empty-msg">추천 항목이 없습니다.</p>';

        const rawHtml = marked.parse(markdown);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = rawHtml;

        // 방식 1: "추천 이유"가 열 헤더인 경우 해당 열 전체 제거
        const tables = tempDiv.querySelectorAll('table');
        tables.forEach(table => {
            let reasonColumnIndex = -1;
            table.querySelectorAll('th').forEach((th, index) => {
                if (th.textContent.trim() === '추천 이유') {
                    reasonColumnIndex = index;
                }
            });

            if (reasonColumnIndex !== -1) {
                table.querySelectorAll('tr').forEach(row => {
                    if (row.cells[reasonColumnIndex]) {
                        row.deleteCell(reasonColumnIndex);
                    }
                });
            }
        });

        // 방식 2: "추천 이유:" 텍스트가 포함된 행 제거
        const rowsToRemove = [];
        tempDiv.querySelectorAll('td').forEach(td => {
            if (td.textContent.includes('추천 이유:')) {
                const row = td.closest('tr');
                if (row) rowsToRemove.push(row);
            }
        });
        rowsToRemove.forEach(row => row.remove());
        
        // 카테고리 텍스트("영화", "음악", "도서")를 이모지로 변경 (첫 번째 열만)
        const categoryEmojiMap = { '영화': '🎬', '음악': '🎵', '도서': '📚' };
        tempDiv.querySelectorAll('tr').forEach(row => {
            // 헤더 행이 아니고, 셀이 존재할 경우
            if (row.cells.length > 0 && row.cells[0].tagName === 'TD') {
                const firstCell = row.cells[0];
                let cellHtml = firstCell.innerHTML;
                for (const category in categoryEmojiMap) {
                    const regex = new RegExp(`(<strong>)?${category}(</strong>)?`, "g");
                    cellHtml = cellHtml.replace(regex, categoryEmojiMap[category]);
                }
                firstCell.innerHTML = cellHtml;
            }
        });

        return tempDiv.innerHTML;
    };

    // --- Event Listeners ---
    const detailModalOverlay = document.getElementById('diary-detail-modal-overlay');
    const detailModalCloseBtn = document.getElementById('diary-detail-modal-close');

    monthList.addEventListener('click', (e) => {
        if (e.target.classList.contains('month-item')) {
            const month = parseInt(e.target.dataset.month);
            if (month !== currentMonth) fp.changeMonth(month - currentMonth);
        }
    });

    prevYearBtn.addEventListener('click', () => fp.changeYear(fp.currentYear - 1));
    nextYearBtn.addEventListener('click', () => fp.changeYear(fp.currentYear + 1));
    
    diaryListContainer.addEventListener('click', async (e) => {
        // 삭제 버튼 로직
        if (e.target.classList.contains('delete-diary-btn')) {
            e.stopPropagation(); // 이벤트 버블링 방지
            const diaryId = e.target.dataset.diaryId;
            if (!diaryId || !confirm('정말로 이 일기를 삭제하시겠습니까?')) {
                return;
            }

            try {
                const response = await fetch(`/diary/delete/${diaryId}`, {
                    method: 'DELETE',
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || '삭제에 실패했습니다.');
                }

                // 삭제 성공 후 UI 업데이트
                const selectedDate = fp.selectedDates[0];
                await handleDateChange(selectedDate.getFullYear(), selectedDate.getMonth());
                renderTimeline(flatpickr.formatDate(selectedDate, "Y-m-d"));

            } catch (error) {
                console.error('삭제 중 오류 발생:', error);
                alert(error.message);
            }
            return; 
        }
        
        // 상세 모달 로직
        const timelineItem = e.target.closest('.timeline-item');
        if (timelineItem && timelineItem.dataset.diary) {
            try {
                const diary = JSON.parse(timelineItem.dataset.diary);
                openDiaryDetailModal(diary);
            } catch (jsonError) {
                console.error("Failed to parse diary data from dataset:", jsonError);
            }
        }
    });

    function openDiaryDetailModal(diary) {
        const modalTitle = document.getElementById('diary-detail-title');
        const modalBody = document.getElementById('diary-detail-body');
        
        modalTitle.innerHTML = ''; // 제목 제거

        let bodyHtml = `
            <div class="diary-content-section">
                <h3>나의 기록</h3>
                <p>${diary.content.replace(/\n/g, '<br>')}</p>
            </div>
        `;

        if (diary.recommendation) {
            const sections = parseRecs(diary.recommendation);
            if (sections.수용) {
                bodyHtml += `
                    <div class="diary-content-section">
                        <h3>수용</h3>
                        ${parseAndClean(sections.수용)}
                    </div>
                `;
            }
            if (sections.전환) {
                bodyHtml += `
                    <div class="diary-content-section">
                        <h3>전환</h3>
                        ${parseAndClean(sections.전환)}
                    </div>
                `;
            }
        }
        
        modalBody.innerHTML = bodyHtml;
        detailModalOverlay.style.display = 'flex';
    }

    function closeDiaryDetailModal() {
        detailModalOverlay.style.display = 'none';
    }

    detailModalCloseBtn.addEventListener('click', closeDiaryDetailModal);
    detailModalOverlay.addEventListener('click', (e) => {
        if (e.target === detailModalOverlay) {
            closeDiaryDetailModal();
        }
    });

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
                // 날짜 숫자를 span으로 감싸서 z-index 제어
                dayElem.innerHTML = `<span class="flatpickr-day-num">${dayElem.innerHTML}</span>`;

                const date = flatpickr.formatDate(dayElem.dateObj, "Y-m-d");
                const diariesForDay = diaryDataByDate[date];
                if (diariesForDay && diariesForDay.length > 0) {
                    const latestDiary = diariesForDay[diariesForDay.length - 1];
                    const emotionInfo = emotionMap[latestDiary.emotion] || emotionMap.default;
                    
                    // 날짜 셀에 직접 배경색 클래스를 추가 (가상요소 ::before가 이 클래스를 사용)
                    dayElem.classList.add('has-diary', emotionInfo.bgClass);
                }
            }
        });
    }

    // --- Initial Load ---
    initializeCalendar();
});
