import json
from app.controllers.application import Application
from bottle import Bottle, route, run, request, static_file
from bottle import redirect, template, response


app = Bottle()
ctl = Application()


#-----------------------------------------------------------------------------
# Rotas:

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static')

@app.route('/helper')
def helper(info= None):
    return ctl.render('helper')




#-----------------------------------------------------------------------------
# Suas rotas aqui:
@app.route('/pagina', methods=['GET'])
def action_pagina():
    return ctl.render('pagina')

@app.route('/compra', methods=['GET'])
def action_pagina():
    return ctl.render('compra')

@app.route('/entrar')
def page_entrar():
    return ctl.render('login_cadastro')

@app.route('/login', method='POST')
def process_login():
    return ctl.handle_login()

@app.route('/cadastro', method='POST')
def process_cadastro():
    return ctl.handle_cadastro()

@app.route('/users', method='GET')
def api_get_all_users():
    """ Rota para listar todos os usuários. """
    users = ctl.get_all_users()
    return json.dumps(users)

@app.route('/users/<user_id>', method='GET')
def api_get_user(user_id):
    """ Rota para obter um usuário específico. """
    user = ctl.get_user(user_id)
    if user:
        return json.dumps(user)
    return {"error": "Usuário não encontrado"}

@app.route('/users/<user_id>', method='POST') 
def api_update_user(user_id):
    """ Rota para atualizar um usuário. """
    return ctl.handle_update_user(user_id)

@app.route('/users/<user_id>/delete', method='POST') 
def api_delete_user(user_id):
    """ Rota para deletar um usuário. """
    return ctl.handle_delete_user(user_id)

#-----------------------------------------------------------------------------


if __name__ == '__main__':

    run(app, host='localhost', port=8080, debug=True)
