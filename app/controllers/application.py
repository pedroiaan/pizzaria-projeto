# /app/controllers/application.py

import sqlite3
import json
from bottle import template, request, redirect, response
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Application():
    def __init__(self, sio=None):
        self.db_name = 'pizzaria.db'
        self.sio = sio
        self.init_db()

    def init_db(self):
        # O seu init_db está correto, não precisa de alterações
        conn = self._get_db_connection()
        cursor = conn.cursor()
        # ... (código para criar tabelas) ...
        conn.commit()
        conn.close()

    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def render(self, page_name, **kwargs):
        session = kwargs.get('session', request.environ.get('beaker.session', {}))
        user_id = session.get('user_id')
        user_name = session.get('user')
        is_logged_in = user_id is not None
        kwargs.update({
            'is_logged_in': is_logged_in,
            'user_name': user_name,
            'session': session
        })
        if not page_name.endswith('.html'):
            page_name += '.html'
        return template(f'app/views/html/{page_name}', **kwargs)

    def handle_login(self, email, password):
        # O seu handle_login está correto
        conn = self._get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            return {'id': user['id'], 'name': user['name']}
        return None

    def handle_cadastro(self):
        # O seu handle_cadastro está correto
        # ... (seu código de cadastro) ...
        return redirect('/login')

    def handle_criar_pedido(self):
        session = request.environ.get('beaker.session')
        dados_carrinho = request.json
        user_id = session['user_id']
        user_name = session['user']
        if not dados_carrinho:
            response.status = 400
            return json.dumps({'error': 'O carrinho está vazio.'})
        conn = self._get_db_connection()
        try:
            preco_total = sum(item['price'] * item['qt'] for item in dados_carrinho)
            itens_para_inserir = [(item['name'], item['qt'], item['price'], item['size']) for item in dados_carrinho]
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pedidos (user_id, preco_total) VALUES (?, ?)", (user_id, preco_total))
            pedido_id = cursor.lastrowid
            for nome, qt, preco, tamanho in itens_para_inserir:
                cursor.execute("INSERT INTO itens_pedido (pedido_id, nome_pizza, quantidade, preco_unitario, tamanho) VALUES (?, ?, ?, ?, ?)", (pedido_id, nome, qt, preco, tamanho))
            conn.commit()
            dados_para_notificacao = {'id': pedido_id, 'cliente': user_name, 'total': f'{preco_total:.2f}', 'items': [{'nome': nome, 'quantidade': qt, 'tamanho': tamanho} for nome, qt, preco, tamanho in itens_para_inserir]}
            if self.sio:
                self.sio.emit('novo_pedido', dados_para_notificacao)
                print(f"✅ Evento 'novo_pedido' emitido: {dados_para_notificacao}")
            response.status = 201
            return json.dumps(dados_para_notificacao)
        except Exception as e:
            conn.rollback()
            response.status = 500
            print(f"❌ Erro ao criar pedido: {e}")
            return json.dumps({'error': 'Erro interno.'})
        finally:
            conn.close()

    def render_meus_pedidos(self):
        # O seu render_meus_pedidos está correto
        session = request.environ.get('beaker.session', {})
        user_id = session.get('user_id')
        if not user_id: return redirect('/login')
        # ... (seu código para buscar e formatar os pedidos) ...
        conn = self._get_db_connection()
        pedidos_db = conn.execute("SELECT * FROM pedidos WHERE user_id = ? ORDER BY data_pedido DESC", (user_id,)).fetchall()
        pedidos_com_itens = []
        for pedido in pedidos_db:
            itens_db = conn.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido['id'],)).fetchall()
            pedido_dict = dict(pedido)
            try:
                data_obj = datetime.strptime(pedido_dict['data_pedido'], '%Y-%m-%d %H:%M:%S')
                pedido_dict['data_formatada'] = data_obj.strftime('%d/%m/%Y às %H:%M')
            except (ValueError, TypeError):
                pedido_dict['data_formatada'] = pedido_dict.get('data_pedido', '')[:16]
            pedido_dict['itens'] = [dict(item) for item in itens_db]
            pedidos_com_itens.append(pedido_dict)
        conn.close()
        return self.render('meus_pedidos', pedidos=pedidos_com_itens, session=session)

    def handle_cancelar_pedido(self, pedido_id):
        # O seu handle_cancelar_pedido está correto
        # ... (seu código para cancelar pedidos) ...
        return json.dumps({'success': True})