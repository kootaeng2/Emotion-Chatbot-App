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
