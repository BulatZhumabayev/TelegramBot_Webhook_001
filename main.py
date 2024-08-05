import logging
import fastapi
import uvicorn
import telebot
import random
from telebot import types
import os

API_TOKEN = os.environ.get('API_TOKEN')

helloText = """КАК ИСПОЛЬЗОВАТЬ ВОПРОСЫ:

🔹 Данный бот содержит 122 вопроса. Нажимайте на кнопку "👋 Получить вопрос"

🔹 Предложите вашему ребёнку поиграть с вами в игру "Ответь на вопрос". Вы по очереди выбираете вопрос и даёте на него ответ. Если вопрос не нравится то можно выбрать следующий. Никакого давления.

🔹 Данным ботом можно пользовать в дороге или при ожидании в очереди, чтобы поговорить с ребёнком и весело провести время. Или договоритесь отвечать по одному вопросу  перед ужином, когда вся семья садится кушать. Или может быть устраивайте семейную встречу на выходных с десертом, фильмом и потом ответом на вопросы. Любое время и любая форма общения с использованием этих вопросов будут полезны.

🔹 Не давите на ребёнка когда он отвечает на вопросы. Не ждите каких-то особенно умных или развёрнутых ответов. Радуйтесь всему что ребёнок решает вам сообщить отвечая на вопросы. Фокусируйтесь на том как вы отвечаете на вопросы которые попадают вам. Очень важно, чтобы в этом общении не было давления или особых ожиданий друг от друга. Чтобы это время было просто спокойным и приятным временем вместе с ребёнком.

🔹 Вы можете выбрать разные вариант, либо каждый выбирает вопросы по очереди и отвечают каждый на свой вопрос. Либо подросток выбирает вопрос в боте и потом все участники отвечают на один и тот же вопрос. Либо можете использовать любые правила которые предложит вам ваш ребёнок.

🔹 Заранее договоритесь со всеми участниками игры о том, что то, что вы рассказываете друг другу отвечая на вопросы останется только между вами.
Подчеркивайте что ваши разговоры строго конфиденциальны. Тогда все участники будут чувствовать себя более расслабленно."""

howPlay = '✨Как играть?'
getQuestion = '👋 Получить вопрос'


WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr


# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

def read_file(path):
    fo = open(path, 'r')
    text = fo.read()
    fo.close()
    return text.splitlines()


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = fastapi.FastAPI(docs=None, redoc_url=None)

path = "./resources/data.txt"
questions = read_file(path)
maxLength = len(questions)

@app.get("/hello")
def hello_page():
    return {"message": "_Hello_"}


@app.post(f'/{API_TOKEN}/')
def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    """
    Handle '/start' and '/help'
    """
    # bot.reply_to(message, ("Hi there, I am EchoBot.\n" "I am here to echo your kind words back to you."))

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(howPlay)
    btn2 = types.KeyboardButton(getQuestion)
    keyboard.add(btn1, btn2)
    bot.send_message(message.from_user.id, helloText, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_questions(message):
    """
    Handle all other messages
    """
    # bot.reply_to(message, message.text)
    if message.text == getQuestion:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton(howPlay)
        btn2 = types.KeyboardButton(getQuestion)

        index = random.randint(0, maxLength-1)

        keyboard.add(btn1, btn2)
        bot.send_message(message.from_user.id, questions[index], reply_markup=keyboard) #ответ бота
    elif message.text == howPlay:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton(howPlay)
        btn2 = types.KeyboardButton(getQuestion)

        keyboard.add(btn1, btn2)
        bot.send_message(message.from_user.id, helloText, reply_markup=keyboard) #ответ бота

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

print('set_webhook = ', WEBHOOK_URL_BASE, WEBHOOK_URL_PATH)

# Set webhook
bot.set_webhook(
    url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
    #,certificate=open(WEBHOOK_SSL_CERT, 'r')
)


uvicorn.run(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT
    #,
    #ssl_certfile=WEBHOOK_SSL_CERT,
    #ssl_keyfile=WEBHOOK_SSL_PRIV
)
