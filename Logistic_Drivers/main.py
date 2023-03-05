import sqlite3
import telebot
from telebot import types
from random import randint

bot = telebot.TeleBot('5740151753:AAFmWSt25dO5p_I_MNOdXEc3lJ5_0Ki_IlQ')


# =====================================CREATE_DATA_BASE===================================================

db = sqlite3.connect('Drivers.db',  check_same_thread=False)
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS drivers (
   unit TEXT,
   name TEXT,
   phone TEXT,
   available INT
)""")

db.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
   user INT,
   name TEXT
)""")

db.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS adminUsers (
   user INT,
   name TEXT
)""")

db.commit()

# =====================================FIRST_STEP===================================================

@bot.message_handler(commands=['start', 'help'])
def start(message):
   bot.send_message(message.chat.id, f'{message.from_user.first_name}')
   if checkUser(message):
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
      NewDriver = types.KeyboardButton('/NewDriver')
      DeleteDriver = types.KeyboardButton('/DeleteDriver')
      ActivateDriver = types.KeyboardButton('/ActivateDriver')
      DisActivateDriver = types.KeyboardButton('/DisActivateDriver')
      RingListing = types.KeyboardButton('/RingListing')
      Phones = types.KeyboardButton('/Phones')
      markup.add(NewDriver, DeleteDriver, ActivateDriver, DisActivateDriver, RingListing, Phones)
      bot.send_message(message.chat.id, f'Натисніть кнопку', reply_markup=markup)


# =====================================NEW_DRIVER===================================================

unit = 0
phone = ''
name = ''
   
@bot.message_handler(commands=['NewDriver'])
def NewDriver(message):
   if checkAdminUser(message):
      bot.send_message(message.chat.id, 'Введите номер юнита')
      bot.register_next_step_handler(message, get_unit)


def get_unit(message):
   global unit
   unit = message.text
   cursor.execute(f'SELECT name FROM drivers WHERE unit = "{unit}"')
   if cursor.fetchone() is None:
      bot.send_message(message.chat.id,'Введите номер телефона')
      bot.register_next_step_handler(message, get_phone)
   else:
      bot.send_message(message.chat.id, 'Такой юнит уже существует!')

def get_phone(message):
   global phone
   phone = message.text
   bot.send_message(message.chat.id,"Введите имя водителя")
   bot.register_next_step_handler(message, get_name)

def get_name(message):
   global name 
   name = message.text
   new_record(message)

def new_record(message):
   cursor.execute('INSERT INTO drivers VALUES(?,?,?,?)', (unit, name, phone, 1))
   db.commit()
   bot.send_message(message.chat.id,"Юнит успешно добавлен")


# =====================================PHONE===================================================

@bot.message_handler(commands=['Phones'])
def Phones(message):
   if checkUser(message):
      bot.send_message(message.chat.id, 'Номер юнита')
      bot.register_next_step_handler(message, give_phone)

def give_phone(message):
   unit = message.text
   cursor.execute(f'SELECT phone,name from drivers WHERE unit = "{unit}"')
   if cursor.fetchone() is None:
      bot.send_message(message.chat.id, f"Такого юнита не существует")
   else:
      cursor.execute(f'SELECT phone,name from drivers WHERE unit = "{unit}"')
      for i in cursor:
         bot.send_message(message.chat.id, f"{i[0]}\n{i[1]}")

# =====================================DELETE_DRIVER===================================================

@bot.message_handler(commands=['DeleteDriver'])
def delete(message):
   if checkAdminUser(message):
      bot.send_message(message.chat.id, 'Ввдеите номер юнита которого хотите удалить')
      bot.register_next_step_handler(message, deleteDriver)

def deleteDriver(message):
   unit = message.text
   cursor.execute(f'SELECT name from drivers WHERE unit = "{unit}"')
   if cursor.fetchone() is None:
      bot.send_message(message.chat.id, 'Такого водителя не существует!')
   else:
      cursor.execute(f'DELETE from drivers WHERE unit = "{unit}"')
      db.commit()
      bot.send_message(message.chat.id, 'Юнит удален успешно')


# =====================================MAILING_LIST===================================================

@bot.message_handler(commands=['RingListing'])
def mailing(message):
   if checkUser(message):
      cursor.execute(f'SELECT phone FROM drivers WHERE available = "{1}"')
      if cursor.fetchone() is None:
         bot.send_message(message.chat.id, 'Ошибка запроса!')
      else:
         cursor.execute(f'SELECT phone FROM drivers WHERE available = "{1}"')
         List = []
         for i in cursor:
            List.append(i[0])
         maxNum = 49
         k = len(List) / maxNum
         k = int(k)
         if k*maxNum<len(List):
            k+=1
         for o in range(k):
            mess = ''
            for i in range(maxNum):
               if o*maxNum+i < len(List):
                  if mess != '':
                     mess = mess + ',' + List[o*maxNum+i]
                  else:
                     mess = mess + List[o*maxNum+i]
            bot.send_message(message.chat.id, f'{mess}\n')


# =====================================ActivateDriver===================================================

@bot.message_handler(commands=['ActivateDriver'])
def startAvailble(message):
   if checkUser(message):
      bot.send_message(message.chat.id, "Введите номер юнита которого хотите включить в рассылку")
      bot.register_next_step_handler(message, availble)

def availble(message):
   unit = message.text
   cursor.execute(f'SELECT name FROM drivers WHERE unit = "{unit}"')
   if cursor.fetchone():
      cursor.execute(f'UPDATE drivers SET available = 1 WHERE unit = "{unit}"')
      db.commit()
      bot.send_message(message.chat.id, 'Водитель успешно ВКЛЮЧЕН')
   else: 
      bot.send_message(message.chat.id, 'Такого юнита не существует!')


# =====================================DisActivateDriver===================================================

@bot.message_handler(commands=['DisActivateDriver'])
def startDisAvailble(message):
   if checkUser(message):
      bot.send_message(message.chat.id, "Введите номер юнита которого хотите выключить из рассылки")
      bot.register_next_step_handler(message, disAvailble)

def disAvailble(message):
   unit = message.text
   cursor.execute(f'SELECT name FROM drivers WHERE unit = "{unit}"')
   if cursor.fetchone() is None:
      bot.send_message(message.chat.id, 'Такого юнита не существует!')
   else: 
      cursor.execute(f'UPDATE drivers SET available = 0 WHERE unit = "{unit}"')
      db.commit()
      bot.send_message(message.chat.id, 'Водитель успешно ВЫКЛЮЧЕН')

# =====================================Check===================================================

@bot.message_handler(commands=['AdminButton'])
def ChecingMy(message):
   cursor.execute(f'DELETE FROM AdminUsers WHERE user = "{message.chat.id}"')


# =====================================LoginUser===================================================

def checkUser(message):
   userId = message.chat.id
   cursor.execute(f'SELECT * FROM users WHERE user = "{userId}"')
   if cursor.fetchone() is None:
      bot.send_message(message.chat.id, 'Вы не зарегестрированы!\nВведите пароль!')
      bot.register_next_step_handler(message, reg)
      return False
   else:
      return True

def checkAdminUser(message):
   userId = message.chat.id
   cursor.execute(f'SELECT * FROM adminUsers WHERE user = "{userId}"')
   if cursor.fetchone() is None:
      bot.send_message(message.chat.id, 'Вы не являетесь администратором!')
      return False
   else:
      return True

def reg(message):
   password = message.text
   if password == 'FordMustang':
      cursor.execute(f'INSERT INTO users (user, name) VALUES({message.chat.id}, "{message.from_user.first_name}")')
      db.commit()
      bot.send_message(message.chat.id,"Вы успешно зарегистрированы как пользователь")
   elif password == 'PorscheCayenne':
      cursor.execute(f'INSERT INTO adminUsers (user, name) VALUES({message.chat.id}, "{message.from_user.first_name}")')
      db.commit()
      cursor.execute(f'INSERT INTO users (user, name) VALUES({message.chat.id}, "{message.from_user.first_name}")')
      db.commit()
      bot.send_message(message.chat.id,"Вы успешно зарегистрированы как администратор")
   else:
      bot.send_message(message.chat.id,"Пароль введен не верно!")

@bot.message_handler(commands=['getAdmin'])
def getAdminStart(message):
   bot.send_message(message.chat.id, "Введите пароль для администратора!")
   bot.register_next_step_handler(message, getAdmin)

def getAdmin(message):
   password = message.text
   if password == 'PorscheCayenne':
      cursor.execute(f'INSERT INTO adminUsers (user, name) VALUES({message.chat.id}, "{message.from_user.first_name}")')
      db.commit()
      bot.send_message(message.chat.id,"Вы успешно зарегистрированы")
   else:
      bot.send_message(message.chat.id,"Пароль введен не верно!")

# =====================================End===================================================

bot.polling(none_stop=True)