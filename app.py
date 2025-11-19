from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

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
# CONFIGURAÇÃO DE UPLOAD
# ------------------------------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------------------
# HOME
# ------------------------------------
@app.route("/", endpoint='home')
@app.route("/index", endpoint='indexx')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("indexx.html", produtos=produtos)

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
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        db.close()

        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario'] = {
                'cpf': usuario['cpf'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'telefone': usuario['telefone'],
                'endereco': usuario.get('endereco', '')
            }
            session.permanent = True
            return redirect(url_for('perfil'))
        else:
            flash("E-mail ou senha incorretos!", "erro")

    return render_template('login.html')

# ------------------------------------
# CADASTRO
# ------------------------------------
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        cpf = request.form.get('cpf', '').strip()
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        nascimento = request.form.get('nascimento', '').strip()
        telefone = request.form.get('telefone', '').strip()
        senha = request.form.get('senha', '')
        endereco = ""

        if not all([cpf, nome, email, nascimento, telefone, senha]):
            flash("Preencha todos os campos!", "erro")
            return render_template("cadastro.html")

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres!", "erro")
            return render_template("cadastro.html")

        senha_hash = generate_password_hash(senha)

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO usuarios (cpf, nome, email, telefone, senha, nascimento, endereco)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (cpf, nome, email, telefone, senha_hash, nascimento, endereco))
            db.commit()
            cursor.close()
            db.close()
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
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco', '')

        cursor.execute("""
            UPDATE usuarios
            SET nome=%s, email=%s, telefone=%s, endereco=%s
            WHERE cpf=%s
        """, (nome, email, telefone, endereco, cpf))
        db.commit()
        session['usuario'].update({'nome': nome, 'email': email, 'telefone': telefone, 'endereco': endereco})
        flash("Dados atualizados com sucesso!", "sucesso")

    cursor.execute("SELECT cpf, nome, email, telefone, endereco FROM usuarios WHERE cpf=%s", (cpf,))
    usuario = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template('perfil.html', usuario=usuario)

# ------------------------------------
# ANUNCIAR PRODUTO
# ------------------------------------
@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    if 'usuario' not in session:
        flash("Faça login para anunciar um produto!", "erro")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco = request.form.get('preco', '').strip()
        condicao = request.form.get('condicao', '').strip()
        descricao = request.form.get('descricao', '').strip()
        localizacao = request.form.get('localizacao', '').strip()
        usuario_cpf = session['usuario']['cpf']

        if not all([nome, categoria, preco, condicao, descricao, localizacao]):
            flash("Preencha todos os campos!", "erro")
            return render_template('anunciar.html')

        # Upload da imagem
        imagem_file = request.files.get('imagem')
        if imagem_file and allowed_file(imagem_file.filename):
            filename = secure_filename(imagem_file.filename)
            imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem_file.save(imagem_path)
            imagem_db = f"/{imagem_path.replace(os.sep, '/')}"
        else:
            imagem_db = "/static/uploads/placeholder.png"  # fallback

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO produtos (nome, categoria, preco, condicao, descricao, localizacao, imagem_url, usuario_cpf)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, categoria, preco, condicao, descricao, localizacao, imagem_db, usuario_cpf))
            db.commit()
            flash("Produto anunciado com sucesso!", "sucesso")
        except mysql.connector.Error as e:
            db.rollback()
            flash(f"Erro ao anunciar produto: {e}", "erro")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('indexx'))

    return render_template('anunciar.html')

# ------------------------------------
# CARRINHO
# ------------------------------------
@app.route('/carrinho')
def carrinho():
    return render_template('carrinho.html')

# ------------------------------------
# LOGOUT
# ------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for('login'))

# ------------------------------------
# RUN
# ------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
