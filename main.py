import telebot
from telebot import types
import requests
import src.ConnectDB as CDB
import src.Translate as T

bot = telebot.TeleBot('6354469033:AAF-ARfr9km4-GJRr011Gi7iv30BNXm0W68')

@bot.message_handler(commands=['start'])
def start(message):
    db_connect = CDB.ConnectDb()

    sql = 'INSERT INTO users (login, user_id) VALUES ("%s", "%s")' % (message.from_user.first_name, message.from_user.id)
    otvet = db_connect.registration(sql, message.from_user.id)
    bot.send_message(message.chat.id, otvet)


@bot.message_handler(commands=['fakt'])
def fakt(message):
    bot.send_message(message.chat.id, 'Скажи мне число о котором ты хотел бы узнать побольше...')
    bot.register_next_step_handler(message, fakt_step_two)

def fakt_step_two(message):
    markup_inLine = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton('Математический', callback_data='math')
    button_2 = types.InlineKeyboardButton('Жизненный', callback_data='trivia')
    button_3 = types.InlineKeyboardButton('О годе', callback_data='year')
    markup_inLine.row(button_1)
    markup_inLine.row(button_2, button_3)
    bot.reply_to(message, 'Какого рода факт о числе тебя интересует? \n🧐🧐🧐🧐🧐', reply_markup=markup_inLine)

@bot.message_handler(commands=['json'])
def json(message):
    print(message)

@bot.message_handler(commands=['clear'])
def clear_button(message):
    markup_reply = types.ReplyKeyboardMarkup()
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
    if callback.data == 'math':
        translate = T.Translate()
        number = callback.message.reply_to_message.text
        type = 'math'
        API = f'http://numbersapi.com/{number}/{type}'
        result = translate.translate(requests.get(API).text)
        bot.send_message(callback.message.chat.id, result)
    elif callback.data == 'trivia':
        translate = T.Translate()
        number = callback.message.reply_to_message.text
        type = 'trivia'
        API = f'http://numbersapi.com/{number}/{type}'
        result = translate.translate(requests.get(API).text)
        bot.send_message(callback.message.chat.id, result)
    elif callback.data == 'year':
        translate = T.Translate()
        number = callback.message.reply_to_message.text
        type = 'year'
        API = f'http://numbersapi.com/{number}/{type}'
        result = translate.translate(requests.get(API).text)
        bot.send_message(callback.message.chat.id, result)


bot.polling(none_stop=True)
