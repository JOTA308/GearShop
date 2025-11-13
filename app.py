from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import timedelta

# ======================================================
#  Configuração do Flask
# ======================================================
app = Flask(__name__)
app.secret_key = 'chave_super_secreta_fixa_gearshop'
app.permanent_session_lifetime = timedelta(days=7)

# ======================================================
#  Conexão com o MySQL
# ======================================================
def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='gearshop'
    )

# ======================================================
#  Página inicial
# ======================================================
@app.route('/')
def index():
    return render_template('indexx.html')

# ======================================================
#  Login
# ======================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            flash("Preencha todos os campos!", "erro")
            return render_template('login.html')

        db = get_db_connection()
        try:
            cursor = db.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT cpf, nome, senha FROM usuarios WHERE email=%s", (email,))
            usuario = cursor.fetchone()
            cursor.close()
        finally:
            db.close()

        if usuario and usuario['senha'] == senha:
            session.permanent = True
            session['usuario'] = {
                'cpf': usuario['cpf'],
                'nome': usuario['nome']
            }
            flash(f"Bem-vindo(a), {usuario['nome']}!", "sucesso")
            return redirect(url_for('perfil'))
        else:
            flash("E-mail ou senha incorretos!", "erro")
            return render_template('login.html')

    return render_template('login.html')

# ======================================================
#  Cadastro
# ======================================================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        cpf = ''.join(filter(str.isdigit, request.form.get('cpf', '')))
        nome = request.form.get('nome')
        email = request.form.get('email')
        nascimento = request.form.get('nascimento')
        senha = request.form.get('senha')

        if not all([cpf, nome, email, nascimento, senha]):
            flash("Por favor, preencha todos os campos!", "erro")
            return render_template('cadastro.html')

        db = get_db_connection()
        try:
            cursor = db.cursor(buffered=True)
            cursor.execute(
                "INSERT INTO usuarios (cpf, nome, email, nascimento, senha) VALUES (%s, %s, %s, %s, %s)",
                (cpf, nome, email, nascimento, senha)
            )
            db.commit()
            cursor.close()
        except mysql.connector.Error as e:
            db.rollback()
            flash(f"Erro ao salvar no banco: {e}", "erro")
            return render_template('cadastro.html')
        finally:
            db.close()

        flash("Cadastro realizado com sucesso!", "sucesso")
        return redirect(url_for('login'))

    return render_template('cadastro.html')

# ======================================================
#  Perfil do usuário
# ======================================================
@app.route('/perfil')
def perfil():
    usuario = session.get('usuario')
    if not usuario:
        flash("Você precisa estar logado para acessar o perfil.", "erro")
        return redirect(url_for('login'))

    return render_template('perfil.html', usuario=usuario)


# ======================================================
#  Carrinho
# ======================================================
@app.route('/carrinho')
def carrinho():
    return render_template('carrinho.html')

# ======================================================
#  Redefinir senha
# ======================================================
@app.route('/senha', methods=['GET', 'POST'])
def senha():
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')

        if not email or not nova_senha:
            flash("Preencha todos os campos!", "erro")
            return render_template('senha.html')

        db = get_db_connection()
        try:
            cursor = db.cursor(buffered=True)
            cursor.execute("UPDATE usuarios SET senha=%s WHERE email=%s", (nova_senha, email))
            db.commit()
            cursor.close()
        finally:
            db.close()

        flash("Senha atualizada com sucesso!", "sucesso")
        return redirect(url_for('login'))

    return render_template('senha.html')

# ======================================================
#  Logout
# ======================================================
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for('login'))

# ======================================================
#  Inicialização do servidor
# ======================================================


if __name__ == '__main__':
    app.run(debug=True)

