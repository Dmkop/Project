#!/usr/bin/python3

import telebot
import requests
from telebot.types import Message
from pprint import pprint
from datetime import datetime
import sqlite3
import class_for_bot

TOKEN = '755209205:AAEuhzhXN0-hU-8K0DYXfs2woNU1qj7p4G0'
YEAR = datetime.now().year
MONTH = datetime.now().month
DAY = datetime.now().day
HOUR = datetime.now().hour
MINUTE = datetime.now().minute

def privat_url():

	'''returns a list of dictionaries containing currency information'''

	#BASE_URL = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={DAY}.{MONTH}.{YEAR}'
	BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date={D}.{M}.{Y}'.format(D = DAY, M = MONTH, Y = YEAR)
	data = requests.get(BASE_URL)
	status = data.status_code
	return data.json()['exchangeRate']

exchange_data = privat_url()
bot = telebot.TeleBot(TOKEN)
#pprint(exchange_data)

def create_data_base(exc_data = exchange_data):

	"""The function creates data base 'exchange_rate' 
	'con' variable - creates data base
	'cur' variable - creates cursor in this data base"""

	con = sqlite3.connect('exchange_rate_data_base.db')
	cur = con.cursor()

	cur.execute("""CREATE TABLE IF NOT EXISTS exchange(
		cur_id INTEGER PRIMARY KEY,
		Currency TEXT,
		SaleRate REAL,
		PurchaseRate REAL)""")

	for item in range(1, len(exc_data)):
		cur.execute("""INSERT INTO exchange(Currency, SaleRate, PurchaseRate)
			VALUES(?, ?, ?)""",(exc_data[item]['currency'], exc_data[item]['saleRateNB'], exc_data[item]['purchaseRateNB']))

	while HOUR == 10 and MINUTE == 0:
		for item in range(1, len(exchange_data)):
			cur.execute("""UPDATE exchange
				SET SaleRate = exc_data[item]['saleRateNB'] WHERE cur_id = item""")
			cur.execute("""UPDATE exchange
				SET PurchaseRate = exc_data[item][purchaseRateNB] where cur_id = item""")
			
	cur.execute("""SELECT Currency, SaleRate, PurchaseRate FROM exchange""")
	res = cur.fetchall()
	my_list = [item for item in res]
	data_base_dict = {a:(b, s) for a, b, s in my_list}

	con.commit()
	con.close()
	return data_base_dict

def telebot_funcs(data = exchange_data, data_base_info = create_data_base()):

	lenght = len(data)

	@bot.message_handler(commands = ['start'])
	def start(message: Message):

		'''The function creates "start" commands in the bot`s help menu'''

		with open('/home/dmytro/SoftServe/My_project/Telebot/start', mode = 'r') as information:
			txt_inf = information.read()
			bot.reply_to(message, txt_inf)

	@bot.message_handler(commands = ['help'])
	def help_data(message: Message):

		'''The function creates "start" commands in the bot`s help menu'''

		with open('/home/dmytro/SoftServe/My_project/Telebot/help', mode = 'r') as help:
			txt_help = help.read()
			bot.reply_to(message, txt_help)

	@bot.message_handler(commands = ['info'])
	def info_data(message: Message):

		'''The function creates "start" commands in the bot`s help menu'''

		with open('/home/dmytro/SoftServe/My_project/Telebot/info', mode = 'r') as information:
			txt_inf = information.read()
			bot.reply_to(message, txt_inf)

	@bot.message_handler(content_types = ['text'])
	@bot.edited_message_handler(content_types = ['text'])
	def currency_code(message: Message):

		'''Sends the current exchange rate at the requests of the users'''

		if lenght == 0:
			bot.reply_to(message, "DATA BASE UPDATING")
			for item in data_base_info:
				if message.text.upper() == item:
					bot.reply_to(message, """The purchase rate at the Ukrainian National Bank equal: {p}\n 
						and the selling rate at the Ukrainian National Bank equal: {s}""".format(s = data_base_info[item][0], p = data_base_info[item][1]))
					return
		try:
			for item in range(1, len(exchange_data)):

				if message.text.upper() == exchange_data[item]['currency']:

					if message.text.upper() == 'EUR' or message.text.upper() == 'USD' or message.text.upper() == 'CHF' or message.text.upper() == 'CZK':
						bot.reply_to(message, 'The purchase rate equel: {purchase}\n' 
						' and the selling rate equel: {sale}'.format(purchase = exchange_data[item]['purchaseRate'], 
						sale = exchange_data[item]['saleRate']))
						return

					elif message.text.upper() == 'CZK' or message.text.upper() == 'GBR' or message.text.upper() == 'PLZ' or message.text.upper() == 'RUB':
						bot.reply_to(message, 'The purchase rate equel: {purchase}\n' 
						' and the selling rate equel: {sale}'.format(purchase = exchange_data[item]['purchaseRate'], 
						sale = exchange_data[item]['saleRate']))
						return

					else:
						bot.reply_to(message, 'The purchase rate at the Ukrainian National Bank equal: {purchase:.2f}\n '
						'and the selling rate at the Ukrainian National Bank equal: {sale:.2f}'.format(purchase = exchange_data[item]['purchaseRateNB'], 
						sale = exchange_data[item]['saleRateNB']))
						return

		#return bot.reply_to(message, "I can't handle this data yet")
			raise class_for_bot.Custom_Exception('Invalid input, please try again. If you have forgotten the currency code, all currency codes can be found here "/ info"')
			
		except class_for_bot.Custom_Exception as error:
			bot.reply_to(message, error.data)

	bot.polling(timeout=60)


if __name__ == '__main__':
	create_data_base()
	telebot_funcs()