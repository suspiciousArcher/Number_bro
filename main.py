import telebot
import webbrowser
from telebot import types
import scripts
import requests

bot = telebot.TeleBot('6354469033:AAF-ARfr9km4-GJRr011Gi7iv30BNXm0W68')

markup_inLine = types.InlineKeyboardMarkup()
markup_reply = types.ReplyKeyboardMarkup()

@bot.message_handler(commands=['fakt'])
def open_web(message):
    translate = scripts.Translate()
    number = message.text.split()
    type = 'trivia'
    API = f'http://numbersapi.com/{number[1]}/{type}'
    print(requests.get(API).text)
    result = translate.translate(requests.get(API).text)
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['start'])
def start(message):
    db_connect = scripts.ConnectDb()

    sql = 'INSERT INTO users (login, user_id) VALUES ("%s", "%s")' %(message.from_user.first_name, message.from_user.id)
    otvet = db_connect.registration(sql, message.from_user.id)
    bot.send_message(message.chat.id, otvet)

@bot.message_handler(commands=['json'])
def json(message):
    print(message)

@bot.message_handler(commands=['test'])
def test(message):
    button_1 = types.InlineKeyboardButton('Перейти в поисковик', url='https://ya.ru/')
    button_2 = types.InlineKeyboardButton('Ответить', callback_data='otvet')
    button_3 = types.InlineKeyboardButton('Удалить', callback_data='delete')
    button_4 = types.InlineKeyboardButton('getObject', callback_data='getObject')
    markup_inLine.row(button_1)
    markup_inLine.row(button_2, button_3)
    markup_inLine.row(button_4)
    # markup.add(types.InlineKeyboardButton('Перейти в поисковик', url='https://ya.ru/'))
    bot.reply_to(message, 'Давай проверим', reply_markup=markup_inLine)

@bot.message_handler(commands=['clear'])
def clear_button(message):
    button_1 = types.KeyboardButton('YES')
    button_2 = types.KeyboardButton('NO')
    markup_reply.row(button_1, button_2)
    bot.reply_to(message, 'Очистить историю чата?', reply_markup=markup_reply)
    bot.register_next_step_handler(message, clear)

def clear(message):
    if message.text == 'YES' or message.text == 'Да':
        print(message)
        for i in range(int(message.message_id + 1)):
            try:
                bot.delete_message(message.chat.id, i)
            except:
                continue
    elif message.text == 'NO' or message.text == 'Нет':
        bot.send_message(message.chat.id, 'Фуф, пронесло...')

@bot.callback_query_handler(func=lambda callback: True)
def otvet(callback):
    if callback.data == 'otvet':
        bot.reply_to(callback.message.reply_to_message, 'Бедет рандомный ответ')
    elif callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'getObject':
        print(callback)

bot.polling(none_stop=True)