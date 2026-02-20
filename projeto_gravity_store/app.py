from flask import Flask, render_template, url_for, request

app = Flask(__name__)

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