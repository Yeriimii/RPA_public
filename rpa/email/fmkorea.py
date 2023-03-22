# -*- encoding: utf-8 -*-
import os
import datetime
import getpass
import time
import pymysql
import smtplib
import pandas as pd
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from utilities.pickle_util import get_data

username = getpass.getuser()
load_dotenv(f'../.env')

DB_HOST = os.getenv('DB_HOST')
DB_SUPER_USER = os.getenv('DB_SUPER_USER')
DB_SUPER_PW = os.getenv('DB_SUPER_PW')
DB_NAME = os.getenv('DB_NAME')

mail_server = ""
mail_port = None
login_id = ""
login_pw = ""
from_mail_addr = login_id
to_mail_addr = ""
cc_addr = ""

client_list = get_data(filename='')

def send_mail_to_fmkorea_for_delete():
    cum_sum = 0
    session = smtplib.SMTP(host=mail_server, port=mail_port)  # Gmail Port: 587
    session.login(user=login_id, password=login_pw)

    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
    start_date = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)) - datetime.timedelta(days=5)
    start_date = start_date.strftime("%Y-%m-%d")

    conn = pymysql.connect(host=DB_HOST,
                        user=DB_SUPER_USER,
                        password=DB_SUPER_PW,
                        port=3306,
                        db=DB_NAME)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    base_html_1 = """
    <html>
    <head>
        <style>
            table {
                width: 100%;
                text-align: center;
                line-height: 1.0;
                margin: 1px 1px;
                }
        </style>
    </head>

    <body>
    <p>안녕하세요.<br>
    </p>"""


    base_html_2 = """
    <br>
    <p>감사합니다.</p>
    <br>
    </body>
    </html>
    """

    for idx, client in enumerate(client_list, 1):
        base_html_client = f"""
        <p><br>
        </p>

        <p></p>
        """

        query_select = f"""
        """

        df:pd.DataFrame = pd.read_sql(query_select, conn)
        if len(df) == 0:
            continue

        root_msg = MIMEMultipart('related')
        root_msg['Subject'] = ''
        root_msg['From'] = from_mail_addr
        root_msg['To'] = to_mail_addr
        root_msg['Cc'] = cc_addr
        root_msg.preamble = ''

        alternative_message = MIMEMultipart('alternative')
        root_msg.attach(alternative_message)

        text_msg = MIMEText('')
        alternative_message.attach(text_msg)

        msg_contents = base_html_1 + base_html_client + df.to_html(index=False, justify='center', col_space=100) + base_html_2
        text_msg = MIMEText(msg_contents, 'html', _charset="utf-8")
        alternative_message.attach(text_msg)

        # Attach the PDF file
        filename = f"../.pdf"
        with open(filename, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            attachment.add_header('', 'attachment', filename='.pdf')
            root_msg.attach(attachment)

        session.sendmail(from_mail_addr, [to_mail_addr, cc_addr], root_msg.as_string())
        update_query = """
            """
        fetch_count = curs.executemany(update_query, df[''].values.tolist())
        print(f'UPDATE ROWS: {fetch_count}')
        cum_sum += fetch_count
        conn.commit()
        time.sleep(1.5)
    session.quit()

    return cum_sum
