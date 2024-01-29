select = [(665469135,), (810960485,), (810960487,), (810960485,)]
user_id = 810960487
otvet = None
for i in range(len(select)):
    print(i)

    if user_id == select[i][0]:
        otvet = 'Вы уже наш пользователь 🤝'
        break
    else:
        otvet = 'Вы зарегистрированны 🎉'

print(otvet)
