from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import telebot
from django.conf import settings
import os
from .utils import create_user_remind
from .models import Poll, Choice, Vote, User, PossibleVote


bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
admin = os.environ.get("TELEGRAM_LOGS_CHAT_ID", 5343742264)
ngrok_url = os.environ.get("NGROK_URL")


@api_view(['GET'])
def set_telegram_webhook(request):
    print("I AM ALIVE")
    webhook = bot.set_webhook(f'{ngrok_url}/api/v1/telegram/webhook/')
#     webhook = bot.delete_webhook()
    
    print(webhook)
    print("WEB HOOK SET")
    bot.send_message(admin, f'Привет!\n')
    
    return Response({"success": "True"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def telegram_webhook(request):
       if request.method == "POST":
              print("Обработка ответа от телеги")
              update = telebot.types.Update.de_json(request.body.decode('utf-8'))
              print(update)
              bot.process_new_updates([update])
       return Response({"success": "True"}, status=status.HTTP_200_OK)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    name = ''
    if message.from_user.last_name is None:
        name = f'{message.from_user.first_name}'
    else:
        name = f'{message.from_user.first_name} {message.from_user.last_name}'
    try:
        text = f'''Привет! {name}
        Я бот, который может создавать уведомления для вас и проводить опросы.
        Чтобы создать уведомление, просто напиши когда вас уведомить и на какую тему.
        Чтобы пройти опрос, вызовите соответствующую команду - /poll. 
        Вы получите последний созданный опрос'''
        bot.send_message(message.chat_id, text)
        user = User.objects.create(
            username=message.from_user.first_name,
            telegram_username=message.from_user.username,
            telegram_id=message.from_user.id,
        )
        user.save()
    except Exception as e:
       text = str(e)
       bot.send_message(admin, text)


@bot.message_handler(content_types=["text"])
def create_reminder_from_text(message):
    create_user_remind(
        username=message.from_user.first_name,
        telegram_username=message.from_user.username,
        telegram_id=message.from_user.id,
        user_message_id=message.id,
        user_remind_message=message.text
    )
    bot.send_message(message.chat.id, "Окей, напомню.")


@bot.message_handler(commands=['poll'])
def start(message: telebot.types.Message):
    poll = Poll.objects.last()
    choices = Choice.objects.filter(poll=poll)
    choices_list = [choice.id for choice in choices]
    sent_message = bot.send_message(message.chat.id, f"Название опроса - {poll.title}")
    bot.register_next_step_handler(
        sent_message,
        survey,
        choices=choices,
        choices_list=choices_list
    )


def survey(message, choices, choices_list):
    if choices_list == []:
        bot.send_message(message.chat.id, "Опрос окончен")
        return
    
    for i in choices_list:
        
        if message.text:
            try:
                choice_vote = PossibleVote.objects.get(text=message.text)
            except PossibleVote.DoesNotExist:
                choice_vote = None
            vote = Vote.objects.create(
                user=User.objects.get(telegram_id=message.from_user.id),
                choice=choice_vote.choice if choice_vote is not None else None,
                choice_text=message.text
            )
            vote.save()

        choice_object = choices.get(id=i)
        if choice_object.text_from_user == True:
            user_message = bot.send_message(message.chat.id, f"Введите ответ на вопрос - {choice_object.choice_text}")
            choices_list.remove(i)
            bot.register_next_step_handler(
                user_message,
                survey,
                choices=choices,
                choices_list=choices_list
            )
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markups = PossibleVote.objects.filter(choice=choice_object)
        for j in markups:
            markup.add(f"{j.text}")
        user_message = bot.send_message(message.chat.id, f"Ответьте на вопрос одним из предложенных вариантов - {choice_object.choice_text}")
        choices_list.remove(i)
        bot.register_next_step_handler(
                user_message,
                survey,
                choices=choices,
                choices_list=choices_list
            )
