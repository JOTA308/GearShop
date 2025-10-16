from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import re

# =====================================================
# CONFIGURAÇÕES BÁSICAS
# =====================================================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_super_secreta_flask")

USUARIOS_FILE = "usuarios.json"


# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================
def carregar_usuarios():
    """Carrega os usuários do arquivo JSON."""
    if os.path.exists(USUARIOS_FILE):
        try:
            with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def salvar_usuarios(usuarios):
    """Salva os usuários no arquivo JSON."""
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)


def buscar_usuario(email):
    """Retorna um usuário pelo e-mail (insensível a maiúsculas/minúsculas)."""
    email = email.strip().lower()
    return next((u for u in usuarios if u["email"].lower() == email), None)


def limpar_cpf(cpf):
    """Remove caracteres não numéricos do CPF."""
    return re.sub(r"\D", "", cpf)


def validar_cpf(cpf):
    """Valida o CPF (apenas tamanho e dígitos, sem algoritmo de verificação)."""
    cpf = limpar_cpf(cpf)
    return len(cpf) == 11 and cpf.isdigit()


# =====================================================
# DADOS INICIAIS
# =====================================================
usuarios = carregar_usuarios()
produtos = []


# =====================================================
# ROTA PRINCIPAL
# =====================================================
@app.route("/")
def home():
    """Página inicial."""
    return render_template("indexx.html", produtos=produtos)


# =====================================================
# CADASTRO DE USUÁRIO
# =====================================================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    """Página de cadastro de novos usuários."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        endereco = request.form.get("endereco", "").strip()

        # Validações básicas
        if not nome or not email or not senha or not cpf:
            flash("Por favor, preencha todos os campos obrigatórios.", "warning")
            return redirect(url_for("cadastro"))

        if not validar_cpf(cpf):
            flash("CPF inválido! Deve conter exatamente 11 números.", "danger")
            return redirect(url_for("cadastro"))

        if buscar_usuario(email):
            flash("Já existe uma conta com este e-mail.", "danger")
            return redirect(url_for("cadastro"))

        novo_usuario = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "cpf": limpar_cpf(cpf),
            "telefone": telefone,
            "endereco": endereco,
        }

        usuarios.append(novo_usuario)
        salvar_usuarios(usuarios)
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


# =====================================================
# LOGIN
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Página de login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "").strip()

        usuario = buscar_usuario(email)
        if usuario and usuario["senha"] == senha:
            session["usuario"] = usuario
            flash(f"Bem-vindo(a), {usuario['nome']}!", "success")
            return redirect(url_for("perfil"))
        else:
            flash("Email ou senha incorretos.", "danger")

    return render_template("login.html")


# =====================================================
# PERFIL DO USUÁRIO
# =====================================================
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    """Página do perfil do usuário logado."""
    if "usuario" not in session:
        flash("Você precisa estar logado para acessar o perfil.", "warning")
        return redirect(url_for("login"))

    usuario = session["usuario"]

    if request.method == "POST":
        usuario["nome"] = request.form.get("nome", usuario["nome"]).strip()
        usuario["email"] = request.form.get("email", usuario["email"]).strip().lower()
        usuario["telefone"] = request.form.get("telefone", usuario.get("telefone", "")).strip()
        usuario["endereco"] = request.form.get("endereco", usuario.get("endereco", "")).strip()

        for i, u in enumerate(usuarios):
            if u["email"] == usuario["email"]:
                usuarios[i] = usuario
                break

        salvar_usuarios(usuarios)
        session["usuario"] = usuario
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil"))

    return render_template("perfil.html", usuario=usuario)


# =====================================================
# CADASTRAR PRODUTO
# =====================================================
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    """Página para cadastrar produtos."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco = request.form.get("preco", "").strip()
        imagem_url = request.form.get("imagem_url", "").strip()

        if not nome or not preco:
            flash("Preencha todos os campos obrigatórios.", "warning")
            return redirect(url_for("cadastrar"))

        produtos.append({
            "nome": nome,
            "preco": preco,
            "imagem_url": imagem_url or "https://via.placeholder.com/300x200",
        })

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("home"))

    return render_template("cadastrar.html")


# =====================================================
# CARRINHO
# =====================================================
@app.route("/carrinho")
def carrinho():
    """Página do carrinho."""
    return render_template("carrinho.html")


# =====================================================
# RECUPERAÇÃO DE SENHA
# =====================================================
@app.route("/senha", methods=["GET", "POST"])
def senha():
    """Página para redefinição de senha (simulada)."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        usuario = buscar_usuario(email)

        if usuario:
            flash("Um link de recuperação foi enviado para seu e-mail (simulado).", "info")
        else:
            flash("E-mail não encontrado em nossa base de dados.", "danger")

        return redirect(url_for("login"))

    return render_template("senha.html")


# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    """Finaliza a sessão do usuário."""
    session.pop("usuario", None)
    flash("Você saiu da sua conta com sucesso.", "info")
    return redirect(url_for("home"))


# =====================================================
# EXECUÇÃO
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
