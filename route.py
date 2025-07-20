# /app/route.py

import json
from app.controllers.application import Application
from bottle import Bottle, run, request, static_file, redirect, template, response
from beaker.middleware import SessionMiddleware
import socketio
import eventlet

# --- Configurações Iniciais ---
session_opts = {'session.type': 'file', 'session.cookie_expires': 3600, 'session.data_dir': './.session_data', 'session.auto': True}
app = Bottle()
app_with_session = SessionMiddleware(app, session_opts)
sio = socketio.Server(async_mode='eventlet')
main_app = socketio.WSGIApp(sio, app_with_session)

# --- Inicialização do Controller com Socket.IO ---
ctl = Application(sio=sio)

# --- Decorator de Login ---
def login_required(fn):
    def check_login(*args, **kwargs):
        session = request.environ.get('beaker.session')
        if not session or 'user_id' not in session:
            if request.path.startswith('/api/'):
                response.status = 401
                return json.dumps({'error': 'Autenticação necessária.'})
            session['flash_message'] = ('Você precisa estar logado para acessar essa página.', 'warning')
            session.save()
            return redirect('/login')
        return fn(*args, **kwargs)
    return check_login

# --- Eventos WebSocket ---
@sio.event
def connect(sid, environ): print(f'✅ Cliente WebSocket Conectado: {sid}')
@sio.event
def disconnect(sid): print(f'Cliente WebSocket Desconectado: {sid}')

# --- Rotas Principais e Estáticas ---
@app.route('/static/<filepath:path>')
def serve_static(filepath): return static_file(filepath, root='./app/static/')

@app.route('/')
def action_index(): return redirect('/pagina')

@app.route('/pagina')
def action_pagina(): return ctl.render('pagina')

# --- Rotas de Autenticação ---
@app.route('/login', method='GET')
def show_login_page(): return ctl.render('login_cadastro')

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
        # ✅ O "ARROZ COM FEIJÃO": REDIRECIONA PARA /compra
        return redirect('/compra')
    else:
        return ctl.render('login_cadastro', login_error="Email ou senha inválidos.")

@app.route('/cadastro', method='POST')
def process_cadastro(): return ctl.handle_cadastro()

@app.route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    if session: session.delete()
    return redirect('/login')

# --- ROTAS DA APLICAÇÃO ---
@app.route('/compra')
@login_required
def pagina_compra():
    """ Rota para a página de finalização de compra. """
    return ctl.render('compra')

@app.route('/meus-pedidos')
@login_required
def pagina_meus_pedidos(): return ctl.render_meus_pedidos()

@app.route('/kitchen')
@login_required
def kitchen_page(): return ctl.render('kitchen')

# --- ROTAS DA API ---
@app.route('/api/pedidos/criar', method='POST')
@login_required
def api_criar_pedido(): return ctl.handle_criar_pedido()

@app.route('/api/pedidos/cancelar/<pedido_id:int>', method='POST')
@login_required
def api_cancelar_pedido(pedido_id): return ctl.handle_cancelar_pedido(pedido_id)

# --- EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    print("🚀 Iniciando servidor com Eventlet na porta 8080...")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), main_app)