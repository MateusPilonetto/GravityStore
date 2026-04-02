from flask import Blueprint, request, render_template, session, redirect, url_for
from hashlib import sha256
from database.conection import get_db_connection

login_bp = Blueprint('login', __name__, 
                     template_folder='../templates', 
                     static_folder='../static',
                     static_url_path='/login_static')

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
        conexao = get_db_connection()
        cursor = conexao.cursor()

        sql = "SELECT * FROM people WHERE email = %s AND senha = %s"
        cursor.execute(sql, (email_digitado, senha_criptografada))

        usuario = cursor.fetchone()
        
        if usuario:
            lembrar = request.form.get('remember')
            
            
            print(f"--- DEBUG: Valor do checkbox Lembrar: {lembrar} ---")
            
            if lembrar:
                session.permanent = True
            else:
                session.permanent = False
            
            session.modified = True 

            session['usuario_logado'] = usuario[0] 
            session['nome_usuario'] = usuario[1]
            
            # ======== ADICIONADO: SALVA O STATUS DE DEV ========
            session['is_dev'] = usuario[6]
            # ===================================================

            return redirect(url_for('main.home')) 
        else:
            return render_template('login.html', erro="E-mail ou senha incorretos!")
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()