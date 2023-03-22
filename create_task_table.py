import datetime
from rpa.mysql.db_manage import weekday_table_create, weekday_table_insert

if __name__ == '__main__':
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9))
    weekday_table_create(today) # 평일 테이블 CREATE 함수
    weekday_table_insert(today) # 평일 테이블 SELECT + INSERT 함수
