from flask import Blueprint, request, render_template, redirect, url_for, session
import pyodbc
from bs4 import BeautifulSoup
from database.conection import get_db_connection

dev_bp = Blueprint('dev', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/dev_static')

@dev_bp.route("/dev")
def dev():

    nome = request.form['nome']
    devName = request.form['devname']
    linkG  = request.form['linkG']
    linkA  = request.form['linkA']
    description  = request.form['description']
    category  = request.form['category']
    version  = request.form['version']
    size  = request.form['size']
    iconApp  = request.form['iconApp']
    screenshots  = request.form['screenshots']

    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()
        
        # O SQL volta a ter apenas 5 valores. O banco colocará o is_dev como 0 automaticamente!
        sql = "INSERT INTO people (nome, devName, linkG, linkA, description, category, version, size, iconApp, screenshots) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (nome, devName, linkG, linkA, description, category, version, size, iconApp, screenshots))
        
        conexao.commit()
        
        return render_template("dev.html")
    except Exception as e:
        return f"Ocorreu um erro no banco: {e}"
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()