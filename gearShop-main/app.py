from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from decimal import Decimal

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

def get_cart():
    return session.setdefault('carrinho', {})

# ------------------------------------
# # Exige login para todas as rotas, exceto: home
# ------------------------------------
@app.before_request
def require_login_guard():
    open_endpoints = {'home', 'indexx', 'login', 'cadastrar', 'senha', 'static', 'logout'}
    ep = request.endpoint
    if ep in open_endpoints or ep is None:
        return
    # Para acessar o carrinho o cliente deve estar logado
    if 'usuario' not in session:
        if ep == 'carrinho_selecionar':
            pid = request.form.get('produto_id')
            if pid:
                try:
                    session['produto_selecionado_pendente'] = int(pid)
                except Exception:
                    pass
        flash("Você precisa estar logado!", "erro")
        return redirect(url_for('login'))

# ------------------------------------
# HOME
# ------------------------------------
@app.route("/", endpoint='home')
@app.route("/index", endpoint='indexx')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Bloco que exibe os produtos com a situação ativo, quando não for comprado
    try:
        cursor.execute("SELECT * FROM produtos WHERE status='ativo' ORDER BY id DESC")
    except mysql.connector.Error:
        cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("indexx.html", produtos=produtos)

# ------------------------------------
# LOGIN
# ------------------------------------
def format_cpf(s):
    digits = ''.join(ch for ch in s if ch.isdigit())
    if len(digits) != 11:
        return s.strip()
    return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

