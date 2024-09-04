from config import bot
from telebot.types import Message
from telebot.types import Voice
from config import BOT_TOKEN
import requests
from yandex_cloud import get_text_from_speech
from config import YC_STT_API_KEY
import requests
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

yandex_cloud_catalog = ""
yandex_api_key = ""
yandex_gpt_model = "yandexgpt-lite"
# Используем декоратор из объекта класса TeleBot, 
# в который передаем параметр commands - список команд, 
# при вызове которых будет вызываться данная функция
@bot.message_handler(commands=['start']) 
# Определяем функцию для обработки команды /start, она принимает объект класса Message - сообщение
def start(message:Message):
    # Отправляем новое сообщение, указав ID чата с пользователем и сам текст сообщения
    bot.send_message(message.chat.id, "Йоу! Отправь мне аудиосообщение")
@bot.message_handler(content_types=['voice'])
def handle_voice(message:Message):
    global speech_text
    # Определяем объект класса Voice, который находится внутри параметра message
# (он же объект класса Message)
    voice:Voice = message.voice
# Получаем из него ID файла аудиосообщения
    file_id = voice.file_id
# Получаем всю информацию о данном файле
    voice_file = bot.get_file(file_id)
# А уже из нее достаем путь к файлу на сервере Телеграм в директории
# с файлами нашего бота
    voice_path = voice_file.file_path
    file_base_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{voice_path}"
    # Сохраняем текст аудиосообщения в перменную
    speech_text = get_text_from_speech(file_base_url)
# Посылаем его пользователю в виде нового собщения
    try:
        bot.send_message(message.chat.id, speech_text)
    except:
        bot.send_message(message.chat.id, "Не удалось распознать. Это может быть по нескольким причинам:\n 1)Сообщение слишком длинное, текущая версия бота работает для сообщений до 30 секунд\n 2)Сообщение невозможно разобрать, попробуйте записать в тихом месте\n 3)Пустое сообщение")
    
    system_prompt = (
        "Сделай краткий конспект текста. Выведи только конспект, без лишних символов и вступления. В начале напиши 'Вот конспект аудиосообщения:' "
    )
    answer = send_gpt_request(system_prompt, speech_text)
    bot.send_message(message.chat.id, answer)
    
def send_gpt_request(system_prompt: str, user_prompt: str):
    body = {
        "modelUri": f"gpt://{yandex_cloud_catalog}/{yandex_gpt_model}",
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "2000"},
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_prompt},
        ],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {yandex_api_key}",
        "x-folder-id": yandex_cloud_catalog,
    }
    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return "ERROR"
    
    response_json = response.json()  # Используем более надежный метод json()
    
    if "result" not in response_json:
        return "ERROR: result not found in response"
    
    answer = response_json["result"]["alternatives"][0]["message"]["text"]
    
    if len(answer) == 0:
        return "ERROR: Empty answer"

    return answer


bot.polling()




'''
fuck them all!'''
"Не удалось распознать аудиофайл. Это может быть по нескольким причинам: \n 1)Вы тупой пидорас и не умеете говорить и записывать гс \n 2)Я тупой пидорас и не распознал ваше глупейшее сообщение, записанное на нокию 2007 года. \n 3)Мы все тупые пидорасы и сервер лег, отъебись пж."