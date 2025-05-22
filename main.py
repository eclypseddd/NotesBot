import telebot
from config import tg_TOKEN
from telebot import types
import time
import json

TOKEN = tg_TOKEN

bot = telebot.TeleBot(TOKEN)

with open('DataBase.json', encoding='utf8') as file:
    try:
        data_base = json.loads(file.read())
        print(data_base)
    except:
        data_base = dict()

def save_changes(dict):
    try:
        with open('DataBase.json','w',encoding='utf8') as file:
            json.dump(dict,file,indent=4)
    except:
        pass


def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add('Создать')
    markup.add('Редактировать')
    markup.add('Посмотреть')
    markup.add('Удалить')
    return markup


@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        chat_id = message.chat.id
        if chat_id not in data_base:
            data_base[chat_id] = dict()
            save_changes()
        bot.send_message(message.chat.id,'Привет, здесь ты можешь вести свои заметки',reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, 'Ошибка')

@bot.message_handler(func=lambda msg:msg.text == 'Вернуться в главное меню')
def return_to_main_menu(message):
    try:
        bot.send_message(message.chat.id,'Возвращаемся в главное меню',reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, 'Ошибка')

@bot.message_handler(func=lambda msg:msg.text=='Создать')
def create_message(message):
    try:
        chat_id = message.chat.id
        msg = bot.send_message(message.chat.id, 'Дай название своей заметке',reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg,create_message_2,chat_id)
        time.sleep(2)
    except:
        bot.send_message(message.chat.id, 'Ошибка')
def create_message_2(message,chat_id):
    try:
        name = message.text
        if name in data_base[chat_id]:
            msg = bot.send_message(message.chat.id, 'У тебя уже есть заметка с таким именем, введи другое имя')
            bot.register_next_step_handler(msg, create_message_2,chat_id)
        else:
            msg = bot.send_message(message.chat.id, 'Напиши содержание своей заметки')
            bot.register_next_step_handler(msg,create_message_3,name,chat_id)
    except:
        bot.send_message(message.chat.id, 'Ошибка')
def create_message_3(message,name,chat_id):
    note = message.text
    date = time.localtime()
    date = f'{('0' + str(date.tm_mday)) if date.tm_mday < 10 else date.tm_mday}.{('0' + str(date.tm_mon)) if date.tm_mon < 10 else date.tm_mon}.{date.tm_year}'
    data_base[chat_id][name] = [note,date]
    save_changes(data_base)
    bot.send_message(message.chat.id, 'Заметка успешно создана',reply_markup=main_menu())
@bot.message_handler(func=lambda msg:msg.text=='Удалить')
def delete_message(message):
    try:
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for note in data_base[chat_id]:
            markup.add(f'Удалить {note}')
        markup.add('Вернуться в главное меню')
        bot.send_message(chat_id, 'Выбери заметку для удаления', reply_markup=markup)
    except:
        bot.send_message(message.chat.id, 'Ошибка')

@bot.message_handler(func=lambda msg:msg.text[8:] in data_base[msg.chat.id].keys())
def delete_message_2(message):
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(types.InlineKeyboardButton('Да', callback_data='Yes'),types.InlineKeyboardButton('Нет', callback_data='No'))
        bot.send_message(message.chat.id,f'Ты уверен(а) что хочешь удалить заметку {message.text}?',reply_markup=markup)
    except:
        bot.send_message(message.chat.id, 'Ошибка')

@bot.callback_query_handler(func=lambda call:True)
def delete(call):
    try:
        note = call.message.text[48:-1]
        if call.data == 'Yes':
            del data_base[call.message.chat.id][note]
            save_changes(data_base)
            markup = types.ReplyKeyboardMarkup(row_width=1)
            for note in data_base[call.message.chat.id]:
                markup.add(f'Удалить {note}')
            markup.add('Вернуться в главное меню')
            bot.send_message(call.message.chat.id,f'Заметка {note} удалена',reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, f'Отмена удаления')
    except:
        bot.send_message(call.message.chat.id, 'Ошибка')


@bot.message_handler(func=lambda msg:msg.text=='Посмотреть')
def check_message(message):
    try:
        chat_id = message.chat.id
        if chat_id not in data_base:
            data_base[chat_id] = dict()
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for note in data_base[chat_id]:
            markup.add(f'Посмотреть {note}')
        markup.add('Вернуться в главное меню')
        bot.send_message(message.chat.id, 'Выбери заметку для просмотра',reply_markup=markup)
    except:
        bot.send_message(message.chat.id, 'Ошибка')

@bot.message_handler(func=lambda msg:msg.text[11:] in data_base[msg.chat.id].keys())
def check_message_2(message):
    try:
        note = message.text[11:]
        bot.send_message(message.chat.id,f'''Содержание заметки {note}:
    \n{data_base[message.chat.id][note][0]}
    \n{data_base[message.chat.id][note][1]}''')
    except:
        bot.send_message(message.chat.id, 'Ошибка')


@bot.message_handler(func=lambda msg:msg.text=='Редактировать')
def edit_message(message):
    try:
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for note in data_base[message.chat.id]:
            markup.add(f'Редактировать {note}')
        markup.add('Вернуться в главное меню')
        bot.send_message(message.chat.id,'Выбери заметку для редактирования',reply_markup=markup)
    except:
        bot.send_message(message.chat.id, 'Ошибка')

@bot.message_handler(func=lambda msg:msg.text[14:] in data_base[msg.chat.id].keys())
def edit_message_2(message):
    try:
        note = message.text[14:]
        chat_id = message.chat.id
        msg = bot.send_message(chat_id,'Введите новое содержание заметки')
        bot.register_next_step_handler(msg,edit_message_3,chat_id,note)
    except:
        bot.send_message(message.chat.id, 'Ошибка')
def edit_message_3(message,chat_id,note):
    try:
        data_base[chat_id][note][0] = message.text
        save_changes(data_base)
        bot.send_message(chat_id,f'Заметка {note} успешно отредактирована')
    except:
        bot.send_message(message.chat.id, 'Ошибка')

if __name__ == '__main__':
    bot.polling()