import os
import json
from flask import Blueprint, request, render_template, redirect, url_for, session

from werkzeug.utils import secure_filename 
from database.conection import get_db_connection

dev_bp = Blueprint('dev', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/dev_static')

# Define a pasta onde as imagens serão salvas
UPLOAD_FOLDER = os.path.join('dev', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Cria a pasta se não existir

@dev_bp.route("/dev")
def dev():
    return render_template("dev.html")

# 1. Adicionado methods=['POST']
@dev_bp.route("/submit", methods=['POST'])
def apps():
    # 1. RASTREADOR: Imprime no terminal o que está chegando
    print("===== DADOS RECEBIDOS DO FORMULÁRIO =====")
    print("Textos (Form):", request.form)
    print("Arquivos (Files):", request.files)
    print("=========================================")

    # 2. Captura super segura (Se não vier nada, ele salva como string vazia ou None)
    nome = request.form.get('nome', '')
    dev_name = request.form.get('devName', '') 
    link_github  = request.form.get('linkG', '')
    link_download  = request.form.get('linkA', '')
    description  = request.form.get('description', '')
    category  = request.form.get('category', '')
    version  = request.form.get('version', '')
    size_mb  = request.form.get('size', 0)

    # Verifica se algum campo essencial está vazio
    if not nome or not dev_name:
        return "Erro: O nome do app ou o nome do dev estão faltando!", 400

    # Continua o código dos arquivos que te passei antes...
    
    # 3 e 4. Pegando e salvando os arquivos (imagens) via request.files
    icon_app = request.files['iconApp']
    icon_filename = ""
    
    if icon_app and icon_app.filename != '':
        icon_filename = secure_filename(icon_app.filename)
        icon_path = os.path.join(UPLOAD_FOLDER, icon_filename)
        icon_app.save(icon_path) # Salva a imagem na pasta

    screenshots = request.files.getlist('screenshots')
    screenshots_filenames = []
    
    for screenshot in screenshots:
        if screenshot and screenshot.filename != '':
            filename = secure_filename(screenshot.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            screenshot.save(file_path) # Salva a imagem na pasta
            screenshots_filenames.append(filename)
    
    # Transforma a lista de screenshots em um formato JSON para o banco de dados
    screenshots_json = json.dumps(screenshots_filenames)

    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()
        
        # 5 e 6. Corrigido para as 10 colunas e os 10 marcadores (%s)
        sql = """
            INSERT INTO apps 
            (nome, dev_name, link_github, link_download, description, category, version, size_mb, icon_path, screenshots_paths) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (nome, dev_name, link_github, link_download, description, category, version, size_mb, icon_filename, screenshots_json)
        
        cursor.execute(sql, valores)
        conexao.commit()
        
        # Redireciona para evitar reenvio de formulário ao atualizar a página
        return render_template("dev.html", sucesso="App enviado com sucesso!")
        
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
    finally:
        if 'cursor' in locals() and cursor: 
            cursor.close()
        if 'conexao' in locals() and conexao: 
            conexao.close()