import sys
import requests

from utils import mylogger


# Logger Setting Start
logger = mylogger.set_logger("INFO")
sys.excepthook = mylogger.handle_exception
# Logger Setting End


def send_discord_webhook(discord_url, msg):
        headers = {"Content-Type": "application/json",}
        data = '{"content": "' + msg + '"}' # 여기서 큰/작은따옴표 때문에 요청 오류 발생했었음 
        data = data.encode("utf-8").decode("iso-8859-1")
        
        response = requests.post(discord_url, headers=headers, data=data)
        
        if not response.status_code < 400:
            logger.error("디스코드 웹훅 메세지 발송 오류가 발생하였습니다.")
            logger.error("HTTP 응답 코드: " + str(response.status_code))


def get_msg_template(category, title, price, link):
    temp_msg = ''
    
    temp_msg += '카테고리: ' + category + '\\n'
    temp_msg += '__**제목: ' + title + '**__\\n'
    temp_msg += '가격: ' + price + '\\n'
    temp_msg += '링크: ' + link
    
    return temp_msg


def get_msg_header_all(category, title, price, link):
    temp_msg = ''
    
    temp_msg = '>>> _새글 알림_\\n' 
    temp_msg += get_msg_template(category, title, price, link)
    
    return temp_msg
    

def get_msg_header_category(conf_category, category, title, price, link):
    temp_msg = ''
    
    temp_msg = f'>>> _카테고리 알림 [{conf_category}]_\\n' 
    temp_msg += get_msg_template(category, title, price, link)
    
    return temp_msg


def get_msg_header_keyword(conf_keyword, category, title, price, link):
    temp_msg = ''
    
    temp_msg = f'>>> _키워드 알림 [{conf_keyword}]_\\n' 
    temp_msg += get_msg_template(category, title, price, link)
    
    return temp_msg