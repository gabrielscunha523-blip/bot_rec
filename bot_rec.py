# PROJETO FACULDADE 

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
from openai import OpenAI

OPENAI_API_KEY = "_"
WHATSAPP_TOKEN = "_"
WHATSAPP_NUMBER = "_"
VERIFY_TOKEN = "_" 

client = OpenAI(api_key=OPENAI_API_KEY)

GRAPH_URL = f"https://graph.facebook.com/v20.0/{WHATSAPP_NUMBER}/messages"

app = FastAPI()


def gerar_resposta_com_ia(pergunta: str) -> str:
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",  # mais barato -aprox 10,00
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em reciclagem, consumo consciente e ODS."},
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


# Verificação inicial do webhook
@app.get("/webhook")
def verificar(mode: str = None, challenge: str = None, token: str = None):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Erro de verificação", status_code=403)


# Recebendo mensagens do usuário 
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
            de = msg["from"]  # número do usuário
            if msg["type"] == "text":
                pergunta = msg["text"]["body"]
                resposta = gerar_resposta_com_ia(pergunta)
                enviar_whatsapp_texto(to=de, text=resposta)
            else:
                enviar_whatsapp_texto(to=de, text="Só consigo responder mensagens de texto no momento.")
    except Exception as e:
        print("Erro no webhook:", e)

    return {"status": "ok"}
