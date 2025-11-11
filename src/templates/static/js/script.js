function createRecommendationTabs(acceptanceContent, diversionContent, containerId) {
    const acceptanceHtml = marked.parse(acceptanceContent || '추천을 불러오지 못했습니다.');
    const diversionHtml = marked.parse(diversionContent || '추천을 불러오지 못했습니다.');

    return `
        <div class="rec-tabs">
            <button class="rec-tab-btn active" data-tab="${containerId}-acceptance">수용</button>
            <button class="rec-tab-btn" data-tab="${containerId}-diversion">전환</button>
        </div>
        <div id="${containerId}-acceptance" class="rec-content active">
            ${acceptanceHtml}
        </div>
        <div id="${containerId}-diversion" class="rec-content">
            ${diversionHtml}
        </div>
    `;
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('rec-tab-btn')) {
        const tabId = event.target.dataset.tab;
        const tabsContainer = event.target.closest('.rec-tabs');
        if (!tabsContainer) return;

        const contentContainer = tabsContainer.parentElement;

        tabsContainer.querySelectorAll('.rec-tab-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        // Find the correct content sections to toggle
        let acceptanceContent = document.getElementById(`${tabsContainer.dataset.containerId}-acceptance`);
        let diversionContent = document.getElementById(`${tabsContainer.dataset.containerId}-diversion`);

        if (!acceptanceContent || !diversionContent) {
            // Fallback for older structure if needed, or just use the more specific IDs
            const allRecContent = contentContainer.querySelectorAll('.rec-content');
            allRecContent.forEach(content => content.classList.remove('active'));
        } else {
            acceptanceContent.classList.remove('active');
            diversionContent.classList.remove('active');
        }
        
        const targetContent = document.getElementById(tabId);
        if (targetContent) {
            targetContent.classList.add('active');
        }
    }
});