import vk_api
import telebot
from telebot import types


bot = telebot.TeleBot('5740151753:AAFmWSt25dO5p_I_MNOdXEc3lJ5_0Ki_IlQ')


# =====================================FIRST_STEP===================================================

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    listing = types.KeyboardButton('/Listing')
    markup.add(listing)
    bot.send_message(message.chat.id, f'Натисніть кнопку', reply_markup=markup)

# ===============================================================================================


token = ''
groupId = 0
textForListing = ''


@bot.message_handler(commands=['Listing'])
def Listing(message):
    bot.send_message(message.chat.id, 'Введите токен группы')
    bot.register_next_step_handler(message, get_token)


def get_token(message):
    global token
    token = message.text
    bot.send_message(message.chat.id, 'Введите Id группы')
    bot.register_next_step_handler(message, get_id)


def get_id(message):
    global groupId
    groupId = message.text
    bot.send_message(message.chat.id, "Введите текст для рассылки")
    bot.register_next_step_handler(message, get_text)


def get_text(message):
    global textForListing
    textForListing = message.text
    bot.send_message(message.chat.id, F" token: {token}\n\n Group Id: {groupId}\n\n Text: {textForListing}"
                                    +"\n\n\n Проверьте правильность данных для расслки.\n Введите 'да' или '+' для потдверждения")
    bot.register_next_step_handler(message, check_correct)


def check_correct(message):
    if message.text == 'да' or message.text == '+':
        MailListing(token, groupId, textForListing, message.chat.id)


def MailListing(token, groupId, text, ChatId):
    vk_session = vk_api.VkApi(token=token)

    members=vk_session.method("groups.getMembers", {"group_id": groupId, "v": 5.131, "sort": "id_asc", "count": 1000, "offset": 0})['items']

    for element in members:
        try: 
            vk_session.method("messages.send", {"user_id":element, "message":text, "random_id":0})
        except:
            pass

    bot.send_message(ChatId, "Рассылка выполнена успешно")


bot.polling(none_stop=True)