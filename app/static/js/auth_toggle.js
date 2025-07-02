document.addEventListener('DOMContentLoaded', () => {
    const loginContainer = document.getElementById('login-container');
    const registerContainer = document.getElementById('register-container');

    const showRegisterLink = document.getElementById('show-register-link');
    const showLoginLink = document.getElementById('show-login-link');

    showRegisterLink.addEventListener('click', (event) => {
        event.preventDefault();


        loginContainer.style.display = 'none';
        registerContainer.style.display = 'flex'; 
    });

    showLoginLink.addEventListener('click', (event) => {
        event.preventDefault();

        registerContainer.style.display = 'none';
        loginContainer.style.display = 'flex';
    });
});