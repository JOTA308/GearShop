from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Caminho do arquivo
USUARIOS_FILE = "usuarios.json"

# --- Funções auxiliares ---
def carregar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_usuarios():
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

# --- Dados iniciais ---
usuarios = carregar_usuarios()
produtos = []

# --- HOME ---
@app.route("/")
def home():
    return render_template("indexx.html", produtos=produtos)

# --- CADASTRO DE USUÁRIO ---
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        telefone = request.form.get("telefone", "")
        endereco = request.form.get("endereco", "")
        usuarios.append({
            "nome": nome,
            "email": email,
            "senha": senha,
            "telefone": telefone,
            "endereco": endereco
        })
        salvar_usuarios()
        return redirect(url_for("login"))
    return render_template("cadastro.html")

# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        for u in usuarios:
            if u["email"] == email and u["senha"] == senha:
                session["usuario"] = u
                return redirect(url_for("perfil"))
        return "Email ou senha incorretos!"
    return render_template("login.html")

# --- PERFIL ---
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]

    if request.method == "POST":
        usuario["nome"] = request.form["nome"]
        usuario["email"] = request.form["email"]
        usuario["telefone"] = request.form.get("telefone", "")
        usuario["endereco"] = request.form.get("endereco", "")
        session["usuario"] = usuario
        session.modified = True
        salvar_usuarios()
        return redirect(url_for("perfil"))

    return render_template("perfil.html", usuario=usuario)

# --- CADASTRO DE PRODUTO ---
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = request.form["preco"]
        imagem_url = request.form["imagem_url"]
        produtos.append({"nome": nome, "preco": preco, "imagem_url": imagem_url})
        return redirect(url_for("home"))
    return render_template("cadastrar.html")

# --- CARRINHO ---
@app.route("/carrinho")
def carrinho():
    return render_template("carrinho.html")

if __name__ == "__main__":
    app.run(debug=True)
