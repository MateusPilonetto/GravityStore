from flask import Blueprint, request, render_template, redirect, url_for
import mysql.connector

register_bp = Blueprint('register', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/register_static') # <-- Adicione isso

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cadastro"
)

# Rota trazida do app.py
@register_bp.route("/register")
def register():
    return render_template("register.html")

@register_bp.route('/submit', methods=['POST'])
def submit():
    # Mantenha todo o seu código original de INSERT e cursor aqui...
    nome = request.form['nome']
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email']
    senha = request.form['senha']
    senha_confirmacao = request.form['senha_confirmacao']

    if senha != senha_confirmacao:
        return(render_template('register.html', erro="As senhas não são iguais!!!"))

    else:

        cursor = None
        try:
            cursor = db.cursor()
            sql = "INSERT INTO people (nome, username, phone, email, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nome, username, phone, email, senha))
            db.commit()
            return render_template("login.html")
    
        except Exception as e:
            return f"Ocorreu um erro no banco: {e}"
        
        finally:
            # 3. O bloco 'finally' SEMPRE roda no final, dando erro ou não.
            # Aqui checamos: se o cursor não for mais 'None', nós o fechamos.
            if cursor:
                cursor.close()