import telebot, random, sqlite3
from flask import Flask, request
from os import path


TOKEN = "token"
URL = "pythonanywhere_url"
ROOT = path.dirname(path.realpath(__file__))

bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=URL)
#https://api.telegram.org/bottoken/deleteWebHook

app = Flask(__name__)

num_button_without = 0
num_button_with = 0

def random_tasty(message, id_user):
	# БД
	filters_db = ()
	with sqlite3.connect(path.join(ROOT, "users.db")) as conn:
		cursor = conn.cursor()
		sql = "SELECT post, nosugar FROM USERS WHERE chat_id = ?"
		cursor.execute(sql, (id_user,))
		filters_db = cursor.fetchall()
	with sqlite3.connect(path.join(ROOT, "tasty.db")) as conn:
		cursor = conn.cursor()
		if filters_db[0][0] == 0 and filters_db[0][1] == 0:
			sql = "SELECT tasty_table.name_of_tasty FROM tasty_table INNER JOIN drinks ON (tasty_table.id=drinks.id_tasty) WHERE drinks.drink=?"
			cursor.execute(sql, (str(message).lower(),))
		elif filters_db[0][0] == 1 and filters_db[0][1] == 1:
			sql = "SELECT tasty_table.name_of_tasty FROM tasty_table INNER JOIN drinks ON (tasty_table.id=drinks.id_tasty) WHERE drinks.drink=? AND tasty_table.post=? AND tasty_table.nosugar=?"
			cursor.execute(sql, (str(message).lower(),filters_db[0][0], filters_db[0][1]))
		elif filters_db[0][0] == 1 and filters_db[0][1] == 0:
			sql = "SELECT tasty_table.name_of_tasty FROM tasty_table INNER JOIN drinks ON (tasty_table.id=drinks.id_tasty) WHERE drinks.drink=? AND tasty_table.post=?"
			cursor.execute(sql, (str(message).lower(), filters_db[0][0],))
		elif filters_db[0][0] == 0 and filters_db[0][1] == 1:
			sql = "SELECT tasty_table.name_of_tasty FROM tasty_table INNER JOIN drinks ON (tasty_table.id=drinks.id_tasty) WHERE drinks.drink=? AND tasty_table.nosugar=?"
			cursor.execute(sql, (str(message).lower(), filters_db[0][1]))
		try:
			list_tasty = cursor.fetchall()
		except:
			return "Извини, но такого нет"
	return random.choice(list_tasty)

def random_without_drink(message):
	# БД
	filters_db = ()
	with sqlite3.connect(path.join(ROOT, "users.db")) as conn:
		cursor = conn.cursor()
		sql = "SELECT post, nosugar FROM USERS WHERE chat_id = ?"
		cursor.execute(sql, (message.chat.id,))
		filters_db = cursor.fetchall()
	with sqlite3.connect(path.join(ROOT, "tasty.db")) as conn:
		cursor = conn.cursor()
		if filters_db[0][0] == 0 and filters_db[0][1] == 0:
			sql = "SELECT name_of_tasty FROM tasty_table"
			cursor.execute(sql)
		elif filters_db[0][0] == 1 and filters_db[0][1] == 1:
			sql = "SELECT name_of_tasty FROM tasty_table WHERE post=?, nosugar=?"
			cursor.execute(sql, (filters_db[0][0], filters_db[0][1],))
		elif filters_db[0][0] == 1 and filters_db[0][1] == 0:
			sql = "SELECT name_of_tasty FROM tasty_table WHERE post=?"
			cursor.execute(sql, (filters_db[0][0],))
		elif filters_db[0][0] == 0 and filters_db[0][1] == 1:
			sql = "SELECT name_of_tasty FROM tasty_table WHERE nosugar=?"
			cursor.execute(sql, (filters_db[0][1],))
		try:
			list_tasty = cursor.fetchall()
		except:
			return "Извини, но такого нет"
	return random.choice(list_tasty)

@app.route('/', methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200


@bot.message_handler(commands=["start"])
def start(message):
	global num_button_without
	global num_button_with
	num_button_without = 0
	num_button_with = 0
	user_markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=False)
	button_without = telebot.types.KeyboardButton(text="Просто вкусняшку хочу")
	button_with = telebot.types.KeyboardButton(text="Мне к напитку")
	button_filter = telebot.types.KeyboardButton(text="Установить особенности вкусняшки")
	user_markup.add(button_without, button_with, button_filter)
	bot.send_message(message.chat.id,
					 "Привет, я бот, который знает какую вкусняшку ты хочешь именно сейчас. Если тебе что-то неясно, то нажми /help, если же все хорошо, то давай начнем! Сделай свой выбор:", reply_markup=user_markup)


@bot.message_handler(commands=["help"])
def start(message):
	bot.send_message(message.chat.id,"Для того чтобы получить название вкусняшки, тебе достаточно нажать на кнопки ниже. Если они скрыты нажми на квадратик в клавиатуре.")

