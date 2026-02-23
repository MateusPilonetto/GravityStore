from flask import Blueprint, render_template, request

# Avisamos o Blueprint sobre as pastas relativas a ele
main_bp = Blueprint('main', __name__, 
                    template_folder='../templates', 
                    static_folder='../static',
                    static_url_path='/main_static')

# Rota trazida do app.py
@main_bp.route("/")
def home():
    return render_template("index.html")

# Rota trazida do app.py
@main_bp.route("/pesquisa")
def pesquisa():
    termo = request.args.get('name') 
    return render_template("search.html", busca=termo)