import mariadb
import sys
import os


# 절대경로 참조
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils import mylogger

# 로거 설정
logger = mylogger.set_logger("INFO")
sys.excepthook = mylogger.handle_exception


def connect_to_db_server():
    # Get DB connection info
    _user = None
    _password = None
    _host = None
    _port = None
    _database = None
    
    with open ('../conf/db.conf', 'r') as file:
        line = None
        while line != '':
            line = file.readline().strip('\n')
            
            if 'user=' in line:
                _user = line.split('=')[1]
            
            if 'password=' in line:
                _password = line.split('=')[1]
            
            if 'host=' in line:
                _host = line.split('=')[1]
            
            if 'port=' in line:
                _port = int(line.split('=')[1])
            
            if 'database=' in line:
                _database = line.split('=')[1]
    
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=_user,
            password=_password,
            host=_host,
            port=_port,
            database=_database
        )
        
    except mariadb.Error as e:
        logger.error(f"Error connecting to MariaDB Platform: {e}")
        # sys.exit(1)
        os._exit(0)

    return conn


def get_cursor(connection):
    return connection.cursor()


def close_db_server(connection):
    connection.close()


def run_query_no_return(connection, cursor, query):
    cursor.execute(query)
    connection.commit()


def run_query_return_one(cursor, query):
    cursor.execute(query)

    # result_set[0], result_set[1] ... 의 형태로 사용
    result_set = cursor.fetchone()

    return result_set


def run_query_return_all(cursor, query):
    cursor.execute(query)

    # result_set[0][0], result_set[0][1], result_set[1][0] ... 의 형태로 사용
    result_set_all = cursor.fetchall()

    return result_set_all