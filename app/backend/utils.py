from django.db import DatabaseError, transaction
from .models import User, Reminder
from datetime import datetime
from openai import OpenAI
import os
from .tasks import bot_reply_to


#todo: get api key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))
MODEL = "gpt-3.5-turbo"


def call_ai_api(user_message_for_remaind):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{user_message_for_remaind}. Исходя из этого, напиши дату и время напоминания и суть напоминания, написав только дату и суть через запятую формат даты - гггг-мм-дд чч:мм"},
        ],
        temperature=0,
    )
    response_text = response.choices[0].message.content
    message_text_from_ai = response_text.split(',')[0]
    time_to_remind_from_ai = response_text.split(',')[1]
    return [message_text_from_ai, time_to_remind_from_ai]\
    

def create_user_remind(
        username: str, telegram_username: str, 
        telegram_id: int, user_message_id, 
        user_remind_message, bot):
    ai_response = call_ai_api(user_message_for_remaind=user_remind_message)
    message_text_from_ai, time_to_remind_from_ai = ai_response[0], datetime.strptime(ai_response[1], '%Y-%m-%d %H:%M')
    with transaction.atomic():
        reminder_str = "Привет, ты просил напомнить "
        user = User.objects.get_or_create(
            username=username,
            telegram_username=telegram_username,
            telegram_id=telegram_id
        )
        user.save()
        remind = Reminder.objects.create(
            user_message_id=user_message_id,
            message_text=reminder_str.join(message_text_from_ai),
            time_to_remind=time_to_remind_from_ai,
            user=user
        )
        remind.save()

    #todo: celery task test
    bot_reply_to.apply_async(
        message_id=remind.user_message_id, 
        text=remind.message_text, bot=bot, eta=time_to_remind_from_ai
    )

