// 테마 변경 스크립트
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const root = document.documentElement;
    const themePalette = document.querySelector('.theme-palette');
    const themeWrappers = document.querySelectorAll('.theme-option-wrapper');

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
        body.style.background = theme.bg;
        root.style.setProperty('--primary-color', theme.primary);
    }

    function saveTheme(themeName, themeData) {
        localStorage.setItem('themeName', themeName);
        if (themeName.startsWith('image-')) {
            localStorage.setItem('themeIsImage', 'true');
            localStorage.setItem('themeValue', themeData.bg);
        }
        else {
            localStorage.setItem('themeIsImage', 'false');
            localStorage.setItem('themeValue', themeName);
        }
    }

    // --- 이벤트 리스너 ---
    themePalette.addEventListener('click', (e) => {
        const target = e.target;
        const wrapper = target.closest('.theme-option-wrapper');

        // 메인 버튼(.theme-btn) 클릭 시 메뉴 토글
        if (target.classList.contains('theme-btn')) {
            e.stopPropagation();
            themeWrappers.forEach(w => {
                if (w !== wrapper) w.classList.remove('active');
            });
            wrapper.classList.toggle('active');
            return; // 메인 버튼 클릭 시 테마 적용 로직을 실행하지 않음
        }

        const subOptions = target.closest('.sub-options');
        if (subOptions) {
            // --- 테마 적용 로직 ---
            let themeName, themeData;

            // 이미지 버튼 클릭 시
            if (target.tagName === 'IMG' && target.dataset.themeBg) {
                themeName = 'image-' + target.dataset.themeBg;
                themeData = { bg: target.dataset.themeBg };
                body.style.background = `url(${themeData.bg}) no-repeat center center / cover`;
                saveTheme(themeName, themeData);
            }
            // 색상 버튼 (서브) 클릭 시
            else if (target.classList.contains('sub-option-btn') && target.dataset.color) {
                themeName = target.dataset.color;
                if (themes[themeName]) {
                    themeData = themes[themeName];
                    applyTheme(themeData);
                    saveTheme(themeName, themeData);
                }
            }
            // 테마 적용 후 모든 메뉴 닫기
            themeWrappers.forEach(w => w.classList.remove('active'));
        }
    });

    // 팔레트 바깥 영역 클릭 시 모든 메뉴 닫기
    document.addEventListener('click', (e) => {
        if (!themePalette.contains(e.target)) {
            themeWrappers.forEach(w => w.classList.remove('active'));
        }
    });
});