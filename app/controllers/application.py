import sqlite3
import json
from bottle import template, request, redirect, response
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Application():

    def __init__(self):
        self.db_name = 'pizzaria.db'
        self.init_db()

    def init_db(self):
        """Cria as tabelas (users, pedidos, itens_pedido) se não existirem."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preco_total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Recebido',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                nome_pizza TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                tamanho TEXT NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()
    
    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row 
        return conn

    def render(self, page_name, **kwargs):
        """Renderiza um template passando quaisquer argumentos necessários."""
        if not page_name.endswith('.html'):
            page_name += '.html'
        
        return template(f'app/views/html/{page_name}', **kwargs)

    # --- CRUD DE USUÁRIO (RESTAURADO) ---

    def handle_login(self, email, password):
        conn = self._get_db_connection()
    # Confirme que a coluna da senha no seu DB se chama 'password'
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

    # O check_password_hash precisa da senha HASHED do banco
        if user and check_password_hash(user['password'], password):
        # Retorna um dicionário com os dados para a rota usar
            return {'id': user['id'], 'name': user['name']}
    
        return None # Retorna None se o login falhar

    def handle_cadastro(self):
        name = request.forms.get('name')
        email = request.forms.get('email')
        password = request.forms.get('password')

        if not all([name, email, password]):
            return self.render('login_cadastro', cadastro_error="Todos os campos são obrigatórios.")

        hashed_password = generate_password_hash(password)
        conn = self._get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return self.render('login_cadastro', cadastro_error="Este email já está cadastrado.")
        finally:
            conn.close()
        
        return self.render('login_cadastro', login_success="Cadastro realizado com sucesso! Faça o login.")
    
    def get_all_users(self):
        conn = self._get_db_connection()
        users = conn.execute('SELECT id, name, email FROM users').fetchall()
        conn.close()
        return [dict(user) for user in users]

    def get_user(self, user_id):
        conn = self._get_db_connection()
        user = conn.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None

    def handle_update_user(self, user_id):
        name = request.forms.get('name')
        email = request.forms.get('email')
        conn = self._get_db_connection()
        conn.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, user_id))
        conn.commit()
        conn.close()
        return redirect('/users') # Exemplo de redirecionamento

    def handle_delete_user(self, user_id):
        conn = self._get_db_connection()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return redirect('/users') # Exemplo de redirecionamento

    # --- CRUD DE PEDIDO ---

    def handle_criar_pedido(self):
        session = request.environ.get('beaker.session')
        dados_carrinho = request.json
        user_id = session['user_id']

        if not dados_carrinho:
            response.status = 400
            return {'error': 'O carrinho está vazio.'}

        conn = self._get_db_connection()
        try:
            preco_total = sum(item['price'] * item['qt'] for item in dados_carrinho)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pedidos (user_id, preco_total) VALUES (?, ?)", (user_id, preco_total))
            pedido_id = cursor.lastrowid
            itens_para_inserir = [
                (pedido_id, item['name'], item['qt'], item['price'], item['size'])
                for item in dados_carrinho
            ]
            cursor.executemany("INSERT INTO itens_pedido (pedido_id, nome_pizza, quantidade, preco_unitario, tamanho) VALUES (?, ?, ?, ?, ?)", itens_para_inserir)
            conn.commit()
            response.status = 201
            return {'success': True, 'pedido_id': pedido_id}
        except Exception as e:
            conn.rollback()
            response.status = 500
            print(f"Erro ao criar pedido: {e}")
            return {'error': 'Erro interno ao processar pedido.'}
        finally:
            conn.close()

    def render_meus_pedidos(self, **kwargs):
        session = kwargs.get('session', {})
        user_id = session.get('user_id')
        if not user_id: return redirect('/login')
        
        conn = self._get_db_connection()
        pedidos_db = conn.execute("SELECT * FROM pedidos WHERE user_id = ? ORDER BY data_pedido DESC", (user_id,)).fetchall()
        
        pedidos_com_itens = []
        for pedido in pedidos_db:
            itens_db = conn.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido['id'],)).fetchall()
            
            # Converte a linha do banco de dados para um dicionário
            pedido_dict = dict(pedido)
            
            
            try:
                # Tenta converter a data do formato do SQLite
                data_obj = datetime.strptime(pedido_dict['data_pedido'], '%Y-%m-%d %H:%M:%S')
                # Cria um novo campo com a data já formatada
                pedido_dict['data_formatada'] = data_obj.strftime('%d/%m/%Y às %H:%M')
            except (ValueError, TypeError):
                # Se falhar, apenas mostra a data como veio do banco
                pedido_dict['data_formatada'] = pedido_dict.get('data_pedido', '')[:16]

            pedido_dict['itens'] = [dict(item) for item in itens_db]
            pedidos_com_itens.append(pedido_dict)
            
        conn.close()
        
        # Passa a lista de pedidos, agora com a data formatada, para o template
        kwargs['pedidos'] = pedidos_com_itens
        return self.render('meus_pedidos', **kwargs)

    def handle_cancelar_pedido(self, pedido_id):
        session = request.environ.get('beaker.session')
        user_id = session['user_id']
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            pedido = cursor.execute("SELECT * FROM pedidos WHERE id = ? AND user_id = ?", (pedido_id, user_id)).fetchone()
            if not pedido:
                response.status = 404
                return {'error': 'Pedido não encontrado ou não autorizado.'}
            if pedido['status'] != 'Recebido':
                response.status = 400
                return {'error': 'Este pedido não pode mais ser cancelado.'}
            cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
            conn.commit()
            return {'success': True, 'message': 'Pedido cancelado com sucesso.'}
        except Exception as e:
            conn.rollback()
            response.status = 500
            print(f"Erro ao cancelar pedido: {e}")
            return {'error': 'Erro interno ao cancelar o pedido.'}
        finally:
            conn.close()