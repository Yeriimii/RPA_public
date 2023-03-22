# -*- coding: utf-8 -*-
import os
import datetime
import pymysql
import pandas as pd
import json
import getpass
from dotenv import load_dotenv
from notion_client import Client

# read the '.env' file
username = getpass.getuser()
load_dotenv(f'../.env')

# 환경변수에서 NOTION_TOKEN 불러오기
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PW')
DB_NAME = os.getenv('DB_NAME')

# FIXME: NOTION은 database <- page <- block 으로 구성.
# Notion client 객체 생성
notion = Client(auth=NOTION_TOKEN)

# Notion 사용자 List 출력
# list_user_response = notion.users.list()

today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')

# 할당량
admin = {'b': 6105,
        'a': 4425}

def search_the_project_db(database_id: str) -> dict:
    # PROJECT DB의 데이터베이스에서 자동 생성된 검수 project의 page id 찾기
    project_db_pages:dict = notion.databases.query(
        **{
            'database_id': database_id,
            'filter': {
                'property': '프로젝트 명',
                'rich_text': {'starts_with': 'YYYY/MM/DD'}
                }
            }
        )
    # pprint(project_db_pages)  # properties 확인
    if len(project_db_pages['results']) == 0:
        raise Exception('YYYY/MM/DD 로 시작하는 페이지를 찾지 못했습니다.')
    else:
        return project_db_pages

def update_date_from_the_project_db(project_db_pages: dict) -> str:
    # PROJECT DB 내 'YYYY/MM/DD'로 시작하는 page 업데이트
    notion.pages.update(
        **{
            'page_id': project_db_pages['results'][0]['id'],
            'properties': {
                '프로젝트 명': {
                    'id': 'title',
                    'type': 'title',
                    'title': [{
                        'annotations': {'bold': False,
                                        'code': False,
                                        'color': 'default',
                                        'italic': False,
                                        'strikethrough': False,
                                        'underline': False},
                        'href': None,
                        'plain_text': f'{today}',
                        'text': {'content': f'{today}',
                                'link': None},
                        'type': 'text'}]
                    },
                '시작일': {
                    'id': project_db_pages['results'][0]['properties']['시작일']['id'],
                    'type': 'date',
                    'date': {'start': today}
                    },
                '종료일': {
                    'id': project_db_pages['results'][0]['properties']['종료일']['id'],
                    'type': 'date',
                    'date': {'start': today}
                    }
                }
            }
        )

    return project_db_pages['results'][0]['id']

def create_page_to_task_db(task_db_id: str, updated_page_id: str) -> list[str]:
    _response_0 = notion.pages.create(  # 첫 번째 담당자에게 할당하는 page properties
        **{
            'parent': {'database_id': task_db_id},
            'properties':{'담당자': {'id': '%5DFWG',
                                    'people': [{'avatar_url': None,
                                                'id': '',
                                                'name': 'a',
                                                'object': 'user',
                                                'person': {'email': ''},
                                                'type': 'person'}],
                                    'type': 'people'},
                        '세부 할 일': {'id': 'title',
                                    'type': 'title',
                                    'title': [{'annotations': {'bold': False,
                                                                'code': False,
                                                                'color': 'default',
                                                                'italic': False,
                                                                'strikethrough': False,
                                                                'underline': False},
                                                'href': None,
                                                'plain_text': f'{today} 데이터 검수',
                                                'text': {'content': f'{today} 데이터 검수',
                                                        'link': None},
                                                'type': 'text'}]},
                        '프로젝트': {'has_more': False,
                                    'id': '%7B_yi',
                                    'relation': [{'id': updated_page_id}],
                                    'type': 'relation'},
                        '마감일자': {'date': {'start': today},
                                    'id': 'lYwQ',
                                    'type': 'date'},
                    }
            }
        )

    _response_1 = notion.pages.create(  # 두 번째 담당자에게 할당하는 page properties
        **{
            'parent': {'database_id': task_db_id},
            'properties':{'담당자': {'id': '%5DFWG',
                                    'people': [{'avatar_url': '',
                                                'id': '47558ba6-cccb-4916-a87e-9100963a63ef',
                                                'name': 'b',
                                                'object': 'user',
                                                'person': {'email': ''},
                                                'type': 'person'}],
                                    'type': 'people'},
                        '세부 할 일': {'id': 'title',
                                    'type': 'title',
                                    'title': [{'annotations': {'bold': False,
                                                                'code': False,
                                                                'color': 'default',
                                                                'italic': False,
                                                                'strikethrough': False,
                                                                'underline': False},
                                                'href': None,
                                                'plain_text': f'{today} 데이터 검수',
                                                'text': {'content': f'{today} 데이터 검수',
                                                        'link': None},
                                                'type': 'text'}]},
                        '프로젝트': {'has_more': False,
                                    'id': '%7B_yi',
                                    'relation': [{'id': updated_page_id}],
                                    'type': 'relation'},
                        '마감일자': {'date': {'start': today},
                                    'id': 'lYwQ',
                                    'type': 'date'},
                    }
            }
        )

    return [_response_0['id'], _response_1['id']]

