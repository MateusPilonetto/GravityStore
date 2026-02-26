from flask import Flask
from register.modules.register import register_bp
from login.modules.login import login_bp
from main.modules.main import main_bp

app = Flask(__name__)
app.secret_key = 'chave_segura'

# O Flask vai cuidar das rotas e pastas automaticamente agora
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)