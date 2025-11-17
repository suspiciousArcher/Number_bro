import random
import telebot
import requests
import os
from dotenv import load_dotenv
from telebot import types


import src.ConnectDB as CDB
import src.Translate as T


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    db_connect = CDB.ConnectDb()

    sql = '''INSERT INTO users (login, user_id) VALUES ('%s', '%s')''' % (
        message.from_user.first_name, message.from_user.id)
    otvet = db_connect.registration(sql, message.from_user.id)
    bot.send_message(message.chat.id, otvet)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Приветсвую, кожанный друг 👋\n'
                                      'Я могу рассказать множество интересных фактов о разных числах.\n'
                                      'Это мое основное занятие, но я развиваюсь😁' 'Возможно в скором временя буду умень намного больше🤗😤 '
                                      'На данный момент ты можешь использовать:\n'
                                      '/fakt - для того что бы узнать факт о числе\n'
                                      '/feedback - используй что бы высказать свое мнение обо мне, принимаются предложения\n'
                                      'ну ииии все...')


@bot.message_handler(commands=['fakt'])
def fakt(message):
    bot.send_message(message.chat.id, 'Скажи мне число о котором ты хотел бы узнать побольше...')
    bot.register_next_step_handler(message, fakt_step_two)


def fakt_step_two(message):
    chek = security(message.text)
    if chek:
        markup_inLine = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton('Математический', callback_data='math')
        button_2 = types.InlineKeyboardButton('Жизненный', callback_data='trivia')
        button_3 = types.InlineKeyboardButton('О годе', callback_data='year')
        markup_inLine.row(button_1)
        markup_inLine.row(button_2, button_3)
        bot.reply_to(message, 'Какого рода факт о числе тебя интересует? \n🧐🧐🧐🧐🧐', reply_markup=markup_inLine)
    else:
        bot.send_message(message.chat.id, 'Это выглядит не как число❗️❗️❗️️')


@bot.message_handler(commands=['feedback'])
def feedback(message):
    img = open('imag/partners-in-crime-spongebob.gif', 'rb')
    bot.send_video(message.chat.id, img,
                   caption='Выскажите свое мнение, постараюсь его учитывать 🫡'
                           'Нипишите его сообщением и оптравьте⤵️')
    img.close()
    bot.register_next_step_handler(message, feedback_message)


def feedback_message(message):
    markup_inLine = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton('Отправить отзыв', callback_data='set_feedback')
    button_2 = types.InlineKeyboardButton('Подумать еще', callback_data='put_aside_feedback')
    markup_inLine.row(button_1, button_2)
    bot.reply_to(message, 'Я благодарен за ваши отзывы. Как положительные так и отрицательные 🤜🏻🫷🏻 ',
                 reply_markup=markup_inLine)


#
# @bot.message_handler(commands=['json'])
# def json(message):
#     print(message)

@bot.message_handler(
    content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'voice', 'location', 'contact',
                   'animation'])
def not_understand(message):
    db_connect = CDB.ConnectDb()

    id_img = str(random.randint(1, 12))
    arr_text = db_connect.get_db('SELECT otvet FROM not_understand')
    id_text = random.randint(1, len(arr_text))
    text = arr_text[id_text - 1][0]
    img = open(f'imag/{id_img}.gif', 'rb')
    bot.send_video(message.chat.id, img,
                   caption=f'{text}\n' 'Попробуйте /help.')


@bot.callback_query_handler(func=lambda callback: True)
def otvet(callback):
    if callback.data == 'math':
        control_callbak(callback.message.chat.id, callback.message.reply_to_message.text, 'math')
    elif callback.data == 'trivia':
        control_callbak(callback.message.chat.id, callback.message.reply_to_message.text, 'trivia')
    elif callback.data == 'year':
        control_callbak(callback.message.chat.id, callback.message.reply_to_message.text, 'year')
    elif callback.data == 'set_feedback':
        db_connect = CDB.ConnectDb()

        set = '''INSERT INTO feedback(feedback) VALUES ('%s')''' % (callback.message.reply_to_message.text)
        db_connect.set_db(set)
        user_id = callback.from_user.id
        get = '''SELECT id FROM users WHERE user_id = %s''' % (user_id)
        id_user = db_connect.get_db(get)
        get = '''SELECT id FROM feedback WHERE feedback = '%s' ''' % (callback.message.reply_to_message.text)
        id_feedback = db_connect.get_db(get)
        set = 'INSERT INTO users_feedback(id_users, id_feedback) VALUES (%s, %s)' % (id_user[0][0], id_feedback[0][0])
        db_connect.set_db(set)
        bot.send_message(callback.message.chat.id, 'Принято‼️')
    elif callback.data == 'put_aside_feedback':
        bot.send_message(callback.message.chat.id, 'Если что надуете пишите...')


