// 테마 로딩 스크립트
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const root = document.documentElement;

    // --- 테마 설정 ---
    const themes = {
        // 그라디언트 테마
        default: { bg: 'linear-gradient(135deg, #ece9f7, #cacae0)', primary: '#6598e5' },
        sunset: { bg: 'linear-gradient(135deg, #ff7e5f, #feb47b)', primary: '#e5533b' },
        forest: { bg: 'linear-gradient(135deg, #5a3f37, #2c7744)', primary: '#92b57a' },
        sky: { bg: 'linear-gradient(135deg, #a1c4fd, #c2e9fb)', primary: '#6a89cc' },
        night: { bg: 'linear-gradient(135deg, #0f2027, #203a43, #2c5364)', primary: '#a3b1c6' },
        sea: { bg: 'linear-gradient(135deg, #2c7744, #6598e5)', primary: '#92b57a' },

        // 단색 테마
        current: { bg: 'linear-gradient(135deg, #ece9f7, #cacae0)', primary: '#6598e5' },
        blue: { bg: 'linear-gradient(135deg, #a1c4fd, #c2e9fb)', primary: '#6a89cc' }, // 하늘 테마 색상으로 변경
        lightyellow: { bg: '#fff9e6', primary: '#d4a237' },
    };

    function applyTheme(theme) {
        if (theme) {
            body.style.background = theme.bg;
            root.style.setProperty('--primary-color', theme.primary);
        }
    }

    // --- 페이지 로드 시 저장된 테마 적용 ---
    const savedThemeName = localStorage.getItem('themeName') || 'default';
    const savedThemeIsImage = localStorage.getItem('themeIsImage') === 'true';
    const savedThemeValue = localStorage.getItem('themeValue');

    if (savedThemeIsImage && savedThemeValue) {
        body.style.background = `url(${savedThemeValue}) no-repeat center center / cover`;
        body.style.backgroundAttachment = 'fixed';
    } else if (themes[savedThemeName]) {
        applyTheme(themes[savedThemeName]);
    }
});
