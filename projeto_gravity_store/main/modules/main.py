from flask import Blueprint, render_template, request, session
from database.conection import get_db_connection # IMPORT NOVO
from bs4 import BeautifulSoup

# Avisamos o Blueprint sobre as pastas relativas a ele
main_bp = Blueprint('main', __name__, 
                    template_folder='../templates', 
                    static_folder='../static',
                    static_url_path='/main_static')

# Rota trazida do app.py
@main_bp.route("/")
def home():
    userLogado = session.get('usuario_logado') 
    userDev = 0 

    if userLogado:
        conexao = None
        cursor = None
        try:
            conexao = get_db_connection()
            cursor = conexao.cursor()

            # Alterado para is_dev e para o formato %s do MySQL
            comando_sql = "SELECT is_dev FROM people WHERE id = %s"
            cursor.execute(comando_sql, (userLogado,))

            resultado = cursor.fetchone()

            if resultado:
                userDev = resultado[0]

        except Exception as e:
            # Imprimir o erro real ajuda caso dê problema de novo
            return f"Erro interno no banco (main): {e}", 500
            
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()
    
    return render_template('index.html', admin_status=userDev)

# Rota trazida do app.py
@main_bp.route("/pesquisa")
def pesquisa():
    termo = request.args.get('name') 
    return render_template("search.html", busca=termo)