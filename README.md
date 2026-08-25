# Bot de Reciclagem: 

Bot de WhatsApp que responde dúvidas sobre reciclagem, descarte correto e consumo consciente, usando IA pra gerar as respostas.

Feito como projeto da faculdade, relacionado ao ODS 12 (Consumo e Produção Responsáveis).

# Como funciona: 

O usuário manda uma mensagem de texto pro número de WhatsApp configurado. O Meta (dono da API do WhatsApp Business) encaminha essa mensagem pro webhook do bot, que manda a pergunta pra API da OpenAI e devolve a resposta pelo próprio WhatsApp.

#Tecnologias
Python
FastAPI
OpenAI API (modelo gpt-4o-mini, mais barato)
WhatsApp Business API (Meta)
Pré-requisitos
Python 3.10 ou superior
Conta no Meta for Developers com o WhatsApp Business API configurado
Chave de API da OpenAI
Configuração

# Instale as dependências:

pip install -r requirements.txt

Copie o .env.example pra .env:

cp .env.example .env

# Preencha com suas credenciais:

OPENAI_API_KEY=sua_chave_da_openai
WHATSAPP_TOKEN=seu_token_do_whatsapp_business
WHATSAPP_NUMBER=numero_configurado_no_meta
VERIFY_TOKEN=uma_chave_qualquer_que_voce_inventa_pra_verificacao_do_webhook

O .env não vai pro GitHub (já está no .gitignore) - as chaves ficam só no seu computador.

# Rodando

uvicorn bot_rec:app --reload

Pra testar de verdade com o WhatsApp, o Meta precisa conseguir chamar seu webhook, e ele não enxerga localhost. Enquanto eu tava desenvolvendo, usei o ngrok pra expor a porta:

ngrok http 8000

Depois cadastra a URL que o ngrok gerou como webhook no painel do Meta for Developers, junto com o VERIFY_TOKEN do seu .env.

# Limitações atuais

Só responde mensagem de texto. Se o usuário manda áudio, imagem ou figurinha, o bot devolve um aviso padrão em vez de processar - fica como próximo passo.
