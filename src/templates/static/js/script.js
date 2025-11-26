document.addEventListener('DOMContentLoaded', function() {
    // --- 매직 내비게이션 바 동작 ---
    const marker = document.querySelector('.nav-marker');
    const navItems = document.querySelectorAll('.nav-item a');
    const navList = document.querySelector('.navbar-menu');

    function moveMarker(e) {
        const item = e.target.closest('li'); // li 요소 기준
        if (item && marker) {
            marker.style.width = (item.offsetWidth - 10) + 'px';
            marker.style.left = (item.offsetLeft + 12) + 'px';
            marker.style.opacity = '1';
        }
    }

    // 각 메뉴에 마우스 올리면 마커 이동
    navItems.forEach(link => {
        link.addEventListener('mouseenter', moveMarker);
    });

    // 메뉴 밖으로 나가면 마커 숨기기 (선택사항)
    if (navList) {
        navList.addEventListener('mouseleave', () => {
            if(marker) marker.style.opacity = '0';
        });
    }
});