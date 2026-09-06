import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from agent.orchestrator import process_message


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🛒 Welcome to KiranaOS AI!\n\n"
        "Your AI-powered Kirana store assistant.\n\n"
        "Try:\n"
        "• Check Maggi stock\n"
        "• Add 5 Maggi to my bill\n"
        "• Show my bill\n"
        "• Finalize my bill\n"
        "• What is Arun's balance?\n"
        "• What is low in stock?\n"
        "• How much did I sell today?\n"
        "• Give me today's business report"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return

    message = update.message.text
    user_id = str(update.effective_user.id)

    print("\nUser ID:", user_id)
    print("Message:", message)

    try:

        result = process_message(
            message,
            user_id=user_id
        )

        if isinstance(result, dict):

            response_text = result.get(
                "text",
                "Done."
            )

            await update.message.reply_text(
                response_text
            )

            artifact_file = result.get(
                "artifact_file"
            )

            if (
                artifact_file
                and os.path.exists(artifact_file)
            ):

                if artifact_file.lower().endswith(".pdf"):

                    with open(
                        artifact_file,
                        "rb"
                    ) as file:

                        await update.message.reply_document(
                            document=file,
                            caption="🧾 Your invoice is attached."
                        )

                elif artifact_file.lower().endswith(".pptx"):

                    with open(
                        artifact_file,
                        "rb"
                    ) as file:

                        await update.message.reply_document(
                            document=file,
                            caption="📊 Your business analysis report is attached."
                        )

        else:

            await update.message.reply_text(
                str(result)
            )

    except Exception as error:

        print("ERROR:", error)

        await update.message.reply_text(
            "❌ Sorry, I couldn't complete the request."
        )


def main():

    if not TOKEN:

        print(
            "ERROR: TELEGRAM_BOT_TOKEN not found in .env"
        )

        return

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print(
        "KiranaOS AI Telegram Bot is running..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()