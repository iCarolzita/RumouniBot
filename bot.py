# Este código foi feito por Carolina Fernandes
# bot.py
# Bot de Telegram para alunos do ensino secundário
# Usa OpenAI para gerar todas as respostas educativas em PT-PT
# 
# Para iniciar o bot no Telegram, envie o comando /start ao bot.
# Certifique-se de que as variáveis de ambiente estão configuradas (.env).

import os
import random
import nest_asyncio
from dotenv import load_dotenv
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

# Permite a execução de código assíncrono em ambientes que não suportam asyncio nativamente
nest_asyncio.apply()

# =======================
# CONFIGURAÇÃO
# =======================
load_dotenv()  # Carrega variáveis de ambiente do ficheiro .env
openai.api_key = os.getenv("OPENAI_API_KEY")  # Chave da API OpenAI
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token do bot Telegram
CHAT_ID_ALERTA = int(os.getenv("CHAT_ID_ALERTA", "0"))  # ID do chat para alertas (opcional)

# Dicionário para guardar o histórico de conversas de cada utilizador
historico_usuarios = {}

# =======================
# LINKS REAIS PARA CURSOS
# =======================
# Dicionário com links oficiais para cursos populares
cursos_links = {
    "Medicina": "[Faculdade de Medicina da Univ. do Porto](https://sigarra.up.pt/fmup/pt/web_page.inicial)",
    "Engenharia Informática": "[Faculdade de Ciências e Tecnologia da Univ. Coimbra](https://www.uc.pt/fctuc)",
    "Gestão": "[ISCTE Business School](https://www.iscte-iul.pt/ensino/bs)",
    "Direito": "[Faculdade de Direito da Univ. Lisboa](https://www.fd.ulisboa.pt/pt)",
    "Psicologia": "[Faculdade de Psicologia da Univ. Lisboa](https://www.psicologia.ulisboa.pt/pt)"
}

# =======================
# FUNÇÃO AUXILIAR OPENAI
# =======================
async def perguntar_openai(prompt: str, max_tokens: int = 400) -> str:
    """Envia um prompt à OpenAI e devolve a resposta como texto limpo"""
    try:
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return resposta.choices[0].message.content.strip()
    except Exception:
        return "Não foi possível obter resposta neste momento. 🤔"

# =======================
# FUNÇÃO PARA MENSAGENS LONGAS (SEM CORTAR FRASES)
# =======================
async def enviar_texto_long(update, texto, parse_mode="Markdown"):
    """
    Divide mensagens longas em blocos de até 4000 caracteres sem cortar frases.
    Tenta separar por parágrafos ou pontos finais.
    """
    max_len = 4000
    partes = []

    while len(texto) > max_len:
        # Procura o último ponto ou quebra de linha antes do limite
        split_pos = max(texto.rfind('\n', 0, max_len), texto.rfind('. ', 0, max_len))
        if split_pos == -1:
            split_pos = max_len  # Se não encontrar, corta no limite
        partes.append(texto[:split_pos+1].strip())
        texto = texto[split_pos+1:].strip()

    if texto:
        partes.append(texto)

    for parte in partes:
        await update.message.reply_text(parte, parse_mode=parse_mode)

# =======================
# COMANDOS DO BOT
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Inicializa o histórico do utilizador ao iniciar o bot
    usuario_id = update.message.from_user.id
    historico_usuarios[usuario_id] = []

    await update.message.reply_text(
        "*Olá! 👋 Eu sou o RumouniBot.*\n\n"
        "Podes perguntar-me sobre cursos universitários e notas de entrada.\n\n"
        "📌 *Comandos úteis:*\n"
        "  /curiosidade - curiosidades sobre cursos 🎓\n"
        "  /dica - dicas motivacionais 💡\n"
        "  /ranking - cursos mais concorridos 🏆\n"
        "  /universidades - resumos rápidos de universidades 🏫\n"
        "  /sobre - informações e links úteis 🔗",
        parse_mode="Markdown"
    )

async def curiosidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Gera uma curiosidade educativa sobre cursos universitários
    prompt = "Gera uma curiosidade educativa sobre cursos universitários em Portugal. Usa emojis e linguagem curta para alunos do secundário."
    texto = await perguntar_openai(prompt, 100)
    await enviar_texto_long(update, texto)

async def dica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Gera uma dica motivacional para alunos do secundário
    prompt = "Gera uma dica motivacional para alunos do ensino secundário, sobre estudar, notas e motivação. Usa emojis e linguagem curta."
    texto = await perguntar_openai(prompt, 80)
    await enviar_texto_long(update, texto)

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Lista os cursos mais concorridos e insere links oficiais
    prompt = (
        "Lista os 5 cursos universitários mais concorridos em Portugal em 2025. "
        "Para cada curso, escreve uma curiosidade educativa de 1 linha e a nota média de entrada. "
        "Não coloques links, vamos usar os links oficiais do dicionário. "
        "Formata em Markdown."
    )
    texto = await perguntar_openai(prompt, max_tokens=400)

    # Substitui os placeholders pelos links reais dos cursos
    for curso, link_md in cursos_links.items():
        texto = texto.replace(f"{curso} - Link oficial", f"{link_md}")
        if curso in texto:
            texto = texto.replace(curso, f"{curso} - {link_md}")

    await enviar_texto_long(update, texto)

