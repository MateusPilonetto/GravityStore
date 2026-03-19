from flask import Blueprint, request, render_template, session, redirect, url_for
import mysql.connector
from hashlib import sha256

login_bp = Blueprint('login', __name__, 
                     template_folder='../templates', 
                     static_folder='../static',
                     static_url_path='/login_static') # <-- Adicione isso

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cadastro"
)

# Rota trazida do app.py
@login_bp.route("/login")
def login():
    return render_template("login.html")

@login_bp.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('main.home')) # Melhor usar redirect com url_for
    
@login_bp.route("/login_auth", methods=['POST'])
def login_auth():
    # Removido o 'email' daqui, vamos pegar do formulário
    email = request.form.get('email') # Pega o e-mail do formulário
    senha_digitada = request.form.get('senha') # Pega a senha do formulário

    hash_senha_digitada = sha256(senha_digitada.encode())
    senha_C = hash_senha_digitada.digest()
    
    cursor = None
    try:
        cursor = db.cursor(dictionary=True) # Usar dictionary=True facilita muito!
        
        # 1. Buscamos o usuário pelo e-mail
        sql = "SELECT * FROM people WHERE email = %s"
        cursor.execute(sql, (email,)) # A vírgula mágica aqui!
        
        usuario = cursor.fetchone()
        
        # 2. Verificamos se o usuário existe e se a senha bate
        if usuario:
            if usuario['senha'] == senha_C:
                session['usuario_logado'] = usuario['nome']
                return redirect(url_for('main.home'))
                
            else:
                return render_template("login.html", erro="Senha incorreta!")
        else:
            return render_template("login.html", erro="E-mail não encontrado!")

    except Exception as e:
        return f"Erro na consulta: {e}"
    
    finally:
        if cursor:
            cursor.close()

