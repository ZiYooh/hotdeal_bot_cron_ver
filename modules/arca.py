# -*- coding: UTF-8 -*-
import time
import os
import sys
import requests
import asyncio

from bs4 import BeautifulSoup
from mariadb import ProgrammingError

# 절대경로 참조
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils import mylogger
from utils import mywebhook
from utils import mydb
from utils import tg_bot_control


# Logger Setting Start
logger = mylogger.set_logger("INFO")
sys.excepthook = mylogger.handle_exception
# Logger Setting End

# URL 설정
arca_url = "https://arca.live/b/hotdeal"

# 임시 변수 선언
temp_num = ""
temp_category = ""
temp_title = ""
temp_price = ""
temp_delivery = ""
temp_link = ""
temp_time = ""

insert_data_query = ""
select_count_query = ""

temp_msg = ""

# def run_scraping(mode_all, mode_category, mode_keyword, discord_webhook):
def run_scraping(mode_all, mode_category, mode_keyword):
    logger.debug("[아카라이브 핫딜 채널 크롤링 시작]")
    logger.debug("===========================================")
    
    # 페이지 소스 가져오기
    response = requests.get(arca_url)
    if response.status_code == 200:
        logger.debug("HTTP 응답 코드: " + str(response.status_code))
        html = response.text
        
        # Soup에 HTML 데이터 넣어주기
        soup = BeautifulSoup(html, "html.parser")

        # 스크래핑 시작
        div_result = soup.find_all("div", "vrow hybrid")
        
        new_post_flag = 0
        
        for i in range(len(div_result)):
            if div_result[i].find("a", "title").get_text().replace("\n", "")  != "":
                # 데이터 가져오기
                temp_num = div_result[i].find("a", "title").get("href").split("/")[3].split("?")[0] # 글번호
                temp_category = div_result[i].find("a", "badge").get_text().replace("\n", "") # 카테고리
                temp_title = div_result[i].find("a", "title").get_text().replace("\n", "") # 제목
                temp_price = div_result[i].find("span", "deal-price").get_text().replace("\n", "") # 가격
                temp_delivery = div_result[i].find("span", "deal-delivery").get_text().replace("\n", "") # 배송비
                temp_link = "https://arca.live" + div_result[i].find("a", "title").get("href") # 링크
                temp_time = div_result[i].find("time",).get("datetime") # 글작성시간
                
                # DB 연결
                conn = mydb.connect_to_db_server()
                cursor = mydb.get_cursor(conn)
                
                # 게시글 중복 유무 확인
                select_count_result = 0
                
                try:
                    select_count_query = "SELECT count(*) FROM arca_list WHERE num=" + temp_num + ";"
                    select_count_result = mydb.run_query_return_one(cursor, select_count_query)[0]
                    cursor.close()
                except ProgrammingError as e:
                    logger.error(e)
                    pass
                
                if select_count_result < 1:
                    insert_data_query = "INSERT INTO arca_list (num, category, title, price, delivery, link, time) VALUES (?, ?, ?, ?, ?, ?, ?)"
                    cursor = mydb.get_cursor(conn)
                    cursor.execute(insert_data_query, (int(temp_num), temp_category, temp_title, temp_price, temp_delivery, temp_link, temp_time))
                    conn.commit()
                    cursor.close()

                    if new_post_flag == 0:
                        new_post_flag = 1

                    if mode_all == True:
                        # temp_msg = mywebhook.get_msg_header_all(temp_category, temp_title, temp_price, temp_link)
                        temp_msg = tg_bot_control.get_msg_header_all(temp_category, temp_title, temp_price, temp_link)
                        logger.info("알림 메세지 발송\n" + temp_msg)
                        # mywebhook.send_discord_webhook(discord_webhook, temp_msg)
                        asyncio.run(tg_bot_control.send_telegram_message(temp_msg))
                        time.sleep(3)
                        logger.info("==========================================")
                        
                    else:
                        if mode_category == True:
                            cursor = mydb.get_cursor(conn)
                            select_category_query = "SELECT category FROM conf_category WHERE uid=1 and site='arca'"
                            select_category_result = mydb.run_query_return_all(cursor, select_category_query)
                            cursor.close()
                            
                            for selected_category in select_category_result:
                                if selected_category[0] in temp_category:
                                    # temp_msg = mywebhook.get_msg_header_category(selected_category[0], temp_category, temp_title, temp_price, temp_link)
                                    temp_msg = tg_bot_control.get_msg_header_category(selected_category[0], temp_category, temp_title, temp_price, temp_link)
                                    logger.info("알림 메세지 발송\n" + temp_msg)
                                    # mywebhook.send_discord_webhook(discord_webhook, temp_msg)
                                    asyncio.run(tg_bot_control.send_telegram_message(temp_msg))
                                    time.sleep(3)
                                    logger.info("==========================================")
                        
                        if mode_keyword == True:
                            cursor = mydb.get_cursor(conn)
                            select_keyword_query = "SELECT keyword FROM conf_keyword WHERE uid=1 and site='arca'"
                            select_keyword_result = mydb.run_query_return_all(cursor, select_keyword_query)
                            cursor.close()
                            
                            for selected_keyword in select_keyword_result:
                                if selected_keyword[0] in temp_title:
                                    # temp_msg = mywebhook.get_msg_header_keyword(selected_keyword[0], temp_category, temp_title, temp_price, temp_link)
                                    temp_msg = tg_bot_control.get_msg_header_keyword(selected_keyword[0], temp_category, temp_title, temp_price, temp_link)
                                    logger.info("알림 메세지 발송\n" + temp_msg)
                                    # mywebhook.send_discord_webhook(discord_webhook, temp_msg)
                                    asyncio.run(tg_bot_control.send_telegram_message(temp_msg))
                                    time.sleep(3)
                                    logger.info("==========================================")
                    
                mydb.close_db_server(conn)
            

        if new_post_flag == 0:
            logger.debug("새로운 글이 없습니다.")
        
        logger.debug("==========================================")
        logger.debug("[아카라이브 핫딜 채널 크롤링 종료]")
        
    else:
        logger.error("통신 에러가 발생하였습니다.")
        logger.error("HTTP 응답 코드: " + str(response.status_code))
