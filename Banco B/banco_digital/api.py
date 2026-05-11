from flask import Flask, request, jsonify
from flask_cors import CORS

import json
import os
import random

app = Flask(__name__)

CORS(app)

ARQUIVO = "clientes.json"

# ==========================================
# CRIAR JSON
# ==========================================

if not os.path.exists(ARQUIVO):

    with open(ARQUIVO, "w") as f:
        json.dump([], f)

# ==========================================
# FUNÇÕES
# ==========================================

def carregar_clientes():

    with open(ARQUIVO, "r") as f:

        return json.load(f)

def salvar_clientes(clientes):

    with open(ARQUIVO, "w") as f:

        json.dump(clientes, f, indent=4)

# ==========================================
# CADASTRO
# ==========================================

@app.route("/cadastro", methods=["POST"])
def cadastro():

    dados = request.json

    clientes = carregar_clientes()

    # CPF DUPLICADO

    for cliente in clientes:

        if cliente["cpf"] == dados["cpf"]:

            return jsonify({
                "erro": "CPF já cadastrado"
            }), 400

    renda = float(dados["renda"])

    score = random.randint(500, 950)

    limite_credito = renda * 0.4

    novo_cliente = {

        "nome": dados["nome"],

        "cpf": dados["cpf"],

        "senha": dados["senha"],

        "idade": dados["idade"],

        "renda": renda,

        "tempo_emprego": dados["tempo_emprego"],

        "tipo_emprego": dados["tipo_emprego"],

        "saldo": 0,

        "score": score,

        "limite_credito": limite_credito,

        "agencia": "0001",

        "conta": str(random.randint(10000, 99999)),

        "extrato": []
    }

    clientes.append(novo_cliente)

    salvar_clientes(clientes)

    return jsonify({
        "mensagem": "Conta criada com sucesso"
    })

# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    dados = request.json

    clientes = carregar_clientes()

    for cliente in clientes:

        if (
            cliente["cpf"] == dados["cpf"]
            and
            cliente["senha"] == dados["senha"]
        ):

            return jsonify(cliente)

    return jsonify({
        "erro": "CPF ou senha inválidos"
    }), 401

# ==========================================
# DEPÓSITO
# ==========================================

@app.route("/deposito", methods=["POST"])
def deposito():

    dados = request.json

    clientes = carregar_clientes()

    for cliente in clientes:

        if cliente["cpf"] == dados["cpf"]:

            valor = float(dados["valor"])

            cliente["saldo"] += valor

            cliente["extrato"].append({
                "tipo": "Depósito",
                "valor": valor
            })

            salvar_clientes(clientes)

            return jsonify(cliente)

    return jsonify({
        "erro": "Cliente não encontrado"
    }), 404

# ==========================================
# PIX
# ==========================================

@app.route("/pix", methods=["POST"])
def pix():

    dados = request.json

    clientes = carregar_clientes()

    for cliente in clientes:

        if cliente["cpf"] == dados["cpf"]:

            valor = float(dados["valor"])

            if cliente["saldo"] < valor:

                return jsonify({
                    "erro": "Saldo insuficiente"
                }), 400

            cliente["saldo"] -= valor

            cliente["extrato"].append({
                "tipo": "PIX enviado",
                "valor": valor
            })

            salvar_clientes(clientes)

            return jsonify(cliente)

    return jsonify({
        "erro": "Cliente não encontrado"
    }), 404
# ==========================================
# SIMULAR EMPRÉSTIMO
# ==========================================

@app.route("/emprestimo", methods=["POST"])
def emprestimo():

    dados = request.json

    clientes = carregar_clientes()

    for cliente in clientes:

        if cliente["cpf"] == dados["cpf"]:

            valor = float(dados["valor"])

            parcelas = int(dados["parcelas"])

            score = cliente["score"]

            aprovado = False

            juros = 0

            # REGRAS

            if score >= 800:

                aprovado = True
                juros = 0.02

            elif score >= 700:

                aprovado = True
                juros = 0.05

            elif score >= 600:

                aprovado = True
                juros = 0.08

            else:

                aprovado = False

            parcela = 0

            if aprovado:

                total = valor * (1 + juros)

                parcela = total / parcelas

            return jsonify({

                "aprovado": aprovado,

                "score": score,

                "juros": juros,

                "parcela": round(parcela, 2),

                "valor": valor

            })

    return jsonify({
        "erro": "Cliente não encontrado"
    }), 404

# ==========================================
# OPENFINANCE
@app.route("/openfinance/<cpf>")
def openfinance(cpf):

    clientes = carregar_clientes()

    for cliente in clientes:

        if cliente["cpf"] == cpf:

            return jsonify({
                "nome": cliente["nome"],
                "cpf": cliente["cpf"],
                "idade": cliente["idade"],
                "renda": cliente["renda"],
                "saldo": cliente["saldo"],
                "score": cliente["score"],
                "inadimplente": False
            })

    return jsonify({
        "erro": "Cliente não encontrado"
    }), 404

# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)