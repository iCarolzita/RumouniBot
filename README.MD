# RumouniBot

**Bot de Telegram educativo para alunos do ensino secundário**

O RumouniBot ajuda os alunos a explorar cursos universitários, notas de entrada e informações sobre universidades em Portugal. O bot utiliza a API da OpenAI para gerar respostas educativas em português de Portugal.

---

## Funcionalidades

- `/start` — Inicia o bot e apresenta os comandos disponíveis  
- `/curiosidade` — Gera curiosidades educativas sobre cursos universitários  
- `/dica` — Envia dicas motivacionais para estudantes  
- `/ranking` — Lista os cursos universitários mais concorridos, com links oficiais  
- `/universidades` — Resumos rápidos de universidades em Portugal  
- `/sobre` — Explica a utilidade do bot e fornece links úteis  

O bot também responde a perguntas livres dos utilizadores mantendo um histórico de conversas.

---

## Requisitos

- Python 3.11 ou superior  
- Pacotes Python:
  - `python-telegram-bot`
  - `openai`
  - `python-dotenv`
  - `nest_asyncio`

```bash
pip install python-telegram-bot openai python-dotenv nest_asyncio
```

---

## Configuração

Crie um ficheiro `.env` na raiz do projeto com o seguinte conteúdo:

```
OPENAI_API_KEY=coloque_aqui_a_sua_chave_openai
TELEGRAM_TOKEN=coloque_aqui_o_token_do_seu_bot_telegram
CHAT_ID_ALERTA=opcional_id_do_chat_para_alertas
```

---

## Como executar

No terminal, execute:

```bash
python bot.py
```

Depois, no Telegram, procure pelo bot @UniGuiaBot e envie o comando `/start`.

---

## Exemplos de utilização

- "Quais são as notas de entrada para Medicina?"
- "Dá-me uma dica para estudar melhor."
- "Quais são as universidades mais antigas em Portugal?"

---

## Contributos

Sugestões e melhorias são bem-vindas!  
Para contribuir, faça um fork ou envie um pull request.
