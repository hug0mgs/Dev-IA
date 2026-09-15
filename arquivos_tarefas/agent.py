import ollama
import json

MODEL = "llama3.2"
PERGUNTA = "Quais os nomes dos times que estão na base de dados? E qual time tem a menor probabilidade de Subir à Série B?"
MAX_PASSOS = 10
SYSTEM = "Você é um especialista em futebol brasileiro. NUNCA invente números ou estatísticas, use as tools."

_TIMES = {
    "Brusque": {"vitorias": 1, "probabilidade": 73,},
    "Inter de Limeira": {"vitorias": 0, "probabilidade": 37},
    "Paysandu": {"vitorias": 0, "probabilidade": 30},
    "Ferroviária": {"vitorias": 1, "probabilidade": 58} 
}

def listar_times():
    return list(_TIMES.keys())

def acesso_prob(time):
    dados = _TIMES.get(time)
    if dados:
        return dados
    return {"erro": f"Time '{time}' não encontrado."}

FUNCS = {"listar_times": listar_times, "acesso_prob": acesso_prob}

TOOLS = [
    {"type": "function", "function": {

    "name": "listar_times",
    "description": "Listar os nomes dos times",
    "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
     "name": "acesso_prob",
     "description": "Lista dados sobre um time específico",
     "parameters": {"type": "object",
                    "properties": {"time": {"type": "string"}},
                        "required": ["time"]}}}
]

def main():
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": PERGUNTA}
    ]

    for passo in range(1, MAX_PASSOS + 1):
        r = ollama.chat(
            model=MODEL,
            messages=msgs,
            tools=TOOLS
        )
        msgs.append(r["message"])

        if not r["message"].tool_calls:
            print(f"\n Concluído com sucesso em {passo} passo(s)!")
            print(f"Resposta final:\n{r['message'].content}")
            return

        for call in r["message"].tool_calls:
            nome = call.function.name
            args = call.function.arguments

            print(f"Chamando Tool: {nome}({args})")
            resultado = FUNCS[nome](**args)
            print(f"Resultado da Tool: {resultado}")

            msgs.append({
                "role": "tool",
                "content": json.dumps(resultado)
            })
    else:
        print(f"\nLimite de {MAX_PASSOS} passos atingido sem resposta definitiva.")

if __name__ == "__main__":
    main()