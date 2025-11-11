// Onboarding script
document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.getElementById('onboarding-overlay');
    const nextBtn = document.getElementById('onboarding-next');
    const prevBtn = document.getElementById('onboarding-prev');
    const closeBtn = document.getElementById('onboarding-close');
    const dots = document.querySelectorAll('.onboarding-dot');
    const slides = document.querySelectorAll('.onboarding-slide');
    const nicknameInput = document.getElementById('onboarding-nickname-input');
    let currentSlide = 1;

    const onboardingComplete = localStorage.getItem('onboardingComplete');
    if (onboardingComplete !== 'true') {
        overlay.classList.add('active');
    }

    function showSlide(slideNumber) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        document.getElementById(`slide${slideNumber}`).classList.add('active');
        document.querySelector(`.onboarding-dot[data-slide='${slideNumber}']`).classList.add('active');
        currentSlide = slideNumber;

        // Update button visibility and text
        if (currentSlide === 1) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'inline-block';
        }

        if (currentSlide === slides.length) {
            nextBtn.textContent = '시작하기';
        } else {
            nextBtn.textContent = '다음';
        }
    }

    nextBtn.addEventListener('click', async () => {
        if (currentSlide < slides.length) {
            showSlide(currentSlide + 1);
        } else { // Last slide (nickname setting)
            const nickname = nicknameInput.value.trim();
            if (nickname) {
                try {
                    const response = await fetch('/update_nickname', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `nickname=${encodeURIComponent(nickname)}`,
                    });
                    if (!response.ok) {
                        throw new Error('Failed to update nickname');
                    }
                    // Optionally, update session storage or display a success message
                    console.log('Nickname updated successfully');
                } catch (error) {
                    console.error('Error updating nickname:', error);
                    // Handle error, e.g., show a message to the user
                }
            }
            localStorage.setItem('onboardingComplete', 'true');
            closeOnboarding();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentSlide > 1) {
            showSlide(currentSlide - 1);
        }
    });

    closeBtn.addEventListener('click', () => {
        localStorage.setItem('onboardingComplete', 'true');
        closeOnboarding();
    });

    dots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            const slideNumber = parseInt(e.target.dataset.slide);
            showSlide(slideNumber);
        });
    });

    function closeOnboarding() {
        overlay.classList.remove('active');
    }

    showSlide(currentSlide); // Initialize first slide
});