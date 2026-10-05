
import os, sqlite3, json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "memory.db")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_memories():
    conn = db()
    rows = conn.execute("SELECT content FROM memories ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return [r["content"] for r in rows]

def add_memory(content):
    conn = db()
    conn.execute("INSERT INTO memories(content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

SYSTEM = """Você é o assistente pessoal de um projeto chamado JARVIS V1.
Responda em português do Brasil, de forma natural, clara e útil.
Priorize qualidade da resposta e raciocínio cuidadoso, sem inventar fatos.
Você é um assistente geral: pode explicar assuntos, responder perguntas,
ajudar a estudar, organizar ideias e conversar.

Memória:
- Abaixo estão memórias que o usuário pediu explicitamente para guardar.
- Use-as quando forem relevantes.
- Nunca diga que lembra de algo se não estiver na memória ou na conversa atual.
- Se o usuário disser "lembre que...", "guarde que..." ou equivalente,
  a aplicação tentará salvar o conteúdo separadamente.

Memórias atuais:
{memories}
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    history = data.get("history") or []
    if not message:
        return jsonify({"error": "Mensagem vazia."}), 400

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return jsonify({"error": "OPENAI_API_KEY não configurada no servidor."}), 500

    # Simple explicit-memory command handling.
    lower = message.lower()
    prefixes = ["lembre que ", "lembre-se que ", "guarde que ", "memorize que "]
    for p in prefixes:
        if lower.startswith(p):
            memory = message[len(p):].strip()
            if memory:
                add_memory(memory)
                return jsonify({
                    "answer": f"Entendido. Vou guardar esta informação: {memory}",
                    "memory_saved": True
                })

    memories = get_memories()
    client = OpenAI(api_key=key)

    # Keep a modest conversation window so the V1 stays responsive.
    recent = history[-12:]
    input_items = []
    for item in recent:
        role = item.get("role")
        content = item.get("content", "")
        if role in ("user", "assistant") and content:
            input_items.append({"role": role, "content": content})
    input_items.append({"role": "user", "content": message})

    response = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-5.6-luna"),
        instructions=SYSTEM.format(memories="\n".join(f"- {m}" for m in memories) or "(nenhuma)"),
        input=input_items,
    )
    return jsonify({"answer": response.output_text, "memory_saved": False})

@app.get("/api/memories")
def memories():
    return jsonify({"memories": get_memories()})

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
