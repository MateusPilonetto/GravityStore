from flask import Blueprint, render_template, request, session
import pyodbc
from bs4 import BeautifulSoup

# Avisamos o Blueprint sobre as pastas relativas a ele
main_bp = Blueprint('main', __name__, 
                    template_folder='../templates', 
                    static_folder='../static',
                    static_url_path='/main_static')



# Botao HTML

servidor = r'localhost\SQLEXPRESS'
banco_de_dados = 'gravity_store_people'
string_conexao = (
    r'Driver={ODBC Driver 17 for SQL Server};'
    f'Server={servidor};'
    f'Database={banco_de_dados};'
    r'Trusted_Connection=yes;'
)


# Rota trazida do app.py
@main_bp.route("/")
def home():

    userLogado = session.get('usuario_logado') 

    userDev = 0 

    if userLogado:
        try:
            conexao = pyodbc.connect(string_conexao)
            cursor = conexao.cursor()

            comando_sql = "SELECT developer FROM people WHERE id = ?;"
            cursor.execute(comando_sql, (userLogado,))

            resultado = cursor.fetchone()

            if resultado:
                userDev = resultado[0]

        except Exception as e:
            return "Erro interno no servidor.", 500
            
        finally:
            if 'conexao' in locals():
                conexao.close()
    
    return render_template('index.html', admin_status=userDev)


# Rota trazida do app.py
@main_bp.route("/pesquisa")
def pesquisa():
    termo = request.args.get('name') 
    return render_template("search.html", busca=termo)