document.addEventListener('DOMContentLoaded', () => {


    const themeToggleInput = document.getElementById('theme-toggle-input');
    const body = document.body;


    const applySavedTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
            themeToggleInput.checked = true; 
        } else {
            body.classList.remove('dark-mode');
            themeToggleInput.checked = false; 
        }
    };

    themeToggleInput.addEventListener('change', () => {
        if (themeToggleInput.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark'); 
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });


    applySavedTheme();

});