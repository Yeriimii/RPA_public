import time
import re
import os
import subprocess
import poplib
import email
from email.header import decode_header, make_header
from dotenv import load_dotenv
from dateutil.parser import parse
from slack_sdk import WebClient

mail_server = ''
mail_user = ''
mail_password = ''

load_dotenv('.env')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
slack = WebClient(SLACK_TOKEN)

def check_email() -> str:
    try_count = 1
    while True:
        pop3_server = poplib.POP3(mail_server, 110)
        pop3_server.user(mail_user)
        pop3_server.pass_(mail_password)
        num_emails = len(pop3_server.list()[1])

        for i in reversed(range(1, num_emails+1)):
            msg = pop3_server.retr(i)
            msg = b"\n".join(msg[1])
            message = email.message_from_bytes(msg)
            fr = make_header(decode_header(message.get('From')))
            subject = make_header(decode_header(message.get('Subject')))

            if message.is_multipart():
                for part in message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)  # decode
                        break
            else:
                body = message.get_payload(decode=True)
            try:
                body = body.decode('utf-8')
            except:
                body = re.sub(r'\r|\n', r'', body.decode('cp949'))

            try:
                receved_date = parse(message["Date"]).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
            find_text = ''
            if (find_text in str(subject)) and ('파일명' in body) and (parse('') <= parse(receved_date) <= parse('')):
                file_name = re.findall(r'파일명.+\.mp4', body)[0]

                if file_name:
                    download_file:str = file_name.split(':')[1].strip()
                    return download_file

        slack.chat_postMessage(channel='', text=f'{try_count} ...\n')
        try_count += 1
        time.sleep(900)

if __name__ == '__main__':
    download_file = check_email()
    slack.chat_postMessage(channel='', text=f'파일명: {download_file}')

    aspera_server = ''  # 리모트 위치
    aspera_user = ''  # 접속 아이디
    file_source = f'./{download_file}'  # 리모트 소스 위치
    file_destination = f'./{download_file}'  # 다운로드 받을 경로 + 파일 이름 + 확장자
    ssh_path = ''

    slack.chat_postMessage(channel='', text=f'')
    subprocess.run(['C:\\Program Files\\Aspera\\Client\\bin\\ascp', '-i', ssh_path, '-P33001', '-T', '-I', '100M', f'{aspera_user}@{aspera_server}:{file_source}', file_destination])
    slack.chat_postMessage(channel='', text=f'')
