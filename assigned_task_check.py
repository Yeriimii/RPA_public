# -*- coding: utf-8 -*-
import os
import time
import getpass
import datetime
from rpa.notion.config import (search_the_project_db, update_date_from_the_project_db,
                               create_page_to_task_db, create_database_to_task_page, assign_to_database)
from rpa.notion.page_check import assigned_task_check, send_message
from rpa.mysql.db_manage import *

os.chdir(f'')

if __name__ == '__main__':
    start_time = time.time()

    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%H:%M")
    current_hour = int(current_time.split(':')[0])
    current_minute = int(current_time.split(':')[1])

    print('current_time:', current_time)

    if current_hour == 15 and current_minute == 30:
        assigned_task_check()
        task_process_data = send_message(terminate=False)
        print(task_process_data)
    elif current_hour == 19 and current_minute <= 30:
        assigned_task_check()
        task_process_data = send_message(terminate=True)
        print(task_process_data)
    elif current_hour == 9 and current_minute <= 50:
        PROJECT_DB_ID = ''  # PROJECT DB ID는 변하지 않으므로, 상수 취급
        related_pages = search_the_project_db(PROJECT_DB_ID)  # '프로젝트 명' 속성에서 특정 페이지의 상세정보 출력
        updated_page_id = update_date_from_the_project_db(related_pages)  # '시작일'/'종료일' 을 오늘로 변경
        if updated_page_id:
            print('updated_page_id:', updated_page_id)
        TASK_DB_ID = ''  # TASK DB ID는 변하지 않으므로, 상수 취급
        task_pages_id = create_page_to_task_db(  # TASK DB 페이지에서 검수 할당을 위해 inline database 내 page 생성
            task_db_id=TASK_DB_ID,
            updated_page_id=updated_page_id
        )
        if updated_page_id:
            print('task_pages_id:', task_pages_id)
        databases_id = create_database_to_task_page(task_pages_id)  # 담당자들에게 할당된 페이지에 database 생성
        if databases_id:
            print('databases_id:', databases_id)
        responses_assign = assign_to_database(databases_id)  # 담당자들의 데이터베이스에 작업량 할당
        if responses_assign:
            print('responses_assign:', responses_assign)
    print(f'conduction time: {time.time() - start_time:.5f}')
