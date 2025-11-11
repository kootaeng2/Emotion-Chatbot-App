document.addEventListener('click', function(event) {
    if (event.target.classList.contains('rec-tab-btn')) {
        const tabId = event.target.dataset.tab;
        const tabsContainer = event.target.closest('.rec-tabs');
        const contentContainer = tabsContainer.parentElement;

        tabsContainer.querySelectorAll('.rec-tab-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        contentContainer.querySelectorAll('.rec-content').forEach(content => content.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
    }
});