from flask import Blueprint, request, render_template, redirect, url_for, session
import pyodbc
from bs4 import BeautifulSoup

dev_bp = Blueprint('dev', __name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        static_url_path='/dev_static')

servidor = r'localhost\SQLEXPRESS'
banco_de_dados = 'aplications'
string_conexao = (
    r'Driver={ODBC Driver 17 for SQL Server};'
    f'Server={servidor};'
    f'Database={banco_de_dados};'
    r'Trusted_Connection=yes;'
)

@dev_bp.route("/dev")
def dev():
    return render_template("dev.html")