def create_database_to_task_page(task_pages_id: list[str]) -> list[str]:
    _response_0 = notion.databases.create(  # 첫 번째 담당자에게 할당된 page 내 database 스키마 생성
            **{
                'parent': {'page_id': task_pages_id[0],
                        'type': 'page_id'},
                'is_inline': True,
                'icon': {'emoji': '🔎', 'type': 'emoji'},
                'title': [{'type': 'text', 'text': {'content': '할당량', 'link': None}}],
                'properties': {
                                '대상': {'id': 'title',
                                        'title': {},
                                        'type': 'title'},
                                '수행량': {'number': {'format': 'number_with_commas'},  # 수행량
                                        'type': 'number',
                                        },
                                '할당량': {'number': {'format': 'number_with_commas'},  # 할당량
                                        'type': 'number',
                                        },
                                '진행률': {'formula': {'expression': 'divide(prop(\"수행량\"), prop(\"할당량\"))'},
                                        'type': 'formula'
                                        }
                                }
            }
        )

    _response_1 = notion.databases.create(  # 두 번째 담당자에게 할당된 page 내 database 스키마 생성
            **{
                'parent': {'page_id': task_pages_id[1],
                        'type': 'page_id'},
                'is_inline': True,
                'icon': {'emoji': '🔎', 'type': 'emoji'},
                'title': [{'type': 'text', 'text': {'content': '할당량', 'link': None}}],
                'properties': {
                                '대상': {'id': 'title',
                                        'title': {},
                                        'type': 'title'},
                                '수행량': {'number': {'format': 'number_with_commas'},  # 수행량
                                        'type': 'number',
                                        },
                                '할당량': {'number': {'format': 'number_with_commas'},  # 할당량
                                        'type': 'number',
                                        },
                                '진행률': {'formula': {'expression': 'divide(prop(\"수행량\"), prop(\"할당량\"))'},
                                        'type': 'formula'
                                        }
                                }
            }
        )

    return [_response_0['id'], _response_1['id']]  # 두 명에게 할당한 2개의 database_id

def assign_to_database(databases_id: list[str]) -> list[str]:
    conn = pymysql.connect(host=DB_HOST,
                            user=DB_USER,
                            password=DB_PW,
                            port=3306,
                            db=DB_NAME)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 오늘의 전체 할당량 테이블
    query = f"""
        SELECT
        FROM
        LIMIT 20000;
        """
    curs.execute(query)
    total_table = pd.DataFrame(curs.fetchall())
    total_table_header = list(total_table.columns)
    query_result = total_table.values.tolist()
    query_result.insert(0, total_table_header)
    curs.close()
    conn.close()

    if len(query_result[1:]) <= (admin['a'] * 2) and (len(query_result[1:]) != 0):
        b_assinged_task = int(round(len(query_result[1:]) * 0.5))
    else:
        b_assinged_task = len(query_result[(1 + admin['a']): (admin['a'] + admin['b'])])
    if len(query_result[1:]) <= (admin['a'] * 2) and (len(query_result[1:]) != 0):
        a_assinged_task = int(round(len(query_result[1:]) * 0.5))
    else:
        a_assinged_task = len(query_result[1:admin['a']])

    _response_0 = notion.pages.create(  # 첫 번째 담당자(a)에게 할당된 데이터베이스에 값 입력
        **{
            'parent': {'database_id': databases_id[0]},
            'properties': {
                '수행량': {'number': 0,
                        'type': 'number'},
                '할당량': {'number': a_assinged_task,
                        'type': 'number'}
                },
        }
    )

    _response_1 = notion.pages.create(  # 두 번째 담당자(b)에게 할당된 데이터베이스에 값 입력
        **{
            'parent': {'database_id': databases_id[1]},
            'properties': {
                '수행량': {'number': 0,
                        'type': 'number'},
                '할당량': {'number': b_assinged_task,
                        'type': 'number'}
                },
        }
    )

    data = {
            'database_id_0': {
                'database_id': databases_id[0],
                'child_page': _response_0['id']},
            'database_id_1': {
                'database_id': databases_id[1],
                'child_page': _response_1['id']}
            }

    with open(f'../{today}.json', 'w') as f:
        json.dump(data, f)

    return [_response_0['id'], _response_1['id']]
