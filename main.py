import telebot
from telebot import types
import requests
import src.ConnectDB as CDB
import src.Translate as T

bot = telebot.TeleBot('6354469033:AAF-ARfr9km4-GJRr011Gi7iv30BNXm0W68')


@bot.message_handler(commands=['start'])
def start(message):
    db_connect = CDB.ConnectDb()

    sql = 'INSERT INTO users (login, user_id) VALUES ("%s", "%s")' % (
    message.from_user.first_name, message.from_user.id)
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
        db_connect = CDB.ConnectDb()

        number = callback.message.reply_to_message.text
        type = 'math'
        API = f'http://numbersapi.com/{number}/{type}'
        fakt = requests.get(API).text
        get = 'SELECT id FROM chislo WHERE chislo = "%s"' % (number)
        chek_chislo = db_connect.get_db(get)
        # print(len(chek_chislo))

        if len(chek_chislo) == 0:
            set = 'INSERT INTO chislo(chislo) VALUES ("%s")' % (number)
            db_connect.set_db(set)
            chek_chislo = db_connect.get_db(get)
            id_chislo = chek_chislo[0][0]
            result = translate.translate(fakt)
            bot.send_message(callback.message.chat.id, result)
            set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
            db_connect.set_db(set)
            get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
            chek_fakt = db_connect.get_db(get)
            id_fakt = chek_fakt[0][0]
            set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
            db_connect.set_db(set)

        elif len(chek_chislo) == 1:
            id_chislo = chek_chislo[0][0]
            get = 'SELECT id_chislo, id_fakt FROM chislo_fakt WHERE id_chislo = "%s"' % (id_chislo)
            chek_fakt = db_connect.get_db(get)

            # print('Получем список свзей числа с фактами: ')
            # print(chek_fakt)
            # print(len(chek_fakt))

            cikl = len(chek_fakt) - 1

            # print('Сколько поставить запятых: ')
            # print(cikl)

            str_id_fakt = ''
            for i in chek_fakt:
                if cikl > 0:
                    str_id_fakt = str_id_fakt + str(i[1]) + ','
                    cikl -= 1
                else:
                    str_id_fakt = str_id_fakt + str(i[1])

            # print('Список id фактов: ')
            # print(str_id_fakt)

            get = 'SELECT * FROM fakt WHERE id IN (%s) AND type = "%s"' % (str_id_fakt, type)

            # print(get)

            chek_fakt = db_connect.get_db(get)

            # print('Список фактов: ')
            # print(chek_fakt)

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

            # print('Результат цикла: ')
            # print(famous_fakt, translate_fakt, id_fakt)

            if famous_fakt:
                if translate_fakt is not None:
                    # print('Факт известен и есть перевод: ')
                    # print(translate_fakt)

                    bot.send_message(callback.message.chat.id, translate_fakt)
                else:
                    # print('Факт известен но нет перевода, отправка на перевод')

                    result = translate.translate(fakt)
                    bot.send_message(callback.message.chat.id, result)
                    set = 'UPDATE fakt SET translate = "%s" WHERE id = "%s" ' % (result, id_fakt)
                    db_connect.set_db(set)

            else:
                # print('Факт не известен')

                result = translate.translate(fakt)
                bot.send_message(callback.message.chat.id, result)
                set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
                db_connect.set_db(set)
                get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
                chek_fakt = db_connect.get_db(get)
                id_fakt = chek_fakt[0][0]
                set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
                db_connect.set_db(set)



    elif callback.data == 'trivia':
        translate = T.Translate()
        db_connect = CDB.ConnectDb()

        number = callback.message.reply_to_message.text
        type = 'trivia'
        API = f'http://numbersapi.com/{number}/{type}'
        fakt = requests.get(API).text
        get = 'SELECT id FROM chislo WHERE chislo = "%s"' % (number)
        chek_chislo = db_connect.get_db(get)
        # print(len(chek_chislo))
        if len(chek_chislo) == 0:
            set = 'INSERT INTO chislo(chislo) VALUES ("%s")' % (number)
            db_connect.set_db(set)
            chek_chislo = db_connect.get_db(get)
            id_chislo = chek_chislo[0][0]
            result = translate.translate(fakt)
            bot.send_message(callback.message.chat.id, result)
            set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
            db_connect.set_db(set)
            get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
            chek_fakt = db_connect.get_db(get)
            id_fakt = chek_fakt[0][0]
            set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
            db_connect.set_db(set)
        elif len(chek_chislo) == 1:
            id_chislo = chek_chislo[0][0]
            get = 'SELECT id_chislo, id_fakt FROM chislo_fakt WHERE id_chislo = "%s"' % (id_chislo)
            chek_fakt = db_connect.get_db(get)
            # print(chek_fakt)
            cikl = len(chek_fakt) - 1
            str_id_fakt = ''
            for i in chek_fakt:
                if cikl > 0:
                    str_id_fakt = str_id_fakt + str(i[1]) + ','
                    cikl -= 1
                else:
                    str_id_fakt = str_id_fakt + str(i[1])
            # print(str_id_fakt)
            get = 'SELECT * FROM fakt WHERE id IN (%s) AND type = "%s"' % (str_id_fakt, type)
            chek_fakt = db_connect.get_db(get)
            # print(chek_fakt)
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
                    bot.send_message(callback.message.chat.id, translate_fakt)
                else:
                    result = translate.translate(fakt)
                    bot.send_message(callback.message.chat.id, result)
                    set = 'UPDATE fakt SET translate = "%s" WHERE id = "%s" ' % (result, id_fakt)
                    db_connect.set_db(set)

            else:
                result = translate.translate(fakt)
                bot.send_message(callback.message.chat.id, result)
                set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
                db_connect.set_db(set)
                get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
                chek_fakt = db_connect.get_db(get)
                id_fakt = chek_fakt[0][0]
                set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
                db_connect.set_db(set)

    elif callback.data == 'year':
        translate = T.Translate()
        db_connect = CDB.ConnectDb()

        number = callback.message.reply_to_message.text
        type = 'year'
        API = f'http://numbersapi.com/{number}/{type}'
        fakt = requests.get(API).text
        get = 'SELECT id FROM chislo WHERE chislo = "%s"' % (number)
        chek_chislo = db_connect.get_db(get)
        # print(len(chek_chislo))
        if len(chek_chislo) == 0:
            set = 'INSERT INTO chislo(chislo) VALUES ("%s")' % (number)
            db_connect.set_db(set)
            chek_chislo = db_connect.get_db(get)
            id_chislo = chek_chislo[0][0]
            result = translate.translate(fakt)
            bot.send_message(callback.message.chat.id, result)
            set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
            db_connect.set_db(set)
            get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
            chek_fakt = db_connect.get_db(get)
            id_fakt = chek_fakt[0][0]
            set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
            db_connect.set_db(set)
        elif len(chek_chislo) == 1:
            id_chislo = chek_chislo[0][0]
            get = 'SELECT id_chislo, id_fakt FROM chislo_fakt WHERE id_chislo = "%s"' % (id_chislo)
            chek_fakt = db_connect.get_db(get)
            # print(chek_fakt)
            cikl = len(chek_fakt) - 1
            str_id_fakt = ''
            for i in chek_fakt:
                if cikl > 0:
                    str_id_fakt = str_id_fakt + str(i[1]) + ','
                    cikl -= 1
                else:
                    str_id_fakt = str_id_fakt + str(i[1])
            # print(str_id_fakt)
            get = 'SELECT * FROM fakt WHERE id IN (%s) AND type = "%s"' % (str_id_fakt, type)
            chek_fakt = db_connect.get_db(get)
            # print(chek_fakt)
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
                    bot.send_message(callback.message.chat.id, translate_fakt)
                else:
                    result = translate.translate(fakt)
                    bot.send_message(callback.message.chat.id, result)
                    set = 'UPDATE fakt SET translate = "%s" WHERE id = "%s" ' % (result, id_fakt)
                    db_connect.set_db(set)

            else:
                result = translate.translate(fakt)
                bot.send_message(callback.message.chat.id, result)
                set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
                db_connect.set_db(set)
                get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
                chek_fakt = db_connect.get_db(get)
                id_fakt = chek_fakt[0][0]
                set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
                db_connect.set_db(set)


