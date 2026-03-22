from flask import Blueprint, request, render_template, session, redirect, url_for
from hashlib import sha256
import pyodbc

login_bp = Blueprint('login', __name__, 
                     template_folder='../templates', 
                     static_folder='../static',
                     static_url_path='/login_static') # <-- Adicione isso

servidor = r'localhost\SQLEXPRESS' 
banco_de_dados = 'gravity_store_people'

string_conexao = (
    r'Driver={ODBC Driver 17 for SQL Server};'
    f'Server={servidor};'
    f'Database={banco_de_dados};'
    r'Trusted_Connection=yes;'
)


# Rota trazida do app.py
@login_bp.route("/login")
def login():
    return render_template("login.html")

@login_bp.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('main.home')) 


@login_bp.route('/login_auth', methods=['POST'])
def login_auth():

    email_digitado = request.form['email']
    senha_digitada = request.form['senha']

    hash_senha = sha256(senha_digitada.encode())
    senha_criptografada = hash_senha.hexdigest()

    conexao = None
    cursor = None
    try:
        conexao = pyodbc.connect(string_conexao)
        cursor = conexao.cursor()

        sql = "SELECT * FROM people WHERE email = ? AND senha = ?"
        cursor.execute(sql, (email_digitado, senha_criptografada))

        usuario = cursor.fetchone()
        
        if usuario:
            session['usuario_logado'] = usuario[0] 
            session['nome_usuario'] = usuario[1]   
            
          
            return redirect(url_for('main.home')) 
        else:
            return render_template('login.html', erro="E-mail ou senha incorretos!")
        
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
        
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
