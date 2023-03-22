# -*- coding: utf-8 -*-
# built-in module
import pytz
import datetime
import getpass
import os

# third-party module
import pymysql
import pandas as pd
from dotenv import load_dotenv

username = getpass.getuser()
load_dotenv(f'../.env')

DB_HOST = os.getenv('DB_HOST')
DB_SUPER_USER = os.getenv('DB_SUPER_USER')
DB_SUPER_PW = os.getenv('DB_SUPER_PW')
DB_NAME = os.getenv('DB_NAME')

def weekday_table_create(today):
    KST = pytz.timezone('Asia/Seoul')
    now = today.strftime("%Y%m%d")
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    query_create_table = f"""
        CREATE TABLE tasktable{now}(
            No INT(11) NOT NULL AUTO_INCREMENT,
            ct_id INT(11) NOT NULL ,
            c_id INT(11) NOT NULL ,
            p_id INT(11) NOT NULL ,
            작품명 VARCHAR(500) NOT NULL ,
            업로더 VARCHAR(500) NOT NULL DEFAULT "-",
            제목 VARCHAR(500) NOT NULL DEFAULT "-",
            본문 VARCHAR(500) NOT NULL DEFAULT "-",
            url VARCHAR(500) NOT NULL ,
            rt VARCHAR(10) NOT NULL DEFAULT "-",
            수집일 DATE NOT NULL ,
            게시일 DATE NOT NULL ,
            i_id INT(11) NOT NULL ,
            info VARCHAR(500) NOT NULL ,
            PRIMARY KEY(No)
        )
    """
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute(query_create_table)
    conn.close()

    return print('Table Creation Complete')

def weekday_table_insert(today):
    KST = pytz.timezone('Asia/Seoul')
    now = today.strftime("%Y-%m-%d")
    startdate = today - datetime.timedelta(days=14)
    startdate = startdate.strftime("%Y-%m-%d")
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    query_select_table = f"""
        SELECT
        FROM
        WHERE
        ORDER BY desc
    """
    df_read_sql = pd.read_sql(query_select_table, conn)
    df_read_sql = df_read_sql.astype({'':'str'})
    insert_db = df_read_sql.values.tolist()

    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y%m%d")
    query_insert_table = f"""
        INSERT INTO
            (, , , , , , , , , , , , )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.executemany(query_insert_table, insert_db)
    conn.commit()
    conn.close()

    return print('Table Insert Complete')

def weekend_table_create(today, ampm):
    KST = pytz.timezone('Asia/Seoul')
    now = today.strftime("%Y%m%d")
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    query_create_table = f"""
        CREATE TABLE tasktable{now}_{ampm}(
            No INT(11) NOT NULL AUTO_INCREMENT,
            ct_id INT(11) NOT NULL ,
            c_id INT(11) NOT NULL ,
            p_id INT(11) NOT NULL ,
            작품명 VARCHAR(500) NOT NULL ,
            업로더 VARCHAR(500) NOT NULL DEFAULT "-",
            제목 VARCHAR(500) NOT NULL DEFAULT "-",
            본문 VARCHAR(500) NOT NULL DEFAULT "-",
            url VARCHAR(500) NOT NULL ,
            rt VARCHAR(10) NOT NULL DEFAULT "-",
            수집일 DATE NOT NULL ,
            게시일 DATE NOT NULL ,
            i_id INT(11) NOT NULL ,
            info VARCHAR(500) NOT NULL ,
            PRIMARY KEY(No)
        )
    """
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute(query_create_table)
    conn.close()

    return print('Table Creation Complete')

def weekend_table_insert(today, ampm):
    KST = pytz.timezone('Asia/Seoul')
    now = today.strftime("%Y-%m-%d")
    startdate = today - datetime.timedelta(days=14)
    startdate = startdate.strftime("%Y-%m-%d")
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    query_select_table = f"""
        SELECT
        FROM
        WHERE
        ORDER BY desc
    """
    df_read_sql = pd.read_sql(query_select_table, conn)
    df_read_sql = df_read_sql.astype({'게시일':'str'})
    insert_db = df_read_sql.values.tolist()

    now = today.strftime("%Y%m%d")

    query_insert_table = f"""
        INSERT INTO tasktable{now}_{ampm}
            (, , , , , , , , , , , , )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.executemany(query_insert_table, insert_db)
    conn.commit()
    conn.close()

    return print('Table Insert Complete')

def table_drop():
    KST = pytz.timezone('Asia/Seoul')
    deletedate = datetime.datetime.now(KST) - datetime.timedelta(days=7)
    deletedate = deletedate.strftime("%Y%m%d")
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    query_drop_table = f"""
        DROP TABLE ;
    """
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute(query_drop_table)
    conn.close()

    return print('Table Drop Complete')