def control_callbak(chat_id, chislo, type):
    translate = T.Translate()
    db_connect = CDB.ConnectDb()

    number = chislo
    type = type
    API = f'http://numbersapi.com/{number}/{type}'
    fakt = requests.get(API).text
    get = 'SELECT id FROM chislo WHERE chislo = "%s"' % (number)
    chek_chislo = db_connect.get_db(get)
    # print(len(chek_chislo))

    if len(chek_chislo) == 0:
        set = 'INSERT INTO chislo(chislo) VALUES ("%s")' % (number)
        db_connect.set_db(set)
        chek_chislo = db_connect.get_db(get)
        id_chislo = chek_chislo[0][0]
        result = translate.translate(fakt)
        bot.send_message(chat_id, result)
        set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
        db_connect.set_db(set)
        get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
        chek_fakt = db_connect.get_db(get)
        id_fakt = chek_fakt[0][0]
        set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
        db_connect.set_db(set)

    elif len(chek_chislo) == 1:
        id_chislo = chek_chislo[0][0]
        get = 'SELECT id_chislo, id_fakt FROM chislo_fakt WHERE id_chislo = "%s"' % (id_chislo)
        chek_fakt = db_connect.get_db(get)

        # print('Получем список свзей числа с фактами: ')
        # print(chek_fakt)
        # print(len(chek_fakt))

        cikl = len(chek_fakt) - 1

        # print('Сколько поставить запятых: ')
        # print(cikl)

        str_id_fakt = ''
        for i in chek_fakt:
            if cikl > 0:
                str_id_fakt = str_id_fakt + str(i[1]) + ','
                cikl -= 1
            else:
                str_id_fakt = str_id_fakt + str(i[1])

        # print('Список id фактов: ')
        # print(str_id_fakt)

        get = 'SELECT * FROM fakt WHERE id IN (%s) AND type = "%s"' % (str_id_fakt, type)

        # print(get)

        chek_fakt = db_connect.get_db(get)

        # print('Список фактов: ')
        # print(chek_fakt)

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

        # print('Результат цикла: ')
        # print(famous_fakt, translate_fakt, id_fakt)

        if famous_fakt:
            if translate_fakt is not None:
                # print('Факт известен и есть перевод: ')
                # print(translate_fakt)

                bot.send_message(chat_id, translate_fakt)
            else:
                # print('Факт известен но нет перевода, отправка на перевод')

                result = translate.translate(fakt)
                bot.send_message(chat_id, result)
                set = 'UPDATE fakt SET translate = "%s" WHERE id = "%s" ' % (result, id_fakt)
                db_connect.set_db(set)

        else:
            # print('Факт не известен')

            result = translate.translate(fakt)
            bot.send_message(chat_id, result)
            set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' % (fakt, result, type)
            db_connect.set_db(set)
            get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
            chek_fakt = db_connect.get_db(get)
            id_fakt = chek_fakt[0][0]
            set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
            db_connect.set_db(set)


bot.polling(none_stop=True)
