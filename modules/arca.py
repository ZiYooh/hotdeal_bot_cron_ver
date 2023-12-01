# -*- coding: UTF-8 -*-
import time
import os
import sys
import requests
import mariadb

from bs4 import BeautifulSoup
from mariadb import ProgrammingError

# 절대경로 참조
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils import mylogger
from utils import mywebhook
from utils import mydb


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

def run_scraping(mode_all, mode_category, mode_keyword, discord_webhook):
    logger.info("[아카라이브 핫딜 채널 크롤링 시작]")
    logger.info("===========================================")
    
    # 페이지 소스 가져오기
    response = requests.get(arca_url)
    if response.status_code == 200:
        logger.info("HTTP 응답 코드: " + str(response.status_code))
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
                    select_count_query = "SELECT count (*) FROM arca_list WHERE num=" + temp_num + ";"
                    select_count_result = mydb.run_query_return_one(cursor, select_count_query)[0]
                    cursor.close()
                except ProgrammingError:
                    pass
                
                if select_count_result > 0:
                    insert_data_query = "INSERT INTO arca_list (num, category, title, price, delivery, link, time) VALUES (?, ?, ?, ?, ?, ?, ?)"
                    cursor = mydb.get_cursor(conn)
                    cursor.execute(insert_data_query, (int(temp_num), temp_category, temp_title, temp_price, temp_delivery, temp_link, temp_time))
                    conn.commit()
                    cursor.close()    

                    if new_post_flag == 0:
                        new_post_flag = 1

                    if mode_all == True:
                        temp_msg = mywebhook.get_msg_header_all(temp_category, temp_title, temp_price, temp_link)
                        logger.info(temp_msg)
                        mywebhook.send_discord_webhook(discord_webhook, temp_msg)
                        time.sleep(3)
                        
                    else:
                        if mode_category == True:
                            return
                        elif mode_keyword == True:
                            return
                        else:
                            # TODO: DB와 연계하여 에러 핸들링
                            logger.error("모드 설정 오류가 발생하였습니다.")
                            return
                
                mydb.close_db_server(conn)
            

        if new_post_flag == 0:
            logger.info("새로운 글이 없습니다.")
        
        logger.info("==========================================")
        logger.info("[아카라이브 핫딜 채널 크롤링 종료]")
        
    else:
        logger.error("통신 에러가 발생하였습니다.")
        logger.error("HTTP 응답 코드: " + str(response.status_code))
