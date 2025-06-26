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

@app.route('/entrar')
def page_entrar():
    return ctl.render('login_cadastro')

@app.route('/login', method='POST')
def process_login():
    return ctl.handle_login()

@app.route('/cadastro', method='POST')
def process_cadastro():
    return ctl.handle_cadastro()

#-----------------------------------------------------------------------------


if __name__ == '__main__':

    run(app, host='localhost', port=8080, debug=True)
