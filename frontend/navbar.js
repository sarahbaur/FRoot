document.addEventListener('DOMContentLoaded', () => {
    // Navigation toggle
    const navIcon = document.querySelector('.nav-icon');
    const navLinks = document.querySelector('.nav-links');

    // Toggle navigation links on click
    navIcon.addEventListener('click', () => {
        navLinks.classList.toggle('nav-active');
    });
});
