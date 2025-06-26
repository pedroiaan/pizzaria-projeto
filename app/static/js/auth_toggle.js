document.addEventListener('DOMContentLoaded', () => {
    // 1. Encontrar os elementos na página
    const loginContainer = document.getElementById('login-container');
    const registerContainer = document.getElementById('register-container');

    const showRegisterLink = document.getElementById('show-register-link');
    const showLoginLink = document.getElementById('show-login-link');

    // 2. Adicionar o evento de clique no link "Cadastre-se"
    showRegisterLink.addEventListener('click', (event) => {
        event.preventDefault(); // Impede que o link recarregue a página

        // Esconde o formulário de login e mostra o de cadastro
        loginContainer.style.display = 'none';
        registerContainer.style.display = 'flex'; // Usamos 'flex' porque é o display original do .form-container
    });

    // 3. Adicionar o evento de clique no link "Entre"
    showLoginLink.addEventListener('click', (event) => {
        event.preventDefault(); // Impede que o link recarregue a página

        // Esconde o formulário de cadastro e mostra o de login
        registerContainer.style.display = 'none';
        loginContainer.style.display = 'flex';
    });
});