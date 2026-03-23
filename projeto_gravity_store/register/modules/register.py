from flask import Blueprint, request, render_template, redirect, url_for
import pyodbc
from hashlib import sha256

register_bp = Blueprint('register', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/register_static')


servidor = r'localhost\SQLEXPRESS'
banco_de_dados = 'gravity_store_people'
string_conexao = (
    r'Driver={ODBC Driver 17 for SQL Server};'
    f'Server={servidor};'
    f'Database={banco_de_dados};'
    r'Trusted_Connection=yes;'
)

try:
    conexao = pyodbc.connect(string_conexao)
    print("Deu certo")
except:
    print("Não deu certo")

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

    hash_senha = sha256(senha.encode())
    armazenar_senha = hash_senha.hexdigest()

    if senha != senha_confirmacao:
        return render_template('register.html', erro="As senhas não são iguais!!!")

    else:
        conexao = None
        cursor = None
        try:
            conexao = pyodbc.connect(string_conexao)
            cursor = conexao.cursor()
            
            sql = "INSERT INTO people (nome, username, phone, email, senha) VALUES (?, ?, ?, ?, ?)"

            cursor.execute(sql, (nome, username, phone, email, armazenar_senha))

            conexao.commit()
            
            return render_template("login.html")
    
        except Exception as e:
            return f"Ocorreu um erro no banco: {e}"
        
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()