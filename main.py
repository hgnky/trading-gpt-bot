import logging
import openai
import os
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

PROMPT_TEXT = """
Baca chart berikut dan analisa apakah ada setup valid berdasarkan strategi:
- Sweep + MSSS / CISD pada candle ke-2
- Entry di candle ke-3
- POI: FVG atau Pivot
- Atau Engulf candle
- Hitung RR min 2R atau TP dengan SD 2.5 - 4
- Validasi juga pakai intermarket (misal DXY/SPX)
Berikan hasil berupa: entry / TP / SL / analisa / valid atau tidak.
"""

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    logging.info("Image received, sending to GPT-4 Vision...")

    completion = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": PROMPT_TEXT },
                    { "type": "image_url", "image_url": { "url": f"data:image/jpeg;base64,{image_base64}" } }
                ]
            }
        ],
        max_tokens=1000,
    )

    reply = completion.choices[0].message.content
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.run_polling()

if __name__ == "__main__":
    main()
