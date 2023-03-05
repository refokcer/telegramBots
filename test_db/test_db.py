import sqlite3
import telebot

bot = telebot.TeleBot('5740151753:AAFmWSt25dO5p_I_MNOdXEc3lJ5_0Ki_IlQ')

db = sqlite3.connect('server.db', check_same_thread=False)
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
   login TEXT,
   number INT
)""")


def log(message):
   user_login = message.chat.id
   cursor.execute('INSERT INTO users VALUES(?,?)', (user_login, 0))
   db.commit()
   bot.send_message(user_login, 'Вы успешно зарегестрированы')


def innumber(message):
   x = int(message.text)
   user_login = message.chat.id
   # cursor.execute(f'SELECT number FROM users WHERE login = "{user_login}"')
   cursor.execute(f'UPDATE users SET number = {x} WHERE login = "{user_login}"')
   db.commit()


@bot.message_handler(commands=['start'])
def start(message):
   user_login = message.chat.id
   cursor.execute(f'SELECT login FROM users WHERE login = "{user_login}"')
   if cursor.fetchone() is None:
      log(message)

   # cursor.execute(f'SELECT login FROM users WHERE login = "{user_login}"')
   # mess = bot.send_message(user_login, 'Введите свое  число')
   # bot.register_next_step_handler(mess, innumber)

bot.polling(non_stop= True)
# mess = bot.send_message(user_login, 'Вы еще не зарегестрированы.')