# Login com redirecionamento pós-autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form.get('login', '').strip()
        senha = request.form.get('senha', '')

        # Validações no login
        if not login_val or not senha:
            flash("Preencha todos os campos!", "erro")
            return render_template("login.html")
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        if '@' in login_val:
            cursor.execute("SELECT * FROM usuarios WHERE email=%s", (login_val,))
        else:
            cpf_val = format_cpf(login_val)
            cursor.execute("SELECT * FROM usuarios WHERE cpf=%s", (cpf_val,))
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
            
            # Recupera seleção de produto feita sem login e segue ao carrinho
            pending = session.pop('produto_selecionado_pendente', None)
            if pending:
                session['produto_selecionado'] = int(pending)
                return redirect(url_for('carrinho'))
            return redirect(url_for('perfil'))
        else:
            flash("Login ou senha incorretos!", "erro")

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
        endereco = request.form.get('endereco', '').strip()

        # Validações na geração do cadastro do cliente
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
# Formulário de anúncio protegido por login
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

        # Validações no cadastro do produto
        if not all([nome, categoria, preco, condicao, descricao, localizacao]):
            flash("Preencha todos os campos!", "erro")
            return render_template('anunciar.html')
        imagem_file = request.files.get('imagem')
        if not imagem_file or not imagem_file.filename:
            flash("Selecione uma imagem válida.", "erro")
            return render_template('anunciar.html')
        if not allowed_file(imagem_file.filename):
            flash("Formato de imagem inválido. Use png, jpg, jpeg ou gif.", "erro")
            return render_template('anunciar.html')
        original = secure_filename(imagem_file.filename)
        ext = os.path.splitext(original)[1].lower()
        unique_name = f"{uuid4().hex}{ext}"
        imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        imagem_file.save(imagem_path)
        imagem_db = f"/static/uploads/{unique_name}"
        db = get_db_connection()
        cursor = db.cursor()
        try:
            preco_db = preco.replace(',', '.')
            cursor.execute("""
                INSERT INTO produtos (nome, categoria, preco, condicao, descricao, localizacao, imagem_url, usuario_cpf)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, categoria, preco_db, condicao, descricao, localizacao, imagem_db, usuario_cpf))
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
# Carrinho exige login; exibe produto único selecionado e total
@app.route('/carrinho')
def carrinho():
    if 'usuario' not in session:
        flash("Faça login para acessar o carrinho.", "erro")
        return redirect(url_for('login'))
    sel_id = session.get('produto_selecionado')
    produto = None
    total = Decimal('0.00')
    if sel_id:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos WHERE id=%s", (sel_id,))
        produto = cursor.fetchone()
        cursor.close()
        db.close()
        if produto:
            total = Decimal(str(produto['preco']))
    return render_template('carrinho.html', produto=produto, total=total)

# Seleção de produto; se não logado, guarda produto e pede login
@app.route('/carrinho/selecionar', methods=['POST'])
def carrinho_selecionar():
    produto_id = request.form.get('produto_id', '').strip()
    if not produto_id:
        flash("Seleção inválida.", "erro")
        return redirect(url_for('indexx'))
    if 'usuario' not in session:
        session['produto_selecionado_pendente'] = int(produto_id)
        flash("Faça login para continuar.", "erro")
        return redirect(url_for('login'))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM produtos WHERE id=%s", (produto_id,))
    exists = cursor.fetchone()
    cursor.close()
    db.close()
    if not exists:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for('indexx'))
    session['produto_selecionado'] = int(produto_id)
    return redirect(url_for('carrinho'))

# Limpar carrinho, devolvendo o produto para a rota principal
@app.route('/carrinho/limpar', methods=['POST'])
def carrinho_limpar():
    if 'usuario' not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for('login'))
    session.pop('produto_selecionado', None)
    return redirect(url_for('carrinho'))

# Finaliza compra: marca produto como vendido e registra em compras (rota)
@app.route('/carrinho/finalizar', methods=['POST'])
def carrinho_finalizar():
    if 'usuario' not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for('login'))
    sel_id = session.get('produto_selecionado')
    if not sel_id:
        flash("Nenhum produto selecionado.", "erro")
        return redirect(url_for('carrinho'))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT preco FROM produtos WHERE id=%s", (sel_id,))
        row = cursor.fetchone()
        preco_val = row['preco'] if row else '0.00'
        try:
            cursor.execute("UPDATE produtos SET status='vendido' WHERE id=%s", (sel_id,))
        except mysql.connector.Error:
            cursor.execute("DELETE FROM produtos WHERE id=%s", (sel_id,))
        # Registro da compra vinculado ao comprador logado
        cursor2 = db.cursor()
        cursor2.execute("INSERT INTO compras (produto_id, comprador_cpf, preco) VALUES (%s, %s, %s)", (sel_id, session['usuario']['cpf'], preco_val))
        db.commit()
        session.pop('produto_selecionado', None)
        flash("Compra finalizada.", "sucesso")
        return redirect(url_for('indexx'))
    except mysql.connector.Error:
        db.rollback()
        flash("Erro ao finalizar compra.", "erro")
        return redirect(url_for('carrinho'))
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        db.close()

# Devolve produto ao estado ativo (uso interno do fluxo)
@app.route('/carrinho/devolver', methods=['POST'])
def carrinho_devolver():
    if 'usuario' not in session:
        flash("Faça login para continuar.", "erro")
        return redirect(url_for('login'))
    sel_id = session.get('produto_selecionado')
    if not sel_id:
        flash("Nenhum produto selecionado.", "erro")
        return redirect(url_for('carrinho'))
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE produtos SET status='ativo' WHERE id=%s", (sel_id,))
        db.commit()
        flash("Produto devolvido.", "sucesso")
        return redirect(url_for('carrinho'))
    except mysql.connector.Error:
        db.rollback()
        flash("Erro ao devolver produto.", "erro")
        return redirect(url_for('carrinho'))
    finally:
        cursor.close()
        db.close()


# ------------------------------------
# LOGOUT
# ------------------------------------
# Logout limpa sessão e retorna ao login
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for('login'))

# ------------------------------------
# ESQUECI A SENHA (stub)
# ------------------------------------
@app.route('/senha')
def senha():
    return redirect(url_for('login'))

# Histórico de compras do usuário autenticado
@app.route('/minhas-compras')
def minhas_compras():
    if 'usuario' not in session:
        flash("Faça login para acessar suas compras.", "erro")
        return redirect(url_for('login'))
    cpf = session['usuario']['cpf']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id, c.created_at, c.preco, p.nome, p.imagem_url
        FROM compras c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.comprador_cpf=%s
        ORDER BY c.created_at DESC
    """, (cpf,))
    compras = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('minhas_compras.html', compras=compras)

# ------------------------------------
# RUN
# ------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
