# -*- coding: utf-8 -*-
import os
import json
import getpass
import datetime
import pymysql
import pandas as pd
from dotenv import load_dotenv
from notion_client import Client
from slack_sdk import WebClient

# read the '.env' file
username = getpass.getuser()
load_dotenv(f'../.env')

# 환경변수에서 NOTION_TOKEN 불러오기
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PW')
DB_NAME = os.getenv('DB_NAME')

# FIXME: NOTION은 database <- page <- block 으로 구성.
# Notion client 객체 생성
notion = Client(auth=NOTION_TOKEN)

today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')

# 할당량
admin = {'a': None,
         'b': None}
admin_user = ['a', 'b']

def assigned_task_check():
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_USER,
                            password=DB_PW,
                            port=3306,
                            db=DB_NAME)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 개별 수행량 테이블
    query = f"""
        SELECT
        FROM
        WHERE
        group by;
        """
    curs.execute(query)
    df = pd.DataFrame(curs.fetchall())
    if len(df) != 0:
        curr_a_perf = int(df[df['']==''][''].iat[0])
        curr_b_perf = int(df[df['']==''][''].iat[0])
    else:
        curr_a_perf = 0
        curr_b_perf = 0
    curs.close()
    conn.close()

    with open(f'../{today}.json', 'r') as f:
        data = json.load(f)

    notion.pages.update(
        **{
            'page_id': data['database_id_0']['child_page'],
            'properties': {
                '': {
                    'id': 'tu%3CD',
                    'number': curr_a_perf,
                    'type': 'number'}
                }
            }
    )

    notion.pages.update(
        **{
            'page_id': data['database_id_1']['child_page'],
            'properties': {
                '': {
                    'id': 'tu%3CD',
                    'number': curr_b_perf,
                    'type': 'number'}
                }
            }
    )

def send_message(terminate=False):
    with open(f'../{today}.json', 'r') as f:
        data = json.load(f)

    a_page = notion.pages.retrieve(data['database_id_0']['child_page'])
    a_task_process:float = round((a_page['properties']['진행률']['formula']['number'] * 100), 2)
    b_page = notion.pages.retrieve(data['database_id_1']['child_page'])
    b_task_process:float = round((b_page['properties']['진행률']['formula']['number'] * 100), 2)

    b_complete_block = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "알림 BOT 이 알려드려요 😀",
                    "emoji": True}
                },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎉 b님 할당량을 다 채우셨습니다.*\n{b_task_process}% 달성했어요."
                    },
                "accessory": {
                    "type": "image",
                    "image_url": "https://i.pinimg.com/564x/83/00/e7/8300e7fd4574c5e20b092f0cd883bfde.jpg",
                    "alt_text": "duck character thumbnail"}
                }
            ]
        }

    a_complete_block = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "알림 BOT 이 알려드려요 😀",
                    "emoji": True}
                },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎉 a님 할당량을 다 채우셨습니다.*\n{a_task_process}% 달성했어요."
                    },
                "accessory": {
                    "type": "image",
                    "image_url": "https://i.pinimg.com/564x/83/00/e7/8300e7fd4574c5e20b092f0cd883bfde.jpg",
                    "alt_text": "duck character thumbnail"}
                }
            ]
        }

    closing_block = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "알림 BOT 이 알려드려요 😀",
                    "emoji": True}
                },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*오늘 하루가 끝났습니다.*\n\n오늘의 달성도 알려드려요.\n"
                    },
                "accessory": {
                    "type": "image",
                    "image_url": "https://i.pinimg.com/564x/83/00/e7/8300e7fd4574c5e20b092f0cd883bfde.jpg",
                    "alt_text": "duck character thumbnail"}
                },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*b님*\n 👍 {b_task_process} % 달성하셨습니다."
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*a님*\n 👍 {a_task_process} % 달성하셨습니다."
                    }
                ]
                },
            {
                "type": "divider"
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "모두 고생 많으셨어요! 👋",
                    "emoji": True}
            }
            ]
        }
    slack = WebClient(SLACK_TOKEN)
    if terminate == False:
        if a_task_process >= 100:
            slack.chat_postMessage(channel='', blocks=a_complete_block['blocks'])
        if b_task_process >= 100:
            slack.chat_postMessage(channel='', blocks=b_complete_block['blocks'])
    else:
        slack.chat_postMessage(channel='', blocks=closing_block['blocks'])
    return {'a':a_task_process,
            'b':b_task_process}
