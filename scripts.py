import sqlite3
from mymemopy.translator import MyMemoryTranslate


class ConnectDb:

    def registration(self, sql, user_id):
        try:
            otvet = None
            zapros = ConnectDb()
            select = zapros.get_db('SELECT user_id FROM users')
            for i in range(len(select)):
                if user_id == select[i][0]:
                    otvet = 'Вы уже наш пользователь 🤝'
                    break
                else:
                    otvet = 'Вы зарегистрированны 🎉'

            if otvet == 'Вы уже наш пользователь 🤝':
                return otvet
            elif otvet == 'Вы зарегистрированны 🎉':
                connect = sqlite3.connect('data/data_bot.db')
                cursor = connect.cursor()

                cursor.execute(sql)
                connect.commit()
                cursor.close()
                connect.close()
                return otvet
        except:
            otvet = 'Не предвиденная ошибка 🤷 \nПопробуйте позже 🫠 '
            return otvet

    def get_db(self, sql):
        connect = sqlite3.connect('data/data_bot.db')
        cursor = connect.cursor()

        cursor.execute(sql)
        select = cursor.fetchall()
        cursor.close()
        connect.close()
        return select

    def test(self, user_id):
        connect = sqlite3.connect('data/data_bot.db')
        cursor = connect.cursor()

        cursor.execute('SELECT user_id FROM users')
        select = cursor.fetchall()
        otvet = None
        for i in range(len(select)):
            if user_id == select[i][0]:
                otvet = 'Вы уже наш пользователь 🤝'
                break
            else:
                otvet = 'Вы зарегистрированны 🎉'
        cursor.close()
        connect.close()
        return otvet


class Translate:

    def translate(self, text):
        translate = MyMemoryTranslate()
        res = translate.translate(text, source_lang='en', target_lang='ru')
        return res