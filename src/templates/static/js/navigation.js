// This script provides visual feedback on click.
// The initial position of the tubelight is set purely by CSS.
// Page navigation is handled by the browser's default behavior.

document.addEventListener('DOMContentLoaded', () => {
    const tubelight = document.querySelector('nav .tubelight');
    const allLinks = document.querySelectorAll('nav a');

    allLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Animate the light to the clicked link's position for visual feedback.
            if (!tubelight) return;
            const newLeft = link.offsetLeft + (link.offsetWidth / 2) - (tubelight.offsetWidth / 2);
            tubelight.style.left = `${newLeft}px`;
        });
    });
});