from flask import Blueprint, request, render_template
import mysql.connector

# Criamos o Blueprint (damos um nome interno 'register_bp')
register_bp = Blueprint('register', __name__)

# Configuração do Banco (fica aqui dentro deste arquivo mesmo)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cadastro"
)


# Criamos a rota usando o Blueprint, NÃO o app
@register_bp.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email']
    senha = request.form['senha']
    senha_confirmacao = request.form['senha_confirmacao']

    if senha != senha_confirmacao:
        return(render_template('register.html', erro="As senhas não são iguais!!!"))

    else:

        try:
            cursor = db.cursor()
            sql = "INSERT INTO people (nome, username, phone, email, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql)
            db.commit()
            return render_template("login.html")
    
        except Exception as e:
            return f"Ocorreu um erro no banco: {e}"
        
        finally:
        # 3. O bloco 'finally' SEMPRE roda no final, dando erro ou não.
        # Aqui checamos: se o cursor não for mais 'None', nós o fechamos.
            if cursor:
                cursor.close()