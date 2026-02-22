from flask import Flask, render_template, request, url_for, session, redirect
# O Python vai procurar o arquivo 'register.py' e puxar a variável 'register_bp'
from modules.register import register_bp
from modules.login import login_bp
from modules.main import main_bp

app = Flask(__name__)

app.secret_key = 'chave_segura'

# Aqui nós colamos as rotas do outro arquivo no aplicativo principal
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(main_bp)


# Rota para a Página Inicial
@app.route("/")
def home():
    return render_template("index.html")

# Rota para Login
@app.route("/login")
def login():
    return render_template("login.html")

# Rota para Registro
@app.route("/register")
def register():
    return render_template("register.html")

# Rota para Pesquisa
@app.route("/pesquisa")
def pesquisa():
    termo = request.args.get('name') 
    return render_template('search.html', busca=termo)


if __name__ == "__main__":
    app.run(debug=True)