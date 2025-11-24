document.addEventListener('DOMContentLoaded', () => {
    const curtain = document.getElementById('transition-curtain');
    const links = document.querySelectorAll('a');

    // Ensure curtain is hidden on new page load (especially for back/forward)
    curtain.classList.remove('active');

    links.forEach(link => {
        link.addEventListener('click', e => {
            const href = link.getAttribute('href');

            // Check for internal, non-anchor, non-new-tab links
            if (href && href.length > 0 && !href.startsWith('#') && !link.getAttribute('target') && link.href.startsWith(window.location.origin)) {
                
                // Don't apply transition to logout
                if (href.includes('logout')) {
                    return;
                }

                e.preventDefault();
                curtain.classList.add('active');

                setTimeout(() => {
                    window.location.href = href;
                }, 400); // Matches CSS transition duration
            }
        });
    });

    // Handle back/forward button cache (bfcache)
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            curtain.classList.remove('active');
        }
    });
});