@bot.message_handler(content_types=["text"])
def choose(message):
	if message.text == "Просто вкусняшку хочу":
		global num_button_without
		global num_button_with
		num_button_without += 1
		num_button_with = 0
		if num_button_without == 3:
			bot.send_message(message.chat.id, "А у тебя, случайно, ничего не слипнется?")
		elif num_button_without == 4:
			bot.send_message(message.chat.id, "А ты все еще влазишь в свои любимые джинсы? Я что-то не уверен")
		elif num_button_without == 5:
			bot.send_message(message.chat.id, "Подумай, хочешь ли ты после такого взвешиваться?")
		elif num_button_without == 6:
			bot.send_message(message.chat.id, "Да одумайся ты уже")
		elif num_button_without == 7:
			bot.send_message(message.chat.id, "Я пытался...")
		elif num_button_without == 8:
			bot.send_message(message.chat.id, "...")
		elif num_button_without == 9:
			num_button_without = 0
			bot.send_message(message.chat.id, "Все, твоя взяла")
		else:
			return_message = random_without_drink(message)
			bot.send_message(message.chat.id, return_message)
	elif message.text == "Мне к напитку":
		num_button_without = 0
		#БД
		with sqlite3.connect(path.join(ROOT, "tasty.db")) as conn:
			cursor = conn.cursor()
			sql = "SELECT drink FROM drinks"
			cursor.execute(sql)
			#собираем напитки из БД для клавиатуры
			list_drink = cursor.fetchall()
		list_drink = set(list_drink)
		list_for_button = ', '.join(i[0] for i in list_drink)
		list_for_button = list_for_button.split(", ")
		markup = telebot.types.InlineKeyboardMarkup()
		#делаем несколько кнопок в ряду
		try:
			for i in range(0, len(list_for_button), 2):
				markup.row(telebot.types.InlineKeyboardButton(text=list_for_button[i], callback_data = list_for_button[i]), telebot.types.InlineKeyboardButton(text=list_for_button[i+1], callback_data = list_for_button[i+1]))
		except:
			markup.row(telebot.types.InlineKeyboardButton(text=list_for_button[-1], callback_data = list_for_button[-1]))
		bot.send_message(message.chat.id, "Я пока знаю немного напитков, но обещаю исправиться, а пока выбери один", reply_markup=markup)
	elif message.text == "Установить особенности вкусняшки":
		markup_sort = telebot.types.InlineKeyboardMarkup()
		button_k_postu = telebot.types.InlineKeyboardButton(text="Мне что-то к посту", callback_data = "button_k_postu")
		button_diet = telebot.types.InlineKeyboardButton(text="Я на диете", callback_data = "button_diet")
		button_clean = telebot.types.InlineKeyboardButton(text="Обнули фильтр", callback_data = "button_clean")
		markup_sort.add(button_k_postu)
		markup_sort.add(button_diet)
		markup_sort.add(button_clean)
		bot.send_message(message.chat.id, "Выбери категорию:",reply_markup=markup_sort)

@bot.callback_query_handler(func=lambda call:True)
def random_tasty_handler(call):
	if call.data != None and call.data != "button_k_postu" and call.data != "button_diet" and call.data != "button_clean":
		global num_button_without
		global num_button_with
		num_button_without = 0
		num_button_with += 1
		if num_button_with == 3:
			bot.send_message(call.message.chat.id, "А у тебя, случайно, ничего не слипнется?")
		elif num_button_with == 4:
			bot.send_message(call.message.chat.id, "А ты все еще влазишь в свои любимые джинсы? Я что-то не уверен")
		elif num_button_with == 5:
			bot.send_message(call.message.chat.id, "Подумай, хочешь ли ты после такого взвешиваться?")
		elif num_button_with == 6:
			bot.send_message(call.message.chat.id, "Да одумайся ты уже")
		elif num_button_with == 7:
			bot.send_message(call.message.chat.id, "Я пытался...")
		elif num_button_with == 8:
			bot.send_message(call.message.chat.id, "...")
		elif num_button_with == 9:
			num_button_with = 0
			bot.send_message(call.message.chat.id, "Все, твоя взяла")
		else:
			return_message = random_tasty(call.data, call.message.chat.id)
			bot.send_message(call.message.chat.id, "{} → {}".format(str(call.data).capitalize(), return_message[0]))
	elif call.data != None and (call.data == "button_k_postu" or call.data != "button_diet" or call.data != "button_clean"):
		# БД
		button_k_postu, button_diet = 0, 0
		if call.data == "button_k_postu":
			button_k_postu = 1
		elif call.data == "button_diet":
			button_diet = 1
		elif call.data == "button_clean":
			button_k_postu, button_diet = 0, 0
		with sqlite3.connect(path.join(ROOT, "users.db")) as conn:
			cursor = conn.cursor()
			try:
				sql = "INSERT INTO USERS VALUES(?, ?, ?)"
				cursor.execute(sql, (call.message.chat.id, 0 if button_k_postu != 1 else button_k_postu, 0 if button_diet != 1 else button_diet,))
			except:
				sql = "UPDATE USERS SET post=?, nosugar=?  WHERE chat_id = ?"
				cursor.execute(sql, (0 if button_k_postu != 1 else button_k_postu,
									 0 if button_diet != 1 else button_diet, call.message.chat.id, ))
			conn.commit()
		bot.send_message(call.message.chat.id, "{} {} {}".format("Тебе надо что-то постное." if call.data == "button_k_postu" else "","Тебе надо что-то диетическое." if call.data == "button_diet" else "","Ты очистил фильтры." if call.data == "button_clean" else ""))

if __name__ == "__main__":
	bot.polling()