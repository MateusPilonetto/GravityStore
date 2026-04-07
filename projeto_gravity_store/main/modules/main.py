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
    apps = []

    conexao = None
    cursor = None
    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()

        if userLogado:
            comando_sql = "SELECT is_dev FROM people WHERE id = %s"
            cursor.execute(comando_sql, (userLogado,))
            resultado = cursor.fetchone()
            if resultado:
                userDev = resultado[0]

        comando_apps = "SELECT id, nome, dev_name, category, size_mb, icon_path, link_github, link_download FROM apps ORDER BY data_envio DESC LIMIT 10"
        cursor.execute(comando_apps)
        
        colunas = [desc[0] for desc in cursor.description]
        apps_db = cursor.fetchall()
        apps = [dict(zip(colunas, app)) for app in apps_db]

    except Exception as e:
        return f"Erro interno na base de dados (main): {e}", 500
        
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
    
    return render_template('index.html', admin_status=userDev, apps=apps)

@main_bp.route("/pesquisa")
def pesquisa():
    conexao = None
    cursor = None
    try:
        termo = request.args.get('pesquisa') 
        conexao = get_db_connection()
        cursor = conexao.cursor()

        # Trocamos 'termo' por ? (Assumindo SQLite)
        sql = "SELECT nome, description FROM apps WHERE LOWER(nome) = LOWER(?);"
        
        # Adicionamos a vírgula para transformar em tupla
        cursor.execute(sql, (termo,))

        # Mudei o nome da variável de 'usuario' para 'app_resultado' por semântica
        app_resultado = cursor.fetchone() 
        
        # Apenas para testar o retorno:
        if app_resultado:
            return f"App encontrado: {app_resultado['nome']}" # ou app_resultado[0] dependendo de como o cursor está configurado
        else:
            return "Nenhum app encontrado com esse nome exato."
        
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()