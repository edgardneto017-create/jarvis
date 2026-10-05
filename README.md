# JARVIS V1

Aplicativo web simples para celular, com uma interface limpa e uma IA baseada na OpenAI.

## Recursos
- Conversa por texto.
- Memória explícita: escreva "Lembre que ..." para guardar uma informação.
- Memórias ficam em SQLite no servidor.
- Histórico da conversa atual fica na interface.
- Pronto para receber câmera/voz no futuro.

## Rodar localmente
1. Instale Python 3.11+.
2. `pip install -r requirements.txt`
3. Defina `OPENAI_API_KEY`.
4. Opcionalmente defina `OPENAI_MODEL` (padrão: `gpt-5.6-luna`).
5. `python app.py`
6. Abra `http://localhost:5000`.

## Publicar no Render
1. Suba esta pasta para um repositório GitHub.
2. No Render, crie um Web Service a partir do repositório.
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Environment variable: `OPENAI_API_KEY` = sua chave.
6. Opcional: `OPENAI_MODEL` = `gpt-5.6-luna`.

NUNCA coloque a chave da API no HTML/JavaScript. Ela deve ficar somente como variável de ambiente do servidor.
