from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_fixa_gearshop'
app.permanent_session_lifetime = timedelta(days=7)

# ------------------------------------
# CONFIGURAÇÃO DO BANCO
# ------------------------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "gearshop"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


# ------------------------------------
# HOME
# ------------------------------------
@app.route("/")
def index():
    return render_template("indexx.html")


# ------------------------------------
# LOGIN
# ------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')

        if not email or not senha:
            flash("Preencha todos os campos!", "erro")
            return render_template("login.html")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT cpf, nome, senha FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()

        cursor.close()
        db.close()

        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario'] = {
                'cpf': usuario['cpf'],
                'nome': usuario['nome']
            }
            return redirect(url_for('perfil'))
        else:
            flash("E-mail ou senha incorretos!", "erro")
            return render_template('login.html')

    return render_template('login.html')


# ------------------------------------
# CADASTRO
# ------------------------------------
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        try:
            cpf = request.form.get('cpf', '').strip()
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip()
            nascimento = request.form.get('nascimento', '').strip()
            telefone = request.form.get('telefone', '').strip()
            senha = request.form.get('senha', '')
            endereco = ""  # endereço padrão vazio

            if not all([cpf, nome, email, nascimento, telefone, senha]):
                flash("Preencha todos os campos!", "erro")
                return render_template("cadastro.html")

            if len(senha) < 8:
                flash("A senha deve ter pelo menos 8 caracteres!", "erro")
                return render_template("cadastro.html")

            senha_hash = generate_password_hash(senha)

            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
                INSERT INTO usuarios (cpf, nome, email, telefone, senha, nascimento, endereco)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (cpf, nome, email, telefone, senha_hash, nascimento, endereco)

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            flash("Conta criada com sucesso!", "sucesso")
            return redirect('/login')

        except mysql.connector.Error as e:
            flash(f"Erro ao cadastrar: {e}", "erro")
            return render_template("cadastro.html")

    return render_template("cadastro.html")



# ------------------------------------
# PERFIL
# ------------------------------------
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        flash("Você precisa estar logado!", "erro")
        return redirect(url_for('login'))

    cpf = session['usuario']['cpf']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Atualizar dados
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco', '')

        # Se a coluna endereço NÃO existir no banco, evita erro
        try:
            cursor.execute("""
                UPDATE usuarios
                SET nome=%s, email=%s, telefone=%s, endereco=%s
                WHERE cpf=%s
            """, (nome, email, telefone, endereco, cpf))

        except mysql.connector.Error:
            # Atualiza sem endereço se a coluna não existir
            cursor.execute("""
                UPDATE usuarios
                SET nome=%s, email=%s, telefone=%s
                WHERE cpf=%s
            """, (nome, email, telefone, cpf))

        conn.commit()
        flash("Dados atualizados com sucesso!", "sucesso")

    # Buscar dados do usuário
    try:
        cursor.execute("SELECT cpf, nome, email, telefone, endereco FROM usuarios WHERE cpf=%s", (cpf,))
    except mysql.connector.Error:
        cursor.execute("SELECT cpf, nome, email, telefone FROM usuarios WHERE cpf=%s", (cpf,))

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    session['usuario'] = usuario

    return render_template('perfil.html', usuario=usuario)

# ------------------------------------
# REDEFINIR SENHA
# ------------------------------------
@app.route('/senha', methods=['GET', 'POST'])
def senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        nova_senha = request.form.get('nova_senha', '')

        if not email or not nova_senha:
            flash("Preencha todos os campos!", "erro")
            return render_template('senha.html')

        if len(nova_senha) < 8:
            flash("A nova senha deve ter pelo menos 8 caracteres!", "erro")
            return render_template('senha.html')

        nova_senha_hash = generate_password_hash(nova_senha)

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE usuarios SET senha=%s WHERE email=%s",
                           (nova_senha_hash, email))
            db.commit()
            flash("Senha atualizada com sucesso!", "sucesso")

        except mysql.connector.Error as erro:
            db.rollback()
            flash(f"Erro ao atualizar senha: {erro}", "erro")

        finally:
            cursor.close()
            db.close()

        return redirect(url_for('login'))

    return render_template('senha.html')


# ------------------------------------
# PRODUTOS
# ------------------------------------
@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if 'usuario' not in session:
        flash("Faça login para cadastrar um produto!", "erro")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        preco = request.form.get('preco', '').strip()
        imagem = request.form.get('imagem_url', '').strip()

        if not all([nome, preco, imagem]):
            flash("Preencha todos os campos!", "erro")
            return render_template('cadastrar_produto.html')

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO produtos (nome, preco, imagem_url)
            VALUES (%s, %s, %s)
        """, (nome, preco, imagem))

        db.commit()
        cursor.close()
        db.close()

        flash("Produto cadastrado com sucesso!", "sucesso")
        return redirect(url_for('perfil'))

    return render_template('cadastrar_produto.html')


@app.route('/carrinho')
def carrinho():
    return render_template('carrinho.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for('login'))


# RUN
if __name__ == '__main__':
    app.run(debug=True)

