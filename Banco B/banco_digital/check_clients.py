import json
with open('clientes.json', 'r') as f:
    clientes = json.load(f)
for cliente in clientes:
    print(f'{cliente["nome"]} - CPF: {cliente["cpf"]} - Score: {cliente["score"]}')