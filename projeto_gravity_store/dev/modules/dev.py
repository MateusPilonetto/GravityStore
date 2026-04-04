import os
import json
from flask import Blueprint, request, render_template, redirect, url_for, session

from werkzeug.utils import secure_filename 
from database.conection import get_db_connection

dev_bp = Blueprint('dev', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/dev_static')

UPLOAD_FOLDER = os.path.join('dev', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

@dev_bp.route("/dev")
def dev():
    return render_template("dev.html")

@dev_bp.route("/submit_app", methods=['POST'])
def apps():
    print("===== DADOS RECEBIDOS DO FORMULÁRIO =====")
    print("Textos (Form):", request.form)
    print("Arquivos (Files):", request.files)
    print("=========================================")

    nome = request.form.get('nome', '')
    dev_name = request.form.get('devName', '') 
    link_github  = request.form.get('linkG', '')
    link_download  = request.form.get('linkA', '')
    description  = request.form.get('description', '')
    category  = request.form.get('category', '')
    version  = request.form.get('version', '')
    size_mb  = request.form.get('size', 0)

    if not nome or not dev_name:
        return "Erro: O nome do app ou o nome do dev estão faltando!", 400
    
    icon_app = request.files['iconApp']
    icon_filename = ""
    
    if icon_app and icon_app.filename != '':
        icon_filename = secure_filename(icon_app.filename)
        icon_path = os.path.join(UPLOAD_FOLDER, icon_filename)
        icon_app.save(icon_path)

    screenshots = request.files.getlist('screenshots')
    screenshots_filenames = []
    
    for screenshot in screenshots:
        if screenshot and screenshot.filename != '':
            filename = secure_filename(screenshot.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            screenshot.save(file_path)
            screenshots_filenames.append(filename)
    
    screenshots_json = json.dumps(screenshots_filenames)

    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()
        
        sql = """
            INSERT INTO apps 
            (nome, dev_name, link_github, link_download, description, category, version, size_mb, icon_path, screenshots_paths) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (nome, dev_name, link_github, link_download, description, category, version, size_mb, icon_filename, screenshots_json)
        
        cursor.execute(sql, valores)
        conexao.commit()
        
        return render_template("dev.html", sucesso="App enviado com sucesso!")
        
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
    finally:
        if 'cursor' in locals() and cursor: 
            cursor.close()
        if 'conexao' in locals() and conexao: 
            conexao.close()

@dev_bp.route("/app_list")
def app_list():
    pesquisa = request.args.get('q', '')

    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()

        if pesquisa:
            comando_apps = """
                SELECT id, nome, dev_name, category, size_mb, icon_path, link_github, link_download 
                FROM apps 
                WHERE nome LIKE %s OR dev_name LIKE %s OR category LIKE %s
                ORDER BY data_envio DESC
            """
            termo = f"%{pesquisa}%"
            cursor.execute(comando_apps, (termo, termo, termo))
        else:
            comando_apps = "SELECT id, nome, dev_name, category, size_mb, icon_path, link_github, link_download FROM apps ORDER BY data_envio DESC LIMIT 10"
            cursor.execute(comando_apps)
        
        
        colunas = [desc[0] for desc in cursor.description]
        apps_db = cursor.fetchall()
        apps = [dict(zip(colunas, app)) for app in apps_db]

       
        return render_template("apps.html", apps=apps, pesquisa=pesquisa)

    except Exception as e:
        return f"Erro interno na base de dados: {e}", 500
        
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conexao' in locals() and conexao: conexao.close()


# ROTA PARA DELETAR O APP
@dev_bp.route("/delete_app/<int:app_id>")
def delete_app(app_id):
    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()
        
        cursor.execute("DELETE FROM apps WHERE id = %s", (app_id,))
        conexao.commit()
        
        return redirect(url_for('dev.app_list'))
    except Exception as e:
        return f"Erro ao deletar o aplicativo: {e}", 500
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conexao' in locals() and conexao: conexao.close()



@dev_bp.route("/edit_app/<int:app_id>", methods=['GET', 'POST'])
def edit_app(app_id):
    conexao = get_db_connection()
    cursor = conexao.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome', '')
        dev_name = request.form.get('devName', '') 
        link_github  = request.form.get('linkG', '')
        link_download  = request.form.get('linkA', '')
        description  = request.form.get('description', '')
        category  = request.form.get('category', '')
        version  = request.form.get('version', '')
        size_mb  = request.form.get('size', 0)

        valores = [nome, dev_name, link_github, link_download, description, category, version, size_mb]
        sql_update_icon = ""

        icon_app = request.files.get('iconApp')
        if icon_app and icon_app.filename != '':
            icon_filename = secure_filename(icon_app.filename)
            icon_path = os.path.join(UPLOAD_FOLDER, icon_filename)
            icon_app.save(icon_path)
            sql_update_icon = ", icon_path = %s"
            valores.append(icon_filename)
        
        valores.append(app_id)

        try:
            sql = f"""
                UPDATE apps 
                SET nome = %s, dev_name = %s, link_github = %s, link_download = %s, 
                    description = %s, category = %s, version = %s, size_mb = %s {sql_update_icon}
                WHERE id = %s
            """
            cursor.execute(sql, tuple(valores))
            conexao.commit()
            return redirect(url_for('dev.app_list'))
        except Exception as e:
            return f"Erro ao atualizar o aplicativo: {e}", 500
        finally:
            cursor.close()
            conexao.close()

    else:
        try:
            cursor.execute("SELECT * FROM apps WHERE id = %s", (app_id,))
            colunas = [desc[0] for desc in cursor.description]
            app_db = cursor.fetchone()
            
            if app_db:
                app = dict(zip(colunas, app_db))
                return render_template("edit_app.html", app=app)
            else:
                return "App não encontrado", 404
        except Exception as e:
            return f"Erro ao carregar dados do aplicativo: {e}", 500
        finally:
            cursor.close()
            conexao.close()