def control_callbak(chat_id, chislo, type):
    translate = T.Translate()
    db_connect = CDB.ConnectDb()

    number = chislo
    type = type
    API = f'http://numbersapi.com/{number}/{type}'
    fakt = requests.get(API).text
    get = '''SELECT id FROM chislo WHERE chislo = "%s"''' % (number)
    chek_chislo = db_connect.get_db(get)
    if len(chek_chislo) == 0:
        set = '''INSERT INTO chislo(chislo) VALUES ('%s')''' % (number)
        db_connect.set_db(set)
        chek_chislo = db_connect.get_db(get)
        id_chislo = chek_chislo[0][0]
        result = translate.translate(fakt)
        bot.send_message(chat_id, result)
        set = '''INSERT INTO fakt(fakt, translate, type) VALUES ('%s', '%s', '%s')''' % (fakt, result, type)
        db_connect.set_db(set)
        get = '''SELECT id FROM fakt WHERE type = "%s" AND fakt = '%s' ''' % (type, fakt)
        chek_fakt = db_connect.get_db(get)
        id_fakt = chek_fakt[0][0]
        set = '''INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ('%s', '%s')''' % (id_chislo, id_fakt)
        db_connect.set_db(set)
    elif len(chek_chislo) == 1:
        id_chislo = chek_chislo[0][0]
        get = '''SELECT id_chislo, id_fakt FROM chislo_fakt WHERE id_chislo = '%s' ''' % (id_chislo)
        chek_fakt = db_connect.get_db(get)
        cikl = len(chek_fakt) - 1
        str_id_fakt = ''
        for i in chek_fakt:
            if cikl > 0:
                str_id_fakt = str_id_fakt + str(i[1]) + ','
                cikl -= 1
            else:
                str_id_fakt = str_id_fakt + str(i[1])
        get = '''SELECT * FROM fakt WHERE id IN (%s) AND type = '%s' ''' % (str_id_fakt, type)
        chek_fakt = db_connect.get_db(get)
        famous_fakt = False
        translate_fakt = None
        id_fakt = None
        for i in chek_fakt:
            if fakt == i[1]:
                famous_fakt = True
                id_fakt = i[0]
                if i[2] is not None:
                    translate_fakt = i[2]
                break
        if famous_fakt:
            if translate_fakt is not None:
                bot.send_message(chat_id, translate_fakt)
            else:
                result = translate.translate(fakt)
                bot.send_message(chat_id, result)
                set = '''UPDATE fakt SET translate = "%s" WHERE id = '%s' ''' % (result, id_fakt)
                db_connect.set_db(set)
        else:
            result = translate.translate(fakt)
            bot.send_message(chat_id, result)
            set = '''INSERT INTO fakt(fakt, translate, type) VALUES ('%s', '%s', '%s')''' % (fakt, result, type)
            db_connect.set_db(set)
            get = '''SELECT id FROM fakt WHERE type = '%s' AND fakt = '%s' ''' % (type, fakt)
            chek_fakt = db_connect.get_db(get)
            id_fakt = chek_fakt[0][0]
            set = '''INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ('%s', '%s')''' % (id_chislo, id_fakt)
            db_connect.set_db(set)


def security(text):
    mes = str(text).replace(' ', '')
    security_arr = str((0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    security = None
    for i in mes:
        if i in security_arr:
            security = True
        else:
            security = False
            break
    return security


bot.polling(none_stop=True)
