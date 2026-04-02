from flask import Blueprint, request, render_template, redirect, url_for
from hashlib import sha256
from database.conection import get_db_connection

register_bp = Blueprint('register', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/register_static')

@register_bp.route("/register")
def register():
    return render_template("register.html")

@register_bp.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email']
    senha = request.form['senha']
    senha_confirmacao = request.form['senha_confirmacao']

    if senha != senha_confirmacao:
        return render_template('register.html', erro="As senhas não são iguais!!!")

    hash_senha = sha256(senha.encode())
    armazenar_senha = hash_senha.hexdigest()

    conexao = None
    cursor = None
    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()
        
        # O SQL volta a ter apenas 5 valores. O banco colocará o is_dev como 0 automaticamente!
        sql = "INSERT INTO people (nome, username, phone, email, senha) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (nome, username, phone, email, armazenar_senha))
        
        conexao.commit()
        
        return render_template("login.html")
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()