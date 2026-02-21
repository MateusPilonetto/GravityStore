from flask import Blueprint, request, render_template, session, redirect, url_for, Flask
import mysql.connector

login_bp = Blueprint('login', __name__)
app = Flask(__name__)



db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cadastro"
)

@login_bp.route('/logout')
def logout():
    session.clear() # Limpa toda a sessão
    return render_template("index.html")
    

@login_bp.route("/login_auth", methods=['POST'])
def login_auth(): # Removido o 'email' daqui, vamos pegar do formulário
    email = request.form.get('email') # Pega o e-mail do formulário
    senha_digitada = request.form.get('senha') # Pega a senha do formulário
    
    cursor = None
    try:
        cursor = db.cursor(dictionary=True) # Usar dictionary=True facilita muito!
        
        # 1. Buscamos o usuário pelo e-mail
        sql = "SELECT * FROM people WHERE email = %s"
        cursor.execute(sql, (email,)) # A vírgula mágica aqui!
        
        usuario = cursor.fetchone()
        
        # 2. Verificamos se o usuário existe e se a senha bate
        if usuario:
            if usuario['senha'] == senha_digitada:
                session['usuario_logado'] = usuario['nome']
                return render_template("index.html")
                
            else:
                return render_template("login.html", erro="Senha incorreta!")
        else:
            return render_template("login.html", erro="E-mail não encontrado!")

    except Exception as e:
        return f"Erro na consulta: {e}"
    
    finally:
        if cursor:
            cursor.close()

