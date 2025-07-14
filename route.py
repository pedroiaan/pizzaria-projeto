import json
from app.controllers.application import Application
from bottle import Bottle, run, request, static_file, redirect, template, response
from beaker.middleware import SessionMiddleware

# --- CONFIGURAÇÃO DA APLICAÇÃO E SESSÃO ---
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 3600,
    'session.data_dir': './.session_data',
    'session.auto': True
}
app = Bottle()
app_with_session = SessionMiddleware(app, session_opts) # Envolve o app com o middleware de sessão
ctl = Application()

# --- DECORATOR PARA EXIGIR LOGIN ---
def login_required(fn):
    def check_login(*args, **kwargs):
        session = request.environ.get('beaker.session')
        # Verifica se a sessão existe e se o user_id está nela
        if not session or 'user_id' not in session:
            if request.path.startswith('/api/'):
                response.status = 401
                return {'error': 'Autenticação necessária.'}
            # Salva uma mensagem para exibir na página de login
            session['flash_message'] = ('Você precisa estar logado para acessar essa página.', 'warning')
            session.save()
            return redirect('/login')
        return fn(*args, **kwargs)
    return check_login

# --- ROTAS PRINCIPAIS E ESTÁTICAS ---
@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static/')

@app.route('/')
def action_index():
    return redirect('/pagina')

@app.route('/pagina')
def action_pagina():
    session = request.environ.get('beaker.session', {})
    return ctl.render('pagina', session=session)

# --- ROTAS DE AUTENTICAÇÃO ---

# ROTA PARA MOSTRAR A PÁGINA DE LOGIN (MÉTODO GET)
@app.route('/login', method='GET')
def show_login_page():
    session = request.environ.get('beaker.session', {})
    flash_message = session.pop('flash_message', None)
    return ctl.render('login_cadastro', error=flash_message)

# ROTA PARA PROCESSAR O FORMULÁRIO DE LOGIN (MÉTODO POST)
@app.route('/login', method='POST')
def process_login_form():
    email = request.forms.get('email')
    password = request.forms.get('password')
    user_data = ctl.handle_login(email, password)

    if user_data:
        session = request.environ.get('beaker.session')
        session['user_id'] = user_data['id']
        session['user'] = user_data['name']
        session.save()
        return redirect('/compra')
    else:
        return ctl.render('login_cadastro', login_error="Email ou senha inválidos.")

@app.route('/cadastro', method='POST')
def process_cadastro():
    return ctl.handle_cadastro()

@app.route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    if session:
        session.delete()
    return redirect('/login')

# --- ROTAS DE COMPRA E PEDIDOS ---
@app.route('/compra')
@login_required
def action_compra():
    session = request.environ.get('beaker.session')
    return ctl.render('compra', session=session)

@app.route('/meus-pedidos')
@login_required
def pagina_meus_pedidos():
    session = request.environ.get('beaker.session')
    return ctl.render_meus_pedidos(session=session)

# --- ROTAS DA API ---
@app.route('/api/pedidos/criar', method='POST')
@login_required
def api_criar_pedido():
    return ctl.handle_criar_pedido()

@app.route('/api/pedidos/cancelar/<pedido_id:int>', method='POST')
@login_required
def api_cancelar_pedido(pedido_id):
    return ctl.handle_cancelar_pedido(pedido_id)

# --- Execução da Aplicação ---
if __name__ == '__main__':
    run(app=app_with_session, host='localhost', port=8080, debug=True, reloader=True)