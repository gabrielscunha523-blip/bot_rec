# PROJETO FACULDADE

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
from openai import OpenAI

# Carrega as variaveis do arquivo .env (nunca commitado no git)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

GRAPH_URL = f"https://graph.facebook.com/v20.0/{WHATSAPP_NUMBER}/messages"

app = FastAPI()


def gerar_resposta_com_ia(pergunta: str) -> str:
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",  # mais barato -aprox 10,00
            messages=[
                {"role": "system", "content": "Voce e um assistente especializado em reciclagem, consumo consciente e ODS."},
                {"role": "user", "content": pergunta}
            ],
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"


def enviar_whatsapp_texto(to: str, text: str):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(GRAPH_URL, headers=headers, json=payload)
    if r.status_code >= 400:
        print("Erro ao enviar mensagem:", r.text)


# Verificacao inicial do webhook
@app.get("/webhook")
def verificar(mode: str = None, challenge: str = None, token: str = None):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Erro de verificacao", status_code=403)


# Recebendo mensagens do usuario
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg = messages[0]
            de = msg["from"]  # numero do usuario
            if msg["type"] == "text":
                pergunta = msg["text"]["body"]
                resposta = gerar_resposta_com_ia(pergunta)
                enviar_whatsapp_texto(to=de, text=resposta)
            else:
                enviar_whatsapp_texto(to=de, text="So consigo responder mensagens de texto no momento.")
    except Exception as e:
        print("Erro no webhook:", e)

    return {"status": "ok"}
