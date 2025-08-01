import os
import stripe
from fastapi import FastAPI, Request
from telegram import Bot

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # Ejemplo: -1001234567890
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")  # ejemplo: https://tu-bot.onrender.com
bot = Bot(token=TELEGRAM_BOT_TOKEN)


@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = session["client_reference_id"]
        try:
            bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=telegram_id)
        except:
            pass  # por si ya está dentro
        bot.invite_link_create(chat_id=CHANNEL_ID, member_limit=1)

    elif event["type"] == "invoice.payment_failed":
        session = event["data"]["object"]
        customer = stripe.Customer.retrieve(session["customer"])
        telegram_id = customer["metadata"].get("telegram_id")
        try:
            bot.kick_chat_member(chat_id=CHANNEL_ID, user_id=int(telegram_id))
        except:
            pass

    return {"status": "success"}


@app.get("/")
async def root():
    return {"message": "Bot funcionando correctamente."}
