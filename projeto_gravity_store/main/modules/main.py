from flask import Blueprint, render_template, request, session
from database.conection import get_db_connection
from bs4 import BeautifulSoup

main_bp = Blueprint('main', __name__, 
                    template_folder='../templates', 
                    static_folder='../static',
                    static_url_path='/main_static')

@main_bp.route("/")
def home():
    userLogado = session.get('usuario_logado') 
    userDev = 0 
    apps = [] # Lista vazia para guardar os apps

    conexao = None
    cursor = None
    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()

        # 1. Verifica se o utilizador é Dev
        if userLogado:
            comando_sql = "SELECT is_dev FROM people WHERE id = %s"
            cursor.execute(comando_sql, (userLogado,))
            resultado = cursor.fetchone()
            if resultado:
                userDev = resultado[0]

        # 2. NOVO: Vai buscar os últimos 10 aplicativos adicionados
        comando_apps = "SELECT id, nome, dev_name, category, size_mb, icon_path, link_download FROM apps ORDER BY data_envio DESC LIMIT 10"
        cursor.execute(comando_apps)
        
        # Converte o resultado para um formato de "Dicionário" (mais fácil para o HTML ler)
        colunas = [desc[0] for desc in cursor.description]
        apps_db = cursor.fetchall()
        apps = [dict(zip(colunas, app)) for app in apps_db]

    except Exception as e:
        return f"Erro interno na base de dados (main): {e}", 500
        
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
    
    # Envia a lista 'apps' para a página HTML
    return render_template('index.html', admin_status=userDev, apps=apps)

@main_bp.route("/pesquisa")
def pesquisa():
    termo = request.args.get('name') 
    return render_template("search.html", busca=termo)