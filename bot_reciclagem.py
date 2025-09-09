#REFERENCIAS:
# OPENAI_API => https://www.youtube.com/watch?v=Y9gOf4we3tk
# PEGAR TOKEN PERMANENTE => https://www.youtube.com/watch?v=X9sC14OgP6g

# PROJETO FACULDADE 

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
from openai import OpenAI

# === CONFIGURAÇÕES ===
# arquivo .env
OPENAI_API_KEY = "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"
WHATSAPP_TOKEN = "EAALSqOOy5ZAsBPXEG0st4PoaLkO7v8POicenIQiHQ0ZCAOImsu0tEZBclcorIUBtUYc6jshdSSKN0Gb9oxH8jcZBWXUe4ZBCql5OmhWAz22Gq8ZAY9NsYE2bviZAvibCKiZBvTpAzEjvoJjiWFqDnRprmlzSRysEDjzo0CaPXridFLAZC9Y50DadVxyfyqFD3yul3SEsoutnTrbAsZBm3JXgXxye5dthWddajxrWZAywfyKDwZDZD"
WHATSAPP_NUMBER_ID = "794274533762527"
VERIFY_TOKEN = "AMIGO2002"  # Você escolhe e cadastra no painel da Meta

client = OpenAI(api_key=OPENAI_API_KEY)

GRAPH_URL = f"https://graph.facebook.com/v20.0/{WHATSAPP_NUMBER_ID}/messages"

# Cria o app FastAPI
app = FastAPI()


#FUNÇÃO DE IA
def gerar_resposta_com_ia(pergunta: str) -> str:
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",  # mais barato que gpt-4 - 20,00
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em reciclagem, consumo consciente e ODS."},
                {"role": "user", "content": pergunta}
            ],
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"


#FUNÇÃO PARA ENVIAR RESPOSTA NO WHATSAPP
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


# ENDPOINTS

# Verificação inicial do webhook (Meta chama GET)
@app.get("/webhook")
def verificar(mode: str = None, challenge: str = None, token: str = None):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Erro de verificação", status_code=403)


# Recebendo mensagens do usuário (Meta chama POST)
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
