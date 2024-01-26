import sys
import os
import telegram

# 절대경로 참조
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils import mylogger


# Logger Setting Start
logger = mylogger.set_logger("INFO")
sys.excepthook = mylogger.handle_exception
# Logger Setting End


# 텔레그램 봇 설정파일 파싱
def get_telegram_bot_token():    
    _token = ""
    with open ('conf/tg.conf', 'r') as file:
        line = None
        while line != '':
            line = file.readline().strip('\n')
            
            if 'token=' in line:
                _token = line.split('=')[1]
            
    return _token


def get_telegram_bot_chatid():    
    _chatid = ""
    with open ('conf/tg.conf', 'r') as file:
        line = None
        while line != '':
            line = file.readline().strip('\n')
            
            if 'chatid=' in line:
                _chatid = line.split('=')[1]
    
    return _chatid
            


async def send_telegram_message(msg):
    _token = get_telegram_bot_token()
    _chatid = get_telegram_bot_chatid()
    
    bot = telegram.Bot(token = _token)

    await bot.send_message(_chatid, msg, parse_mode="markdown")


def get_msg_template(category, title, price, link):
    temp_msg = ''
    
    temp_msg += '카테고리: ' + category + '\n'
    temp_msg += '*제목: ' + title + '*\n'
    temp_msg += '가격: ' + price + '\n'
    temp_msg += '링크: [바로가기](' + link + ')'
    
    return temp_msg


def get_msg_header_all(category, title, price, link):
    temp_msg = ''
    
    temp_msg = '*새글 알림*\n' 
    temp_msg += get_msg_template(category, title, price, link)
    
    return temp_msg
    

def get_msg_header_category(conf_category, category, title, price, link):
    temp_msg = ''
    
    temp_msg = f'*카테고리 알림 [{conf_category}]*\n' 
    temp_msg += get_msg_template(category, title, price, link)
    
    return temp_msg


def get_msg_header_keyword(conf_keyword, category, title, price, link):
    temp_msg = ''
    
    temp_msg = f'*키워드 알림 [{conf_keyword}]*\n' 
    temp_msg += get_msg_template(category, title, price, link)
    
    return temp_msg