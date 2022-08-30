import io
import os
import requests
from telebot import TeleBot
from telebot.types import Message
from dotenv import load_dotenv
import csv
from datetime import datetime
from googleapiclient.discovery import build, Resource
from google.oauth2 import service_account

load_dotenv()

token = os.getenv('BOT_TOKEN')
sheetID = os.getenv('SPREADSHEET_ID')
sheetLetter = os.getenv('SPREADSHEET_LETTER')

bot = TeleBot(token)



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
    
def parse(url):
    data = readCSV(url)

    report = Report(data)

    currentDate = datetime.strptime(data[0].date, '%m/%d/%Y').strftime('%B %Y')

    googleSheetsWrite(report.values(), currentDate)

def googleLogin() -> Resource:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def googleSheetsWrite(values: list, sheetName: str):
    range = f"{sheetName}!A1:{sheetLetter}"
    
    # Get list of sheets
    sheet_metadata = service.spreadsheets().get(spreadsheetId=sheetID).execute()
    sheets = [sheet['properties']['title'] for sheet in sheet_metadata.get('sheets', '')]

    if sheetName not in sheets:
        # Create Sheet
        batch_update_values_request_body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': sheetName
                        }
                    }
                },
                {
                "repeatCell": {
                    "range": {
                    "sheetId":  sheetID,
                    "startRowIndex": 0,
                    "endRowIndex": 1
                    },
                    "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                        "red": 0.0,
                        "green": 0.0,
                        "blue": 0.0
                        },
                        "horizontalAlignment" : "CENTER",
                        "textFormat": {
                        "foregroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        },
                        "fontSize": 12,
                        "bold": True
                        }
                    }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheetID, body=batch_update_values_request_body).execute()

    values = [['Date', 'Type', 'Amount', 'Currency', 'Benificiary', 'Payment details']] + values

    # Add vales
    return service.spreadsheets().values().update(
        spreadsheetId=sheetID, range=range,
        valueInputOption="USER_ENTERED", body={ 'values': values }).execute()

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
    
    url = bot.get_file_url(message.document.file_id)
    print(url)
    # downloaded_file = botdownload_file(fileInfo.file_path)

    # with open('csv.csv', 'wb') as new_file:
        # new_file.write(downloaded_file)
    # readCSV('csv.csv')

@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    bot.send_message(message.chat.id, message.text)


# service = googleLogin()

# print(dir(service))
bot.infinity_polling(20)

# parse('https://api.telegram.org/file/bot5583575129:AAH1TzDpQ1EOtLB6CaXeL3ObwvMs03wfZeo/documents/file_0.csv')