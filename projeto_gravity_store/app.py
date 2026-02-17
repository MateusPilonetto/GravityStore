from flask import Flask, render_template, url_for, request, redirect, flash, session

app = Flask(__name__)
app.secret_key = "chave_super_secreta_do_mateus"  # Necessário para lembrar quem está logado

# --- BANCO DE DADOS TEMPORÁRIO ---
banco_de_usuarios = {
    "admin@gravity.com": {
        "nome": "Admin",
        "usuario": "admin",
        "telefone": "000000000",
        "senha": "1234"
    }
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email in banco_de_usuarios:
            user_data = banco_de_usuarios[email]
            if senha == user_data['senha']:
                # --- MÁGICA DA SESSÃO ---
                # Guardamos o nome do usuário na "memória" do navegador
                session['usuario_logado'] = user_data['nome']
                session['email_usuario'] = email
                
                flash(f"Login realizado! Bem-vindo, {user_data['nome']}", "sucesso")
                return redirect(url_for('home'))
            else:
                flash("Senha incorreta.", "erro")
        else:
            flash("Usuário não encontrado.", "erro")
        
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['user']
        telefone = request.form['phone']
        email = request.form['email']
        senha = request.form['senha']
        
        try:
            senha_confirm = request.form['senha_confirmacao']
        except KeyError:
             # Fallback caso o HTML ainda esteja antigo
            senha_confirm = request.form.get('senha_confirmacao', senha)

        if senha != senha_confirm:
            flash("As senhas não conferem!", "erro")
            return redirect(url_for('register'))

        if email in banco_de_usuarios:
            flash("Email já cadastrado!", "erro")
            return redirect(url_for('login'))

        # Salva o usuário novo
        banco_de_usuarios[email] = {
            "nome": nome,
            "usuario": usuario,
            "telefone": telefone,
            "senha": senha
        }
        
        flash("Conta criada! Faça login.", "sucesso")
        return redirect(url_for('login'))

    return render_template("register.html")

# --- NOVA ROTA: SAIR (LOGOUT) ---
@app.route("/logout")
def logout():
    session.clear()  # Limpa a memória (desloga)
    flash("Você saiu da conta.", "info")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)