async def universidades(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Mostra as primeiras universidades e prepara botão para ver mais
    context.user_data["contador_universidades"] = 0
    context.user_data["universidades_mostradas"] = []

    prompt = "Gera uma lista das 3 primeiras universidades de Portugal com breve descrição educativa e emojis. Sem numeração."
    novas = await perguntar_openai(prompt, 150)
    novas_universidades = [linha.strip() for linha in novas.split("\n") if linha.strip()]

    texto_numerado = ""
    for uni in novas_universidades:
        context.user_data["contador_universidades"] += 1
        texto_numerado += f"{context.user_data['contador_universidades']}. {uni}\n"

    context.user_data["universidades_mostradas"] = [texto_numerado]

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Ver mais 3 universidades", callback_data="mostrar_3")]])
    await update.message.reply_text(texto_numerado, reply_markup=keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Mostra mais universidades quando o utilizador clica no botão
    query = update.callback_query
    await query.answer()

    if query.data == "mostrar_3":
        contador = context.user_data.get("contador_universidades", 0)
        ja_mostradas = context.user_data.get("universidades_mostradas", [])

        prompt = "Gera 3 universidades em Portugal que ainda não foram mencionadas, cada uma com resumo educativo de 2-3 linhas e emojis. Sem numeração."
        novas = await perguntar_openai(prompt, 150)
        novas_universidades = [linha.strip() for linha in novas.split("\n") if linha.strip()]

        texto_numerado = ""
        for uni in novas_universidades:
            contador += 1
            texto_numerado += f"{contador}. {uni}\n"

        ja_mostradas.append(texto_numerado)
        context.user_data["contador_universidades"] = contador
        context.user_data["universidades_mostradas"] = ja_mostradas

        # Limita a apresentação a 18 universidades
        if contador >= 18:
            keyboard = None
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Ver mais 3 universidades", callback_data="mostrar_3")]])

        await query.edit_message_text("\n".join(ja_mostradas), reply_markup=keyboard)

async def sobre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Explica a utilidade do bot e adiciona links úteis
    prompt = (
        "Escreve uma mensagem educativa e amigável explicando a utilidade de um bot "
        "para alunos do ensino secundário. Inclui exemplos de como pode ajudar nos estudos, "
        "resumos de cursos, dicas e links úteis de universidades e ensino superior em Portugal. "
        "Termina a mensagem com uma conclusão motivacional completa. "
        "Não cortes frases no final. Garante que a resposta seja contínua e completa. "
        "Formata em Markdown para Telegram."
    )
    texto = await perguntar_openai(prompt, max_tokens=400)

    # Adiciona links úteis fixos à mensagem
    links_utiles = "\n\nLinks úteis:\n- [DGES](https://www.dges.gov.pt)\n- [Universia Portugal](https://www.universia.pt)\n- [Estudante.pt](https://www.estudante.pt)"
    texto += links_utiles

    await enviar_texto_long(update, texto)

# =======================
# RESPOSTAS LIVRES
# =======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Responde a perguntas livres, mantendo o histórico do utilizador
    usuario_id = update.message.from_user.id
    user_text = update.message.text

    if usuario_id not in historico_usuarios:
        historico_usuarios[usuario_id] = []

    historico_usuarios[usuario_id].append({"role": "user", "content": user_text})
    historico_usuarios[usuario_id] = historico_usuarios[usuario_id][-10:]  # Mantém apenas as últimas 10 mensagens

    # Mensagem de sistema para orientar a IA a responder em PT-PT e de forma educativa
    system_message = (
        "És um assistente educativo em Português de Portugal. "
        "Responde de forma clara, natural e amigável sobre cursos e notas. "
        "Inclui exemplos de notas típicas, sugere cursos por nota, explica termos difíceis, usa emojis e links quando possível."
    )

    mensagens_gpt = [{"role": "system", "content": system_message}] + historico_usuarios[usuario_id]

    try:
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensagens_gpt,
            max_tokens=400
        )
        bot_reply = resposta.choices[0].message.content.strip()
        # Acrescenta uma frase motivacional aleatória no final da resposta
        frases_motivacionais = [
            "Lembra-te: cada esforço conta! 🌟",
            "Continua a estudar, vais conseguir! 💪",
            "O teu futuro depende do que fazes hoje! 📚✨"
        ]
        bot_reply += f"\n\n_{random.choice(frases_motivacionais)}_"
        historico_usuarios[usuario_id].append({"role": "assistant", "content": bot_reply})
    except Exception:
        bot_reply = "Desculpa, houve um problema a processar a tua pergunta. 🤔"

    await enviar_texto_long(update, bot_reply)

# =======================
# CONFIGURAÇÃO DO BOT
# =======================
def main():
    # Inicializa a aplicação do Telegram e regista os handlers dos comandos
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("curiosidade", curiosidade))
    app.add_handler(CommandHandler("dica", dica))
    app.add_handler(CommandHandler("ranking", ranking))
    app.add_handler(CommandHandler("universidades", universidades))
    app.add_handler(CommandHandler("sobre", sobre))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()  # Inicia o bot e fica à escuta de mensagens

if __name__ == "__main__":
    main()
