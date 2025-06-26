import sqlite3
from bottle import template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash

class Application():

    def __init__(self):
        self.db_name = 'pizzaria.db'
        self.init_db()

        self.pages = {
            'pagina': self.pagina,
            'login_cadastro': self.login_cadastro_page,
        }

    def init_db(self):
        """Cria a tabela de usuários se ela não existir."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        return self.login_cadastro_page(login_success="Cadastro realizado com sucesso! Faça o login.")
    
    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row 
        return conn

    def render(self, page_name, **kwargs):
       """Renderiza a página solicitada pelo nome."""
       content_method = self.pages.get(page_name)
       return content_method(**kwargs)
    
    def pagina(self):
        """Renderiza a página principal."""
        return template('app/views/html/pagina.html')

    def login_cadastro_page(self, **kwargs):
        """Exibe a página combinada de login/cadastro."""
        return template('app/views/html/login_cadastro.html', **kwargs)

    def handle_login(self):
        """Processa o formulário de login."""
        email = request.forms.get('email')
        password = request.forms.get('password')

        conn = self._get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            return redirect('/pagina')
        
        return self.login_cadastro_page(login_error="Email ou senha inválidos.")

    def handle_cadastro(self):
        """Processa o formulário de cadastro."""
        name = request.forms.get('name')
        email = request.forms.get('email')
        password = request.forms.get('password')

        hashed_password = generate_password_hash(password)
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, hashed_password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()

            return self.login_cadastro_page(cadastro_error="Este email já está cadastrado.")
        
        conn.close()
        return redirect('/pagina')