def update_from_today_to_sdt():
    KST = pytz.timezone('Asia/Seoul')
    today = datetime.datetime.now(KST).strftime("%Y%m%d")
    select_query = f"""
        SELECT
        FROM
        WHERE
        """
    update_query = """
        UPDATE
        SET
        WHERE
        """
    with pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME) as conn:
        curs = conn.cursor(pymysql.cursors.DictCursor)
        df_read_sql = pd.read_sql(select_query, conn).astype('str')
        update_data = df_read_sql.values.tolist()
        fetch_count = curs.executemany(update_query, update_data)
        conn.commit()

    return fetch_count

def insert_from_sdt_to_dct():
    KST = pytz.timezone('Asia/Seoul')
    yesterday = datetime.datetime.now(KST) - datetime.timedelta(days=5)
    yesterday = yesterday.strftime("%Y-%m-%d")
    today = datetime.datetime.now(KST).strftime("%Y-%m-%d")

    with pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME) as conn:
        curs = conn.cursor(pymysql.cursors.DictCursor)
        select_query = f"""
            SELECT
            FROM
            WHERE
            """
        df_read_sql = pd.read_sql(select_query, conn).astype('str')
        insert_data = df_read_sql.values.tolist()
        insert_query = """
            INSERT IGNORE INTO
            VALUES (%s, %s, %s, %s)
            """
        fetch_count = curs.executemany(insert_query, insert_data)
        conn.commit()

    return fetch_count

def insert_from_sdt_to_art():
    KST = pytz.timezone('Asia/Seoul')
    yesterday = datetime.datetime.now(KST) - datetime.timedelta(days=5)
    yesterday = yesterday.strftime("%Y-%m-%d")
    today = datetime.datetime.now(KST).strftime("%Y-%m-%d")

    with pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME) as conn:
        curs = conn.cursor(pymysql.cursors.DictCursor)
        select_query = f"""
            SELECT
            FROM
            WHERE
            """
        df_read_sql = pd.read_sql(select_query, conn).astype('str')
        insert_data = df_read_sql.values.tolist()
        insert_query = """
            INSERT IGNORE INTO
            VALUES (%s, %s, %s, %s)
            """
        fetch_count = curs.executemany(insert_query, insert_data)
        conn.commit()

    return fetch_count

def select_dct_to_delete() -> pd.DataFrame:
    """
    delete_check_table 에서 신고되지 않은 URL 을 select 후 df 로 리턴하는 함수.

    Returns:
        pd.DataFrame: 쿼리 결과를 DataFrame으로 리턴합니다. 컬럼은 다음과 같습니다.\n
        반환하는 컬럼 ->
    """
    KST = pytz.timezone('Asia/Seoul')
    yesterday = datetime.datetime.now(KST) - datetime.timedelta(days=14)
    yesterday = yesterday.strftime("%Y-%m-%d")
    today = datetime.datetime.now(KST).strftime("%Y-%m-%d")
    with pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME) as conn:
        curs = conn.cursor(pymysql.cursors.DictCursor)
        select_query = f"""
            SELECT
            FROM
            JOIN ON
            JOIN ON
            WHERE
            ORDER BY asc
            """
        df = pd.read_sql(select_query, conn).astype({'':'str',
                                                    '':'int',
                                                    '':'int',
                                                    '': 'str',
                                                    '': 'str'})

    return df

def update_system_report_date_from_dct(update_data: list[str], report_success=True):
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if report_success:  # TODO: 리포팅 실패했을 때와 성공했을 때의 쿼리가 같은 문제 해결이 필요
        update_query = """
            UPDATE
            SET
            WHERE
            """
    else:
        update_query = """
            UPDATE
            SET
            WHERE
            """
    fetch_count = curs.executemany(update_query, update_data)
    if fetch_count is not int:
        fetch_count = 0
    conn.commit()
    curs.close()
    conn.close()

    return fetch_count

def select_delete_check():
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    query = f"""
        SELECT
        FROM
        JOIN ON
        WHERE
        ORDER BY asc
        ;
    """

    df_read_sql = pd.read_sql(query, conn)
    conn.close()

    df = df_read_sql
    df.reset_index(drop=True, inplace=True)

    return df

def update_delete_yn_from_dct(dc_id, site_name):

    conn = pymysql.connect(host=DB_HOST,
                            user=DB_SUPER_USER,
                            password=DB_SUPER_PW,
                            port=3306,
                            db=DB_NAME)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    update_query = f"""
        UPDATE
        SET
        WHERE
        """
    curs.execute(update_query)
    conn.commit()
    curs.close()
    conn.close()

if __name__ == '__main__':
    fetch = insert_from_sdt_to_dct()
    print(fetch)
