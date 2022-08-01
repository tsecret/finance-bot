import io
import os
import requests
from telebot import TeleBot
from telebot.types import Message
from dotenv import load_dotenv
import csv
from datetime import date, datetime

load_dotenv()

token = os.getenv('BOT_TOKEN')

bot = TeleBot(token)



def parse(url):
    data = readCSV(url)

    report = Report(data)

    for row in report.values():
        print(row)

    

class Transaction:
    def __init__(self, values: list) -> None:
        self.date = values[0]
        self.type = values[2]
        self.benificiary = values[3]
        self.details = values[4]
        self.iban = values[5]
        self.bic = values[6]
        self.debit = float(values[15]) if values[15] != '' else 0
        self.credit = float(values[16]) if values[16] != '' else 0
        self.currency = values[17]

class Report:
    def __init__(self, data: list[Transaction]) -> None:
        self.data = data
        self.totalDebit = sum([value.debit for value in data])
        self.totalCredit = sum([value.credit for value in data])
        self.left = round(self.totalCredit - abs(self.totalDebit), 2)

    def values(self) -> list:
        return [[
            value.date,
            value.type,
            value.credit if value.credit else value.debit,
            value.currency,
            value.benificiary,
            value.details,
        ] for value in self.data]
    

def readCSV(url: str) -> list[Transaction]:
    r = requests.get(url)
    buff = io.StringIO(r.text)
    dr = csv.reader(buff, delimiter=';')
    data: list[Transaction] = []
    for row in dr:
        try:
            datetime.strptime(row[0], '%m/%d/%Y')
            data.append(Transaction(row))
        except Exception as e:
            print(e)
            pass
    
    return data
        
@bot.message_handler(content_types=['document'])
def handle_docs_audio(message: Message):
    if message.document.mime_type != 'text/csv':
        bot.send_message(message.chat.id, 'File should be in csv format')
        return
    
    fileInfo = bot.get_file(message.document.file_id)
    url = bot.get_file_url(message.document.file_id)
    print(url)
    downloaded_file = botdownload_file(fileInfo.file_path)

    with open('csv.csv', 'wb') as new_file:
        new_file.write(downloaded_file)
    readCSV('csv.csv')


# bot.infinity_polling(20)

parse('https://api.telegram.org/file/bot5583575129:AAGo4lHd-JO-6aS8Ir2OPllHJHGSXmxO3AI/documents/file_13.csv')