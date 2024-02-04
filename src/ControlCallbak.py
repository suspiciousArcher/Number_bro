import telebot
from telebot import types
import requests
import src.ConnectDB as CDB
import src.Translate as T

def otvet(callback):
    if callback.data == 'math':
        translate = T.Translate()
        db_connect = CDB.ConnectDb()

        number = callback.message.reply_to_message.text
        type = 'math'
        API = f'http://numbersapi.com/{number}/{type}'
        fakt = requests.get(API).text
        get = 'SELECT id FROM chislo WHERE chislo = "%s"' %(number)
        chek_chislo = db_connect.get_db(get)
        # print(len(chek_chislo))

        if len(chek_chislo) == 0:
            set = 'INSERT INTO chislo(chislo) VALUES ("%s")' %(number)
            db_connect.set_db(set)
            chek_chislo = db_connect.get_db(get)
            id_chislo = chek_chislo[0][0]
            result = translate.translate(fakt)
            bot.send_message(callback.message.chat.id, result)
            set = 'INSERT INTO fakt(fakt, translate, type) VALUES ("%s", "%s", "%s")' %(fakt, result, type)
            db_connect.set_db(set)
            get = 'SELECT id FROM fakt WHERE type = "%s" AND fakt = "%s"' % (type, fakt)
            chek_fakt = db_connect.get_db(get)
            id_fakt = chek_fakt[0][0]
            set = 'INSERT INTO chislo_fakt(id_chislo, id_fakt) VALUES ("%s", "%s")' % (id_chislo, id_fakt)
            db_connect.set_db(set)

        elif len(chek_chislo) == 1:
            id_chislo = chek_chislo[0][0]
            get = 'SELECT id_chislo, id_fakt FROM chislo_fakt WHERE id_chislo = "%s"' %(id_chislo)
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

            get = 'SELECT * FROM fakt WHERE id IN (%s) AND type = "%s"' %(str_id_fakt, type)

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
                    set = 'UPDATE fakt SET translate = "%s" WHERE id = "%s" ' %(result, id_fakt)
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