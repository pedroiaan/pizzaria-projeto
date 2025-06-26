document.addEventListener('DOMContentLoaded', () => {
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');

    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', () => {
            const passwordInput = button.previousElementSibling;
            
            if (passwordInput.type === 'password') {
                // Mostra a senha
                passwordInput.type = 'text';
                button.textContent = '🙈'; 
            } else {
                // Oculta a senha
                passwordInput.type = 'password';
                button.textContent = '👁️'; 
            }
        });
    });
});