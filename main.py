import sys

from utils import mylogger
from utils import mywebhook
from utils import mydb

from modules import arca

# 로거 설정
logger = mylogger.set_logger("INFO")
sys.excepthook = mylogger.handle_exception


if __name__ == "__main__":
    conn = mydb.connect_to_db_server()
    cursor = mydb.get_cursor(conn)
    
    url_query = "SELECT * FROM conf_general WHERE uid = 1"
    
    discord_url = mydb.run_query_return_one(cursor, url_query)[1]
    mode_keyword = mydb.run_query_return_one(cursor, url_query)[2]
    mode_category = mydb.run_query_return_one(cursor, url_query)[3]
    mode_all = mydb.run_query_return_one(cursor, url_query)[4]
    
    logger.debug(discord_url)
    logger.debug(mode_keyword)
    logger.debug(mode_category)
    logger.debug(mode_all)
    
    mydb.close_db_server(conn)
    
    if mode_all == mode_keyword == mode_category == 0:
        logger.debug("uid 1 알림 off 상태")
    else:
        # arca.run_scraping(False, False, True, discord_url)
        # 디스코드 웹훅 사용시
        # arca.run_scraping(mode_all, mode_category, mode_keyword, discord_url)
        
        # 텔레그램 봇 사용시
        arca.run_scraping(mode_all, mode_category, mode_keyword)
    
    
