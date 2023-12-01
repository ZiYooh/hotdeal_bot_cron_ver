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
    
    url_query = "SELECT webhook_link FROM conf_general WHERE uid = 1"
    
    discord_url = mydb.run_query_return_one(cursor, url_query)[0]
    # logger.debug(discord_url)
    mydb.close_db_server(conn)
    
    arca.run_scraping(True, False, False, discord_url)
