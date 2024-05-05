from celery import shared_task


@shared_task()
def bot_reply_to(message_id, text, bot):
    bot.reply_to(message_id, text)
