import json
import os
import urllib.request
import urllib.error
from functools import wraps
from flask import Flask, render_template, request, redirect, session, jsonify, url_for

app = Flask(__name__)
app.secret_key = "hub_openfinance_secret"

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "banco_a_url": "http://127.0.0.1:5001/openfinance",
    "banco_b_url": "http://127.0.0.1:5000/openfinance"
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            config = json.load(arquivo)
            return {**DEFAULT_CONFIG, **config}
    except (ValueError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(config, arquivo, indent=2, ensure_ascii=False)


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


# ================= BUSCAR DADOS DOS BANCOS =================
def buscar_dados(cpf):
    config = load_config()

    def consulta_banco(url):
        try:
            with urllib.request.urlopen(f"{url}/{cpf}", timeout=5) as resposta:
                if resposta.status != 200:
                    return {}
                dados = resposta.read().decode("utf-8")
                return json.loads(dados)
        except (urllib.error.URLError, ValueError):
            return {}

    banco_a = consulta_banco(config["banco_a_url"])
    banco_b = consulta_banco(config["banco_b_url"])

    return {
        "nome": banco_a.get("nome") or banco_b.get("nome") or "Cliente Desconhecido",
        "idade": banco_a.get("idade", banco_b.get("idade", 0)),
        "renda_mensal": banco_a.get("renda", banco_b.get("renda", 0)),
        "historico_cartao_positivo": True,
        "contas": {
            "banco_a": {
                "saldo": banco_a.get("saldo", 0),
                "meses_conta": 12,
                "inadimplente": banco_a.get("inadimplente", False)
            },
            "banco_b": {
                "saldo": banco_b.get("saldo", 0),
                "meses_conta": 24,
                "inadimplente": banco_b.get("inadimplente", False)
            }
        }
    }


# ================= MOTOR DE SCORE =================
def app_open_finance(dados_completos):
    nome = dados_completos.get("nome", "Cliente Desconhecido")
    idade = dados_completos.get("idade", 0)

    if idade < 18:
        return {
            "cliente": nome,
            "score": 0,
            "decisao": "REPROVADO",
            "motivo": "Idade inferior a 18 anos",
            "limite_sugerido": "R$ 0.00"
        }

    score = 0
    renda = dados_completos.get("renda_mensal", 0)
    score += min((renda / 100) * 10, 400)

    saldo_total = sum(banco["saldo"] for banco in dados_completos["contas"].values())
    score += min(saldo_total * 0.05, 200)

    meses_media = sum(banco["meses_conta"] for banco in dados_completos["contas"].values()) / len(dados_completos["contas"])
    score += min(meses_media * 5, 100)

    if dados_completos.get("historico_cartao_positivo"):
        score += 200

    if any(banco["inadimplente"] for banco in dados_completos["contas"].values()):
        score -= 500

    score_final = max(0, min(score, 1000))

    if score_final >= 750:
        decisao = "APROVADO: Crédito Platinum Liberado"
        limite = renda * 2
    elif score_final >= 450:
        decisao = "APROVADO: Crédito Standard Liberado"
        limite = renda * 0.5
    else:
        decisao = "REPROVADO"
        limite = 0

    return {
        "cliente": nome,
        "score": round(score_final, 2),
        "decisao": decisao,
        "limite_sugerido": f"R$ {limite:.2f}"
    }


# ================= ROTAS WEB =================
@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("usuario"):
        return redirect(url_for("dashboard"))

    error = None
    usuario = ""

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "").strip()

        if not usuario or not senha:
            error = "Informe usuário e senha."
        else:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))

    return render_template("login.html", error=error, usuario=usuario)


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/consulta", methods=["POST"])
@login_required
def consulta():
    cpf = request.form.get("cpf", "").strip()
    if not cpf:
        return render_template("dashboard.html", error="Informe um CPF.", cpf=cpf)

    dados = buscar_dados(cpf)
    resultado = app_open_finance(dados)

    return render_template("dashboard.html", resultado=resultado, cpf=cpf)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    config = load_config()
    message = None

    if request.method == "POST":
        config["banco_a_url"] = request.form.get("banco_a_url", config["banco_a_url"]).strip()
        config["banco_b_url"] = request.form.get("banco_b_url", config["banco_b_url"]).strip()
        save_config(config)
        message = "Configurações atualizadas com sucesso."

    return render_template("settings.html", config=config, message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================= ENDPOINT DO HUB =================
@app.route("/openfinance/<cpf>")
def openfinance_hub(cpf):
    dados = buscar_dados(cpf)
    resultado = app_open_finance(dados)
    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
