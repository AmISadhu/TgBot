import telebot
import os
from dotenv import load_dotenv
from telebot import types

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token=BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Я ваш помощник в выборе рецептов. Как мне к вам обращаться?')
    bot.register_next_step_handler(message, hello)


def hello(message):
    bot.send_message(message.chat.id, f'Приятно познакомиться, {message.text}! Рад вас видеть!')
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
        btn3 = types.InlineKeyboardButton('Супы', callback_data='soup')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Что будем готовить?', reply_markup=markup)
    elif message.text == 'Список покупок':
        ...
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
        btn3 = types.KeyboardButton('Вернуться в главное меню')
        markup.row(btn1, btn2)
        markup.add(btn3)
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
        btn1 = types.KeyboardButton('Ингредиенты')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, back)
        bot.send_message(message.chat.id, 'Продолжить просмотр?', reply_markup=markup)
    elif message.text == 'Ингредиенты':
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
    elif callback.data == 'soup':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Сырный суп-пюре')
        btn2 = types.KeyboardButton('Грибной суп-пюре')
        back = types.KeyboardButton('Вернуться в главное меню')
        markup.add(btn1, btn2, back)
        bot.send_message(callback.message.chat.id, 'Какой салат хотите сделать?', reply_markup=markup)
    else:
        bot.send_message(callback.message.chat.id, 'На такую команду  не запрограммирован(')


bot.polling(none_stop=True)
