import telebot
import os
from dotenv import load_dotenv
from telebot import types
import sqlite3

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token=BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Я ваш помощник в выборе рецептов. Как мне к вам обращаться?')
    # bot.send_message(message.chat.id, message)

    bot.register_next_step_handler(message, hello)


def hello(message):
    # connect bd
    conn = sqlite3.connect('food_bot.sql')
    cur = conn.cursor()

    # create table (id, nickname)
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id integer primary key, nickname varchar(50))')
    conn.commit()

    person_id = message.from_user.id
    cur.execute(f"SELECT user_id FROM users WHERE user_id = {person_id}")
    data = cur.fetchone()
    if data is None:
        cur.execute(
            'INSERT INTO users(user_id, nickname) VALUES("%s", "%s")' % (
                message.from_user.id, message.from_user.username))
        conn.commit()
        bot.send_message(message.chat.id, f'Приятно познакомиться, {message.text}! Рад вас видеть!')
    else:
        bot.send_message(message.chat.id, f"Вы уже со мной работали, я вас запомнил, {message.text}!😊")

    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ('Рецепты', 'Список покупок', 'Заказать еду')
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Чем я могу вам помочь?', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main(message):
    if message.text == 'Рецепты':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Макароны', callback_data='pasta')
        btn2 = types.InlineKeyboardButton('Салаты', callback_data='salad')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Что будем готовить?', reply_markup=markup)

    elif message.text == 'Список покупок':
        conn = sqlite3.connect('food_bot.sql')
        cur = conn.cursor()
        try:
            # shopping_data = "\n".join(''.join(data).split(","))
            cur.execute('SELECT id, shopping_list FROM food')
            products = cur.fetchall()
            info = ''
            for el in products:
                # ''.join(el.replace(' ', ''))
                info += f'{el[0]}. {"".join(el[1].replace(" ", "")).title()}\n'
            markup = types.ReplyKeyboardMarkup()
            btn1 = types.KeyboardButton('Очистить список покупок')
            back = types.KeyboardButton('Вернуться в главное меню')
            markup.add(btn1, back)
            bot.send_message(message.chat.id, f'Вот ваш список покупок:\n{info}', reply_markup=markup)
        except sqlite3.OperationalError:
            markup = types.ReplyKeyboardMarkup()
            btn1 = types.KeyboardButton('Заполнить список покупок')
            back = types.KeyboardButton('Вернуться в главное меню')
            markup.row(btn1, back)
            bot.send_message(message.chat.id, "Ваш список покупок пуст, желаете заполнить его?",
                             reply_markup=markup)
        cur.close()
        conn.close()
    elif message.text == 'Заполнить список покупок':
        bot.send_message(message.chat.id, 'Вводите, пожалуйста, свои продукты через запятую')
        bot.register_next_step_handler(message, shop_list)
    elif message.text == 'Очистить список покупок':
        conn = sqlite3.connect('food_bot.sql')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS food")
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Заполнить список покупок')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.row(btn1, back)
        bot.send_message(message.chat.id, "Вы очистили список покупок, желаете заполнить его?",
                         reply_markup=markup)

    elif message.text == 'Заказать еду':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Пиццка', url='https://pzz.by/')
        btn2 = types.InlineKeyboardButton('Суси', url='https://godzilla.by/')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Что будете: пиццу или суши?', reply_markup=markup)

    elif message.text == 'Карбонара':
        photo = r'https://eda.ru/recepty/pasta-picca/pasta-karbonara-s-bekonom-pasta-carbonara-38721'.format(
            os.getcwd())
        bot.send_photo(message.chat.id, photo)
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Рецепт карбонары')
        btn2 = types.KeyboardButton('Ингредиенты')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.row(btn1, btn2)
        markup.add(back)
        bot.send_message(message.chat.id, 'Что выберем?', reply_markup=markup)
    elif message.text == 'Рецепт карбонары':
        bot.send_message(message.chat.id, '1.Нарежьте ломтиками бекон и обжарьте на сковородке.\n'
                                          '2.Поставьте закипать воду.\n'
                                          '3.Взбейте в отдельной емкости желтки и сливки, добавьте соль и \n'
                                          'перец и тертый пармезан.\n'
                                          '4.Добавьте в кипящую воду соль, оливковое масло и спагетти.\n'
                                          '5.Варите на 1 минуту меньше, чем указано в инструкции на упаковке \n'
                                          '(если вы сделали пасту сами — варка 2 минуты), \n'
                                          'варить нужно до состояния аль денте.\n'
                                          '6.В емкость с соусом добавьте бекон, пасту, перемешайте и \n'
                                          'выложите в тарелки, посыпьте сверху тертым пармезаном.\n')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Карбонара', url='https://eda.ru/recepty/pasta-karbonara')
        markup.add(btn1)
        bot.send_message(message.chat.id, 'Больше рецептов карбонары смотрите на сайте!',
                         reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Ингредиенты карбонары')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Ингредиенты карбонары':
        bot.send_message(message.chat.id, '1.Спагетти из твердых сортов пшеницы - 125 г.\n'
                                          '2.Сливки 20%-ные - 50 г.\n'
                                          '3.Бекон - 50 г.\n'
                                          '4.Яичный желток - 2 шт.\n'
                                          '5.Оливковое масло - 5 мл.(по вкусу)\n'
                                          '6.Тёртый сыр пармезан - 25 г.\n'
                                          'Ингредиенты рассчитаны на одну персону,\n'
                                          'если человек больше, то умножайте требуемые\n'
                                          'ингредиенты на кол-во персон.\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Рецепт карбонары')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Макароны с сыром':
        photo = r'https://eda.ru/recepty/osnovnye-blyuda/makarony-s-syrom-91462'.format(
            os.getcwd())
        bot.send_photo(message.chat.id, photo)
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Рецепт макарон с сыром')
        btn2 = types.KeyboardButton('Ингредиенты макарон с сыром')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.row(btn1, btn2)
        markup.add(back)
        bot.send_message(message.chat.id, 'Что выберем?', reply_markup=markup)
    elif message.text == 'Рецепт макарон с сыром':
        bot.send_message(message.chat.id, '1.Подогреть воду.\n'
                                          '2.Закинуть макароны.\n'
                                          '3.Натереть сыр. \n'
                                          '4.Слить воду.\n'
                                          '5.Добавить сыр и сливочное масло. \n')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Макароны с сыром', url='https://eda.ru/recepty/makaroni')
        markup.add(btn1)
        bot.send_message(message.chat.id, 'Больше рецептов макарон с сыром смотрите на сайте!',
                         reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Ингредиенты макарон с сыром')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Ингредиенты макарон с сыром':
        bot.send_message(message.chat.id, '1.Макароны - 80 г.\n'
                                          '2.Сыр - 25 г.\n'
                                          '3.Бекон - 50 г.\n'
                                          '4.Сливочное масло - 1 чайная ложка\n'
                                          '5.Соль - по вкусу\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Рецепт макарон с сыром')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Яичный салат':
        photo = r'https://eda.ru/recepty/salaty/jaichnij-salat-47456'.format(
            os.getcwd())
        bot.send_photo(message.chat.id, photo)
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Рецепт яичного салата')
        btn2 = types.KeyboardButton('Ингредиенты яичного салата')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.row(btn1, btn2)
        markup.add(back)
        bot.send_message(message.chat.id, 'Что выберем?', reply_markup=markup)
    elif message.text == 'Рецепт яичного салата':
        bot.send_message(message.chat.id, '1.Яйца сварить вкрутую, охладить, почистить, мелко нарубить.\n'
                                          '2. Мелко нарезать лук (только зеленую часть).\n'
                                          '3. Соединить лук и яйца, добавить майонез \n'
                                          '(можно приготовить самостоятельно), \n'
                                          'соль, перец, тщательно перемешать.\n')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Яичный салат', url='https://eda.ru/recepty/salaty/jaichnij-salat-47456')
        markup.add(btn1)
        bot.send_message(message.chat.id, 'Больше рецептов яичного салата смотрите на сайте!',
                         reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Ингредиенты яичного салата')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Ингредиенты яичного салата':
        bot.send_message(message.chat.id, '1.Куриное яйцо - 1,5 шт.\n'
                                          '2.Майонез - 1,5 чайные ложки\n'
                                          '3.Зелёный лук - по вкусу\n'
                                          '4.Молотый чёрный перец - по вкусу\n'
                                          '5.Соль - по вкусу\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Рецепт яичного салата')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Салат "Весенний"':
        photo = r'https://eda.ru/recepty/salaty/salat-vesenniy-1264281'.format(
            os.getcwd())
        bot.send_photo(message.chat.id, photo)
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Рецепт салата "Весенний"')
        btn2 = types.KeyboardButton('Ингредиенты салата "Весенний"')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.row(btn1, btn2)
        markup.add(back)
        bot.send_message(message.chat.id, 'Что выберем?', reply_markup=markup)
    elif message.text == 'Рецепт салата "Весенний"':
        bot.send_message(message.chat.id, '1.Яйца положить в кипящую воду и варить 11 минут.\n'
                                          'Затем переместить их в холодную воду, \n'
                                          'чтобы остановить приготовление и охладить.\n'
                                          '2. Огурцы и редис нарезать тонкими кольцами, \n'
                                          'яйца натереть на крупной терке, \n'
                                          'а зеленый лук и укроп мелко нарезать. \n'
                                          'Смешать все в большой чаше.\n'
                                          '3.Заправить салат сметаной, посолить и поперчить по вкусу.')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Салат "Весенний"', url='https://eda.ru/recepty/salaty/salat-vesenniy-126428')
        markup.add(btn1)
        bot.send_message(message.chat.id, 'Больше рецептов салата "Весенний" смотрите на сайте!',
                         reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Ингредиенты салата "Весенний"')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Ингредиенты салата "Весенний"':
        bot.send_message(message.chat.id, '1.Куриное яйцо - 1/2 шт.\n'
                                          '2.Редис - 34 г.\n'
                                          '3.Огурцы - 34 г.\n'
                                          '4.Зелёный лук - 4 г.\n'
                                          '5.Укроп - по вкусу\n'
                                          '6.Сметана - 1,5 чайные ложки\n'
                                          '7.Соль - по вкусу\n'
                                          '8.Молотый чёрный перец - по вкусу\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Рецепт салата "Весенний"')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)

    elif message.text == 'Вернуться в главное меню':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ('Рецепты', 'Список покупок', 'Заказать еду')
        markup.add(*buttons)
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.\nЧем я ещё могу вам помочь?',
                         reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ('Рецепты', 'Список покупок', 'Заказать еду')
        markup.add(*buttons)
        bot.send_message(message.chat.id, 'Я такого не умею\nВы вернулись в главное меню',
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'pasta':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Карбонара')
        btn2 = types.KeyboardButton('Макароны с сыром')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, btn2, back)
        bot.send_message(callback.message.chat.id, 'Какие макароны будем готовить?', reply_markup=markup)
    elif callback.data == 'salad':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Яичный салат')
        btn2 = types.KeyboardButton('Салат "Весенний"')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, btn2, back)
        bot.send_message(callback.message.chat.id, 'Какой салат хотите сделать?', reply_markup=markup)
    else:
        bot.send_message(callback.message.chat.id, 'На такую команду  не запрограммирован(')


def shop_list(message):
    conn = sqlite3.connect('food_bot.sql')
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS food (id integer primary key, shopping_list TEXT, users_id INTEGER, '
        'FOREIGN KEY (users_id) REFERENCES users(user_id))')
    conn.commit()
    for i in message.text.split(","):
        cur.execute(
            'INSERT INTO food(shopping_list,users_id) VALUES("%s","%s")' % (
                i, message.from_user.id
            )
        )
        # shopping_data = "\n".join(''.join(data).split(","))
        conn.commit()
    # bot.send_message(message.chat.id, message.text)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Список покупок')
    btn2 = types.KeyboardButton('Очистить список покупок')
    back = types.KeyboardButton('Вернуться в главное меню')
    markup.add(btn1)
    markup.row(btn2, back)
    bot.send_message(message.chat.id, 'Список покупок сохранён, хотите его посмотреть?',
                     reply_markup=markup)
    cur.close()
    conn.close()


bot.polling(none_stop=True)
