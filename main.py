import os
import stripe
from fastapi import FastAPI, Request
from telegram import Bot
from telegram.ext import ApplicationBuilder

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()


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
            await bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=int(telegram_id))
        except:
            pass

    elif event["type"] == "invoice.payment_failed":
        session = event["data"]["object"]
        customer = stripe.Customer.retrieve(session["customer"])
        telegram_id = customer["metadata"].get("telegram_id")
        try:
            await bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=int(telegram_id))
        except:
            pass

    return {"status": "success"}


@app.get("/")
async def root():
    return {"message": "Bot funcionando correctamente."}
