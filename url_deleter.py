# built-in module
import os
import time
import getpass

# third-party module
import pyautogui
import pandas as pd
from PIL import *
from PIL import ImageGrab
from functools import partial
from slack_sdk import WebClient
from dateutil.parser import parse
from dotenv import load_dotenv

# local module
from rpa.chrome_browser.custom_webdriver import *
from rpa.mysql.db_manage import select_dct_to_delete, update_system_report_date_from_dct
from utilities.pickle_util import get_data


class BaseReportObject():
    """
    이 클래스는 BaseReportObject라는 이름의 부모 클래스로, __init__() 메소드를 사용하여 Slack API와 웹 드라이버를 초기화합니다.

    #### __init__() 메소드에서는 다음과 같은 작업을 수행합니다:

    - getpass.getuser(): 현재 사용자 이름을 가져오는 함수 호출
    - load_dotenv(): .env 파일에서 환경 변수를 로드하는 함수 호출
    - os.getenv('SLACK_TOKEN'): SLACK_TOKEN 환경 변수 값을 가져오기 위해 os 모듈의 getenv() 함수 호출
    - WebClient(SLACK_TOKEN): Slack API에 대한 인증 토큰을 전달하여 Slack API와 연결
    - self.total_success_count = 0: 성공적으로 처리된 작업 수를 저장하는 변수 초기화
    - self.total_fail_count = 0: 실패한 작업 수를 저장하는 변수 초기화
    - CustomWebDriver.run_chrome(): TeamNode가 커스터마이징한 CustomWebDriver 클래스의 run_chrome() 메소드를 호출하여 크롬 웹 드라이버를 실행합니다.
    """
    def __init__(self):
        self.username = getpass.getuser()
        load_dotenv(f'../.env')
        SLACK_TOKEN = os.getenv('SLACK_TOKEN')
        self.slack = WebClient(SLACK_TOKEN)
        self.total_success_count = 0
        self.total_fail_count = 0
        self.driver = CustomWebDriver.run_chrome()


class YoutubeReport(BaseReportObject):
    """
    _summary_

    _extended_summary_
    """
    def __init__(self):
        super().__init__()
        self.dmca_information = get_data(filename='')
        self.dmca_url = ""

    def input_infringing_copyright_work(self, c_id:int, copyright_work_title:str, infringing_url: str):
        """
        _summary_

        _extended_summary_

        Args:
            c_id (int): _description_
            copyright_work_title (str): _description_
            infringing_url (str): _description_

        Raises:
            Exception: _description_
        """
        choose_content_type_dropdown = self.driver.find_element(By.XPATH, '//*[@id="trigger"]/ytcp-dropdown-trigger/div/div[2]/div').click()  # 콘텐츠 유형 드롭다운 메뉴 클릭
        choose_etc = self.driver.find_element(By.XPATH, '//*[@id="text-item-6"]').click()  # 콘텐츠 유형에서 '기타' 선택
        choose_types_of_copyrighted_works = self.driver.find_element(By.XPATH, '//*[@id="otherIssue"]/div/textarea')  # 저작권 보호 작품 유형 입력칸
        choose_types_of_copyrighted_works.clear()  # 라벨 값 지우기
        choose_types_of_copyrighted_works.send_keys(self.dmca_information[c_id]['type'])  # 저작권 보호 작품 유형 입력칸에 '동영상' 입력
        choose_title_of_copyright_protection_works = self.driver.find_element(By.XPATH, '//*[@id="title"]/div/textarea')  # 저작권 보호 작품 제목 입력칸
        choose_title_of_copyright_protection_works.clear()
        choose_title_of_copyright_protection_works.send_keys(copyright_work_title)  # 저작권 보호 작품 제목 입력
        choose_additional_information = self.driver.find_element(By.XPATH, '//*[@id="description"]/div/textarea')  # 추가 정보 입력칸
        choose_additional_information.clear()
        if len(self.dmca_information[c_id]['additional_information_1'] + ' ' + f'<{copyright_work_title}>' + self.dmca_information[c_id]['additional_information_2']) >= 200:
            raise Exception('글자 수가 200 자를 초과합니다.')
        choose_additional_information.send_keys(self.dmca_information[c_id]['additional_information_1'] + ' ' + f'<{copyright_work_title}>' + self.dmca_information[c_id]['additional_information_2'])  # 추가 정보 입력칸에 추가 정보 입력
        choose_youTube_url = self.driver.find_element(By.XPATH, '//*[@id="targetVideo"]/div/textarea')  # 삭제할 영상 URL 입력칸
        choose_youTube_url.clear()
        choose_youTube_url.send_keys(infringing_url)  # 삭제할 영상 URL 입력칸에 삭제할 YouTube URL 입력

        try:
            already_delete = self.driver.find_element(By.XPATH, '//*[@id="new-entry-form"]/div[6]/div[2]/ytcr-video-details/div/div[2]').text
            if already_delete == '미리보기를 사용할 수 없음':
                cancel = self.driver.find_element(By.XPATH, '//*[@id="cancel-button"]')
                cancel.click()
                cancel = self.driver.find_element(By.XPATH, '/html/body/ytcp-confirmation-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div[2]/ytcp-button[2]')
                cancel.click()

                return False
        except NoSuchElementException as e:
            cancel = self.driver.find_element(By.XPATH, '//*[@id="cancel-button"]')
            cancel.click()
            cancel = self.driver.find_element(By.XPATH, '/html/body/ytcp-confirmation-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div[2]/ytcp-button[2]')
            cancel.click()

            return False

        choose_location_of_compromised_content_dropdown = self.driver.find_element(By.XPATH, '//*[@id="new-entry-form"]/div[7]/div').click()  # 침해한 콘텐츠의 위치 드롭다운 버튼 클릭
        time.sleep(2)
        choose_full_video = self.driver.find_element(By.XPATH, '//*[@id="html-body"]/ytcp-text-menu[2]/tp-yt-paper-dialog/tp-yt-paper-listbox/tp-yt-paper-item[1]').click()  # 침해한 콘텐츠의 위치 목록에서 '전체 동영상' 클릭
        time.sleep(2)
        choose_add_to_list = self.driver.find_element(By.XPATH, '//*[@id="save-button"]').click()  # 목록에 추가 버튼 클릭
        time.sleep(2)

        return True

    def input_common_informaton(self, c_id:int):
        """
        _summary_

        _extended_summary_

        Args:
            c_id (int): _description_
        """
        copyright_holder_dropdown_box = self.driver.find_element(By.XPATH, '//*[@id="contact-info-section"]/div[2]/div[1]/ytcp-form-select/ytcp-select')  # 영향을 받는 대상 드롭다운 메뉴
        copyright_holder_dropdown_box.click()
        copyright_holder_item = self.driver.find_element(By.XPATH, '//*[@id="text-item-1"]').click()  # 영향을 받는 대상 목록에서 '본인' 클릭
        copyright_holder_input_box = self.driver.find_element(By.XPATH, '//*[@id="claimant-name"]/div/textarea')  # 저작권 소유자 이름(필수 항목) 입력칸
        copyright_holder_input_box.clear()
        copyright_holder_input_box.send_keys(self.dmca_information[c_id]['copyright_owner'])  # 저작권 소유자 이름 입력칸에 저작권 소유자 입력
        phone_number_input_box = self.driver.find_element(By.XPATH, '//*[@id="phone"]/div/textarea')  # 전화번호(필수항목) 입력칸
        phone_number_input_box.clear()
        phone_number_input_box.send_keys(self.dmca_information['common_information']['phone_number'])  # 전화번호(필수 항목) 입력칸에 전화번호 입력
        sub_email_address_input_box = self.driver.find_element(By.XPATH, '//*[@id="secondary-email"]/div/textarea')  # 기본 이메일 주소(필수 항목) 입력칸
        sub_email_address_input_box.clear()
        sub_email_address_input_box.send_keys(self.dmca_information['common_information']['sub_email'])  # 기본 이메일 주소(필수 항목) 입력칸에 보조 이메일 주소 입력
        copyright_relationship_input_box = self.driver.find_element(By.XPATH, '//*[@id="requester-authority"]/div/textarea')  # 저작권 보호 콘텐츠와의 관계(필수항목) 입력칸
        copyright_relationship_input_box.clear()
        copyright_relationship_input_box.send_keys(self.dmca_information['common_information']['relationship'])  # 저작권 보호 콘텐츠와의 관계(필수 항목) 입력칸에 '모니터링팀' 입력
        country_dropdown_box = self.driver.find_element(By.XPATH, '//*[@id="country-select"]/ytcp-select').click()  # 국가(필수 항목) 드롭다운 메뉴 클릭
        country_dropdown_box_item = self.driver.find_element(By.XPATH, '//*[@id="text-item-30"]').click()  # 국가(필수 항목) 드롭다운 목록에서 한국 클릭
        detail_address_input_box = self.driver.find_element(By.XPATH, '//*[@id="street-address"]/div/textarea')  # 상세 주소(필수 항목) 입력칸
        detail_address_input_box.clear()
        detail_address_input_box.send_keys(self.dmca_information['common_information']['detail_address'])  # 상세 주소(필수 항목) 입력칸에 상세주소 입력
        district_address_input_box = self.driver.find_element(By.XPATH, '//*[@id="city"]/div/textarea')  # 구/군(필수 항목) 입력칸
        district_address_input_box.clear()
        district_address_input_box.send_keys(self.dmca_information['common_information']['district'])  # 구/군(필수 항목) 입력칸에 주소 입력
        city_address_input_box = self.driver.find_element(By.XPATH, '//*[@id="state"]/div/textarea')  # 시/도(필수 항목) 입력칸
        city_address_input_box.clear()
        city_address_input_box.send_keys(self.dmca_information['common_information']['city'])  # 시/도(필수 항목) 입력칸에 도시 입력
        postal_code_input_box = self.driver.find_element(By.XPATH, '//*[@id="zip"]/div/textarea')  # 우편번호(필수 항목) 입력칸
        postal_code_input_box.clear()
        postal_code_input_box.send_keys(self.dmca_information['common_information']['postal_code'])  # 우편번호(필수 항목) 입력칸에 우편번호 입력

        delete_option_1 = self.driver.find_element(By.XPATH, '//*[@id="immediate-takedown-radio-button"]').click()  # 3. 삭제 옵션 - 일반: 지금 삭제 요청 라디오 박스 버튼 클릭
        delete_option_2 = self.driver.find_element(By.XPATH, '//*[@id="tdsd-option-checkbox"]').click()  # 3. 삭제 옵션 - 앞으로 이 동영상의 사본이 YouTube에 표시되지 않도록 방지 클릭
        time.sleep(0.5)
        delete_option_3 = self.driver.find_element(By.XPATH, '//*[@id="tdsd-guidelines-checkbox"]/ytcp-checkbox-lit').click()  # 3. 삭제 옵션 - 본인은 삭제를 요청하는 콘텐츠에 대한~ 클릭

        legal_condition_1 = self.driver.find_element(By.XPATH, '//*[@id="checkbox-1"]/ytcp-checkbox-lit').click()  # 4. 법률 약관 첫 번째 박스 클릭
        legal_condition_2 = self.driver.find_element(By.XPATH, '//*[@id="checkbox-2"]/ytcp-checkbox-lit').click()  # 4. 법률 약관 두 번째 박스 클릭
        legal_condition_3 = self.driver.find_element(By.XPATH, '//*[@id="checkbox-3"]/ytcp-checkbox-lit').click()  # 4. 법률 약관 세 번째 박스 클릭

        signature_input_box = self.driver.find_element(By.XPATH, '//*[@id="signature"]/div/textarea')  # 서명(필수 항목) 입력칸
        signature_input_box.clear()
        signature_input_box.send_keys(self.dmca_information['common_information']['signature'])  # 서명(필수 항목) 입력칸에 서명 입력

    def pass_capcha(self):
        """
        ### [제출] 버튼 element를 클릭한 후 생성되는 capcha를 통과하는 함수.

        PIL library의 ImageGrab 클래스를 사용하며,
        1. capcha 안의 '로봇이 아닙니다.'에 해당하는 "체크박스 jpg"의 bbox 좌표(x,y) 를 찾는다.
        2. bbox 좌표의 중앙 (x/2, y/2) 위치에 마우스를 이동 및 클릭한다.

        Returns:
            bool: capcha 처리 여부를 bool 타입으로 리턴한다.
        """
        try:
            # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'⏳[알림] 캡챠를 처리 중입니다.')
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
            capcha_box = pyautogui.locateCenterOnScreen(image=f'C:/Users/{self.username}/Documents/GitHub/pic-devops/images/capcha_image/yt_capcha_box.jpg', minSearchTime=5.0, confidence=0.7)
            if capcha_box is None:
                # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'👎[알림] 캡챠 처리에 실패했습니다.\n이미지를 찾지 못했습니다.')
                return False
            else:
                pyautogui.click(capcha_box)
                # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'✅[알림] 캡챠 처리에 성공했습니다.')
                return True
        except Exception as e:
            print(f'{e}')
            # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'👎[알림] 캡챠 처리에 실패했습니다.\n에러 메세지는 다음과 같습니다.\n{e}')
            return False

    def new_delete_request(self, xpath='//*[@id="new-removal-button"]/div'):
        """
        ### [새로운 삭제 요청] 버튼 element를 클릭하는 함수

        YouTube Studio 저작권 관리탭 안의 [새로운 삭제 요청] 버튼을 클릭

        Args:
            xpath (str, optional): [새로운 삭제 요청] 버튼 element의 XPATH. Defaults to '//*[@id="submit-button"]/div'.
        """
        self.driver.find_element(By.XPATH, xpath).click()
    def submit(self, xpath='//*[@id="submit-button"]/div'):
        """
        ### [제출] 버튼 element를 클릭하는 함수

        YouTube 저작권 신고서 안의 [제출] 버튼을 클릭

        Args:
            xpath (str, optional): [제출] 버튼 element의 XPATH. Defaults to '//*[@id="submit-button"]/div'.
        """
        self.driver.find_element(By.XPATH, xpath).click()  # 제출 버튼 클릭
        # already_request = WebDriverWait(self.driver, 3).until_not(EC.visibility_of_element_located((By.XPATH, '//div[contains(text(), "이미 제출")]')))

    def add_video(self, xpath='//*[@id="add-new-entry"]/div'):
        """
        ### [동영상 추가] 버튼 element를 클릭하는 함수

        YouTube 저작권 신고서 안의 [동영상 추가] 버튼을 클릭

        Args:
            xpath (str, optional): [동영상 추가] 버튼 element의 XPATH. Defaults to '//*[@id="add-new-entry"]/div'.
        """
        self.driver.find_element(By.XPATH, xpath).click()  # 동영상 추가 버튼 클릭

    def close_report_window(self, xpath='//*[@id="close-icon"]'):
        self.driver.find_element(By.XPATH, xpath).click()  # 동영상 추가 버튼 클릭

    def run(self, df: pd.DataFrame):
        """
        이 메소드는 객체 지향 프로그래밍을 사용하여 작성된 메소드로, self 파라미터를 통해 클래스 내부 변수 및 메소드에 접근할 수 있습니다.

        이 메소드는 pd.DataFrame 형식의 데이터프레임을 파라미터로 받으며, 각각의 고객(c_id)과 해당 고객이 등록한 작품(monitoring_title)을 그룹핑하여 작업 리스트를 생성합니다.
        이후 작업 리스트를 반복하면서, 해당 작품의 각 URL을 포함하는 저작권 침해 신고서를 생성합니다.

        Args:
            df (pd.DataFrame): D.ct_id, S.c_id, D.p_id, T.monitoring_title, D.url 을 컬럼 헤더로 갖는 데이터프레임을 파라미터로 받습니다.

        Returns:
            dict: 함수가 종료될 때, 총 신고서 작성에 성공하거나 실패한 게시물의 개수를 dictionary 형태로 반환합니다.
        """
        self.driver.get(self.dmca_url)  # 유튜브 스튜디오 접속
        self.driver.implicitly_wait(10)
        time.sleep(5)

        each_client_work = dict(list(df.groupby(['c_id'])))
        each_title_work = [(c_id, list(each_client_work[c_id].groupby(['monitoring_title'])['ct_id', 'url'])) for c_id in each_client_work.keys()]
        work_list:list[tuple[int, str, list]] = [(c_id, title, ctid_url_list.reset_index(drop=True).values.tolist()) for c_id, title_and_url_list in each_title_work for title, ctid_url_list in title_and_url_list]
        for c_id, copyright_work_title, ctid_url_list in work_list:
            report_success_urls_ctid:list[str] = []
            report_failed_urls_ctid:list[str] = []
            self.new_delete_request()
            time.sleep(1.5)
            for report_cnt, ctid_url in enumerate(ctid_url_list, 1):
                if (report_cnt % 10) == 0:
                    self.input_common_informaton(c_id)
                    time.sleep(1.5)
                    self.submit()
                    time.sleep(1.5)
                    is_pass = self.pass_capcha()
                    if is_pass != True:
                        raise Exception('capcha pass error')
                    time.sleep(1.5)
                    self.new_delete_request()
                    time.sleep(1.5)
                self.add_video()
                time.sleep(1.5)
                is_reportable = self.input_infringing_copyright_work(c_id, copyright_work_title, ctid_url[1])
                if is_reportable == True:
                    report_success_urls_ctid.append(ctid_url[0])
                else:
                    report_failed_urls_ctid.append(ctid_url[0])
                    continue
            else:
                if len(report_success_urls_ctid) == 0:  # 아무것도 신고하지 못할 때
                    # 이미 삭제된 영상일 경우 --> system_report_yn = 1, del_yn = 1 처리
                    self.close_report_window()
                    time.sleep(1.5)
                    failed_update_count = update_system_report_date_from_dct(report_failed_urls_ctid, report_success=False)
                    self.total_fail_count += failed_update_count
                    continue
                self.input_common_informaton(c_id)
                time.sleep(1.5)
                self.submit()
                time.sleep(1.5)
                is_pass = self.pass_capcha()
                if is_pass != True:
                    raise Exception('capcha pass error')
                time.sleep(1.5)
                success_update_count = update_system_report_date_from_dct(report_success_urls_ctid)
                self.total_success_count += success_update_count
                failed_update_count = update_system_report_date_from_dct(report_failed_urls_ctid, report_success=False)
                self.total_fail_count += failed_update_count
            time.sleep(2)

        self.driver.close()

        return {'total_success': self.total_success_count, 'total_fail': self.total_fail_count}


class FacebookReport(BaseReportObject):
    def __init__(self):
        super().__init__()
        self.dmca_information = get_data(filename='')
        self.dmca_url = ""

    def click_reporter_option(self, xpath='//*[@id="SupportFormRow.250116565117827"]/div[3]/label[1]/span'):
        self.driver.find_element(By.XPATH, xpath).click()

    def click_report_type(self, xpath='//*[@id="1076937109041279.0"]/following-sibling::span'):
        self.driver.find_element(By.XPATH, xpath).click()

    def input_infringing_copyright_work(self, c_id: int, copyright_work_title: str, infringing_url: str):
        report_description = self.driver.find_element(By.XPATH, '//*[@id="451242651624945"]')  # 신고 내용
        report_description.send_keys(self.dmca_information[c_id]['additional_information_1'] + ' ' + f'<{copyright_work_title}>\n' + self.dmca_information[c_id]['additional_information_2'])
        delete_urls = self.driver.find_element(By.XPATH, '//*[@id="388149281267730"]')
        delete_urls.send_keys(infringing_url)

    def input_common_informaton(self, c_id:int):
        your_name = self.driver.find_element(By.XPATH, '//*[@id="474274485979849"]')  # 이름 element
        your_name.send_keys(self.dmca_information['common_information']['your_name'])
        address = self.driver.find_element(By.XPATH, '//*[@id="364697220303015"]')  # 우편주소 element
        address.send_keys(self.dmca_information['common_information']['address'])
        email = self.driver.find_element(By.XPATH, '//*[@id="244971059275452"]')  # 이메일 주소 element
        email.send_keys(self.dmca_information['common_information']['email'])
        email_reconfirm = self.driver.find_element(By.XPATH, '//*[@id="755605467935533"]')  # 이메일 주소 재확인 element
        email_reconfirm.send_keys(self.dmca_information['common_information']['email'])
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="2411416902487298"]')) # 권리자의 본사: select 태그의 XPATH로 요소를 찾음
        select.select_by_value('South Korea') # option 중 '대한민국'을 선택
        copyright_owner = self.driver.find_element(By.XPATH, '//*[@id="1467491100178767"]')  # 권리 소유자 이름
        copyright_owner.send_keys(self.dmca_information[c_id]['copyright_owner'])
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="418475341579315"]')) # 저작물 설명: select 태그
        select.select_by_value('Video') # option 중 '동영상'을 선택
        self.click_report_type()  # '사진, 동영상 또는 게시물' 옵션 선택
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="136284146523176"]')) # 신고하려는 이유: select 태그
        select.select_by_value('This content copies my work') # option 중 '동영상'을 선택
        upload_btn = self.driver.find_element(By.XPATH, '//*[@id="381648032194738"]/input')  # 첨부 파일: 개수 만큼 반복
        upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/common/Business_Registration.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
        wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="381648032194738"]/input')))
        upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/poa/client/{c_id}/POA.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
        wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="381648032194738"]/input')))
        if (c_id == 1) or (c_id == 4):
            upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/poa/client/{c_id}/POA_Appendix.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
            wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="381648032194738"]/input')))
        signature = self.driver.find_element(By.XPATH, '//*[@id="159694930852744"]')  # 전자 서명
        signature.send_keys(self.dmca_information['common_information']['signature'])

    def submit(self):
        submit_btn = self.driver.find_element(By.XPATH, '//button[contains(text(), "제출")]')
        if submit_btn.text == '제출':
            submit_btn.click()
            time.sleep(1.5)
            while True:
                is_pass = self.pass_capcha()
                if is_pass != True:
                    raise Exception('capcha pass error')
                submit_btn_2 = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="captcha_dialog_submit_button"]')))
                submit_btn_2.click()
                confirm_btn = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="facebook"]/body/div[2]/div[2]/div/div/div/div[3]/div/a')))
                if confirm_btn.text != '취소':
                    break
            confirm_btn.click()
        else:
            raise Exception('제출 버튼 element xpath 에러')

    def pass_capcha(self):
        """
        ### [제출] 버튼 element를 클릭한 후 생성되는 capcha를 통과하는 함수.

        PIL library의 ImageGrab 클래스를 사용하며,
        1. capcha 안의 '로봇이 아닙니다.'에 해당하는 "체크박스 jpg"의 bbox 좌표(x,y) 를 찾는다.
        2. bbox 좌표의 중앙 (x/2, y/2) 위치에 마우스를 이동 및 클릭한다.

        Returns:
            bool: capcha 처리 여부를 bool 타입으로 리턴한다.
        """
        try:
            # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'⏳[알림] 캡챠를 처리 중입니다.')
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
            capcha_box = pyautogui.locateCenterOnScreen(image=f'C:/Users/{self.username}/Documents/GitHub/pic-devops/images/capcha_image/yt_capcha_box.jpg', minSearchTime=5.0, confidence=0.7)
            if capcha_box is None:
                # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'👎[알림] 캡챠 처리에 실패했습니다.\n이미지를 찾지 못했습니다.')
                return False
            else:
                pyautogui.click(capcha_box)
                # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'✅[알림] 캡챠 처리에 성공했습니다.')
                return True
        except Exception as e:
            print(f'{e}')
            # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'👎[알림] 캡챠 처리에 실패했습니다.\n에러 메세지는 다음과 같습니다.\n{e}')
            return False

    def run(self, df: pd.DataFrame):
        """
        이 메소드는 객체 지향 프로그래밍을 사용하여 작성된 메소드로, self 파라미터를 통해 클래스 내부 변수 및 메소드에 접근할 수 있습니다.

        이 메소드는 pd.DataFrame 형식의 데이터프레임을 파라미터로 받으며, 각각의 고객(c_id)과 해당 고객이 등록한 작품(monitoring_title)을 그룹핑하여 작업 리스트를 생성합니다.
        이후 작업 리스트를 반복하면서, 해당 작품의 각 URL을 포함하는 저작권 침해 신고서를 생성합니다.

        Args:
            df (pd.DataFrame): D.ct_id, S.c_id, D.p_id, T.monitoring_title, D.url 을 컬럼 헤더로 갖는 데이터프레임을 파라미터로 받습니다.

        Returns:
            dict: 함수가 종료될 때, 총 신고서 작성에 성공하거나 실패한 게시물의 개수를 dictionary 형태로 반환합니다.
        """
        each_client_work = dict(list(df.groupby(['c_id'])))
        each_title_work = [(c_id, list(each_client_work[c_id].groupby(['monitoring_title'])['ct_id', 'url'])) for c_id in each_client_work.keys()]
        work_list:list[tuple[int, str, list]] = [(c_id, title, ctid_url_list.reset_index(drop=True).values.tolist()) for c_id, title_and_url_list in each_title_work for title, ctid_url_list in title_and_url_list]
        report_url_list:list[str] = []
        requested_urls_ctid:list[str] = []
        for c_id, copyright_work_title, ctid_url_list in work_list:
            list(map(lambda x: report_url_list.append(x[1]), ctid_url_list))
            self.driver.get(self.dmca_url)
            time.sleep(5)
            self.click_reporter_option()
            time.sleep(1.5)
            self.input_common_informaton(c_id)
            time.sleep(1.5)
            report_urls:str = "\n".join(report_url_list)
            self.input_infringing_copyright_work(c_id, copyright_work_title, report_urls)
            time.sleep(1.5)
            self.submit()
            time.sleep(1.5)
            list(map(lambda x: requested_urls_ctid.append(x[0]), ctid_url_list))
            update_count = update_system_report_date_from_dct(requested_urls_ctid)
            self.total_success_count += update_count

        self.driver.close()

        return {'total_success': self.total_success_count, 'total_fail': self.total_fail_count}


class InstagramReport(BaseReportObject):
    def __init__(self):
        super().__init__()
        self.dmca_information = get_data(filename='')
        self.dmca_url = ""

    def click_reporter_option(self, xpath='//*[@id="SupportFormRow.250116565117827"]/div[3]/label[1]/span'):
        self.driver.find_element(By.XPATH, xpath).click()

    def click_report_type(self, xpath='//input[@value="Photo, video or post"]/following-sibling::span'):
        self.driver.find_element(By.XPATH, xpath).click()

    def input_infringing_copyright_work(self, c_id: int, copyright_work_title: str, infringing_url: str):
        report_description = self.driver.find_element(By.XPATH, '//*[@id="451242651624945"]')  # 신고 내용
        report_description.send_keys(self.dmca_information[c_id]['additional_information_1'] + ' ' + f'<{copyright_work_title}>\n' + self.dmca_information[c_id]['additional_information_2'])
        delete_urls = self.driver.find_element(By.XPATH, '//*[@id="388149281267730"]')
        delete_urls.send_keys(infringing_url)

    def input_common_informaton(self, c_id:int):
        your_name = self.driver.find_element(By.XPATH, '//*[@id="474274485979849"]')  # 이름 element
        your_name.send_keys(self.dmca_information['common_information']['your_name'])
        address = self.driver.find_element(By.XPATH, '//*[@id="364697220303015"]')  # 우편주소 element
        address.send_keys(self.dmca_information['common_information']['address'])
        email = self.driver.find_element(By.XPATH, '//*[@id="367587743601218"]')  # 이메일 주소 element
        email.send_keys(self.dmca_information['common_information']['email'])
        email_reconfirm = self.driver.find_element(By.XPATH, '//*[@id="254868214933490"]')  # 이메일 주소 재확인 element
        email_reconfirm.send_keys(self.dmca_information['common_information']['email'])
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="2468492400123843"]')) # 권리자의 본사: select 태그의 XPATH로 요소를 찾음
        select.select_by_value('South Korea') # option 중 '대한민국'을 선택
        copyright_owner = self.driver.find_element(By.XPATH, '//*[@id="1467491100178767"]')  # 권리 소유자 이름
        copyright_owner.send_keys(self.dmca_information[c_id]['copyright_owner'])
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="418475341579315"]')) # 저작물 설명: select 태그
        select.select_by_value('Video') # option 중 '동영상'을 선택
        self.click_report_type()  # '사진, 동영상 또는 게시물' 옵션 선택
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="136284146523176"]')) # 신고하려는 이유: select 태그
        select.select_by_value('This content copies my work') # option 중 '동영상'을 선택
        upload_btn = self.driver.find_element(By.XPATH, '//*[@id="175836572908296"]/input')  # 첨부 파일: 개수 만큼 반복
        upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/common/Business_Registration.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
        wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="175836572908296"]/input')))
        upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/poa/client/{c_id}/POA.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
        wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="175836572908296"]/input')))
        if (c_id == 1) or (c_id == 4):
            upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/poa/client/{c_id}/POA_Appendix.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
            wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="175836572908296"]/input')))
        signature = self.driver.find_element(By.XPATH, '//*[@id="159694930852744"]')  # 전자 서명
        signature.send_keys(self.dmca_information['common_information']['signature'])

    def submit(self):
        submit_btn = self.driver.find_element(By.XPATH, '//button[contains(text(), "보내기")]')
        if submit_btn.text == '보내기':
            submit_btn.click()
        else:
            raise Exception('보내기 버튼 element xpath 에러')
        time.sleep(1.5)
        is_pass = self.pass_capcha()
        if is_pass != True:
            raise Exception('capcha pass error')
        submit_btn_2 = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="captcha_dialog_submit_button"]')))
        submit_btn_2.click()
        confirm_btn = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="facebook"]/body/div[2]/div[2]/div/div/div/div[3]/div/a')))
        confirm_btn.click()

    def pass_capcha(self):
        """
        ### [제출] 버튼 element를 클릭한 후 생성되는 capcha를 통과하는 함수.

        PIL library의 ImageGrab 클래스를 사용하며,
        1. capcha 안의 '로봇이 아닙니다.'에 해당하는 "체크박스 jpg"의 bbox 좌표(x,y) 를 찾는다.
        2. bbox 좌표의 중앙 (x/2, y/2) 위치에 마우스를 이동 및 클릭한다.

        Returns:
            bool: capcha 처리 여부를 bool 타입으로 리턴한다.
        """
        try:
            # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'⏳[알림] 캡챠를 처리 중입니다.')
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
            capcha_box = pyautogui.locateCenterOnScreen(image=f'C:/Users/{self.username}/Documents/GitHub/pic-devops/images/capcha_image/yt_capcha_box.jpg', minSearchTime=5.0, confidence=0.7)
            if capcha_box is None:
                # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'👎[알림] 캡챠 처리에 실패했습니다.\n이미지를 찾지 못했습니다.')
                return False
            else:
                pyautogui.click(capcha_box)
                # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'✅[알림] 캡챠 처리에 성공했습니다.')
                return True
        except Exception as e:
            print(f'{e}')
            # self.slack.post_thread_message(channel_id='C049QR40YES', text=f'👎[알림] 캡챠 처리에 실패했습니다.\n에러 메세지는 다음과 같습니다.\n{e}')
            return False

    def run(self, df: pd.DataFrame):
        """
        이 메소드는 객체 지향 프로그래밍을 사용하여 작성된 메소드로, self 파라미터를 통해 클래스 내부 변수 및 메소드에 접근할 수 있습니다.

        이 메소드는 pd.DataFrame 형식의 데이터프레임을 파라미터로 받으며, 각각의 고객(c_id)과 해당 고객이 등록한 작품(monitoring_title)을 그룹핑하여 작업 리스트를 생성합니다.
        이후 작업 리스트를 반복하면서, 해당 작품의 각 URL을 포함하는 저작권 침해 신고서를 생성합니다.

        Args:
            df (pd.DataFrame): D.ct_id, S.c_id, D.p_id, T.monitoring_title, D.url 을 컬럼 헤더로 갖는 데이터프레임을 파라미터로 받습니다.

        Returns:
            dict: 함수가 종료될 때, 총 신고서 작성에 성공하거나 실패한 게시물의 개수를 dictionary 형태로 반환합니다.
        """
        each_client_work = dict(list(df.groupby(['c_id'])))
        each_title_work = [(c_id, list(each_client_work[c_id].groupby(['monitoring_title'])['ct_id', 'url'])) for c_id in each_client_work.keys()]
        work_list:list[tuple[int, str, list]] = [(c_id, title, ctid_url_list.reset_index(drop=True).values.tolist()) for c_id, title_and_url_list in each_title_work for title, ctid_url_list in title_and_url_list]
        report_url_list:list[str] = []
        requested_urls_ctid:list[str] = []
        for c_id, copyright_work_title, ctid_url_list in work_list:
            list(map(lambda x: report_url_list.append(x[1]), ctid_url_list))
            self.driver.get(self.dmca_url)
            time.sleep(5)
            self.click_reporter_option()
            time.sleep(1.5)
            self.input_common_informaton(c_id)
            time.sleep(1.5)
            report_urls:str = "\n".join(report_url_list)
            self.input_infringing_copyright_work(c_id, copyright_work_title, report_urls)
            time.sleep(1.5)
            self.submit()
            time.sleep(1.5)
            list(map(lambda x: requested_urls_ctid.append(x[0]), ctid_url_list))
            update_count = update_system_report_date_from_dct(requested_urls_ctid)
            self.total_success_count += update_count

        self.driver.close()

        return {'total_success': self.total_success_count, 'total_fail': self.total_fail_count}


class TiktokReport(BaseReportObject):
    def __init__(self):
        super().__init__()
        self.dmca_information = get_data(filename='')
        self.dmca_url = ""

    def confirm_email(self, email_xpath='//*[@id="main"]/div[2]/div[2]/main/article/div/div/div/input',
                            next_btn_xpath='//*[@id="main"]/div[2]/div[2]/main/article/div/button'):
        input_email = self.driver.find_element(By.XPATH, email_xpath)
        input_email.send_keys(self.dmca_information['common_information']['email'])
        next_btn = self.driver.find_element(By.XPATH, next_btn_xpath)
        next_btn.click()

    def input_common_informaton(self, c_id:int):
        your_name = self.driver.find_element(By.XPATH, '//*[@id="name"]/div/input')  # 이름 element
        your_name.send_keys(self.dmca_information['common_information']['your_name'])
        copyright_owner = self.driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[2]/main/article/div/form/div[2]/div/input')  # 권리 소유자 이름
        copyright_owner.send_keys(self.dmca_information[c_id]['copyright_owner'])
        address = self.driver.find_element(By.XPATH, '//*[@id="address"]/div/input')  # 우편주소 element
        address.send_keys(self.dmca_information['common_information']['address'])
        phone_number = self.driver.find_element(By.XPATH, '//*[@id="phoneNumber"]/div/input')  # 전화번호 element
        phone_number.send_keys(self.dmca_information['common_information']['phone_number'])
        relationship = self.driver.find_element(By.XPATH, '//*[@id="relationship"]/div[4]/label')
        relationship.click()  # '본인은 저작권 소유자의 인증된 대리인입니다.' 선택
        content_type = self.driver.find_element(By.XPATH, '//*[@id="typeCopyRight"]/div[1]/label')
        content_type.click()  # 저작물 유형: 동영상 선택
        upload_btn = self.driver.find_element(By.XPATH, '//*[@id="input-file-authorizations"]')  # 첨부 파일: 개수 만큼 반복
        upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/common/Business_Registration.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
        wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="input-file-authorizations"]')))
        upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/poa/client/{c_id}/POA.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
        wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="input-file-authorizations"]')))
        if (c_id == 1) or (c_id == 4):
            upload_btn.send_keys(f"C:/Users/{self.username}/Documents/GitHub/pic-devops/images/poa/client/{c_id}/POA_Appendix.pdf")  # 이미지 경로: jpg, gif, png, tiff, pdf 형식만 지원
            wait_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="input-file-authorizations"]')))
        legal_condition_1 = self.driver.find_element(By.XPATH, '//*[@id="Statement"]/div[1]/label')
        legal_condition_1.click()  # 해당 진술:1 선택
        legal_condition_2 = self.driver.find_element(By.XPATH, '//*[@id="Statement"]/div[2]/label')
        legal_condition_2.click()  # 해당 진술:2 선택
        legal_condition_3 = self.driver.find_element(By.XPATH, '//*[@id="Statement"]/div[3]/label')
        legal_condition_3.click()  # 해당 진술:3 선택
        signature = self.driver.find_element(By.XPATH, '//*[@id="signature"]/div/input')  # 전자 서명
        signature.send_keys(self.dmca_information['common_information']['signature'])

    def input_infringing_copyright_work(self, c_id: int, copyright_work_title: str, infringing_url: str):
        report_description = self.driver.find_element(By.XPATH, '//*[@id="descOfWork"]/div/input')  # 저작물에 대한 설명(신고 내용)
        report_description.send_keys(self.dmca_information[c_id]['additional_information_1'] + ' ' + f'<{copyright_work_title}>\n' + self.dmca_information[c_id]['additional_information_2'])
        delete_urls = self.driver.find_element(By.XPATH, '//*[@id="link"]/textarea')
        delete_urls.send_keys(infringing_url)
        personal_account_btn = self.driver.find_element(By.XPATH, '//*[@id="personalAccount"]/div[2]/label/span')  # 개인 tiktok 계정 -> 아니오
        personal_account_btn.click()
        copyright_work_type = self.driver.find_element(By.XPATH, '//*[@id="typeCopyRight"]/div[1]/label/span')  # 저작물 유형 -> 동영상
        copyright_work_type.click()

    def submit(self):
        submit_btn = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[2]/main/article/div/button')
        if submit_btn.text == '보내기':
            submit_btn.click()
        else:
            raise Exception('제출 버튼 element xpath 에러')
        confirm_btn = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[2]/div[2]/main/article/div/div/button')))
        confirm_btn.click()

    def run(self, df: pd.DataFrame):
        """
        이 메소드는 객체 지향 프로그래밍을 사용하여 작성된 메소드로, self 파라미터를 통해 클래스 내부 변수 및 메소드에 접근할 수 있습니다.

        이 메소드는 pd.DataFrame 형식의 데이터프레임을 파라미터로 받으며, 각각의 고객(c_id)과 해당 고객이 등록한 작품(monitoring_title)을 그룹핑하여 작업 리스트를 생성합니다.
        이후 작업 리스트를 반복하면서, 해당 작품의 각 URL을 포함하는 저작권 침해 신고서를 생성합니다.

        Args:
            df (pd.DataFrame): D.ct_id, S.c_id, D.p_id, T.monitoring_title, D.url 을 컬럼 헤더로 갖는 데이터프레임을 파라미터로 받습니다.

        Returns:
            dict: 함수가 종료될 때, 총 신고서 작성에 성공하거나 실패한 게시물의 개수를 dictionary 형태로 반환합니다.
        """
        each_client_work = dict(list(df.groupby(['c_id'])))
        each_title_work = [(c_id, list(each_client_work[c_id].groupby(['monitoring_title'])['ct_id', 'url'])) for c_id in each_client_work.keys()]
        work_list:list[tuple[int, str, list]] = [(c_id, title, ctid_url_list.reset_index(drop=True).values.tolist()) for c_id, title_and_url_list in each_title_work for title, ctid_url_list in title_and_url_list]
        report_url_list:list[str] = []
        requested_urls_ctid:list[str] = []
        self.driver.get(self.dmca_url)
        for c_id, copyright_work_title, ctid_url_list in work_list:
            list(map(lambda x: report_url_list.append(x[1]), ctid_url_list))
            time.sleep(5)
            self.confirm_email()
            time.sleep(1.5)
            self.input_common_informaton(c_id)
            time.sleep(1.5)
            report_urls = "\n".join(report_url_list)
            self.input_infringing_copyright_work(c_id, copyright_work_title, report_urls)
            time.sleep(1.5)
            self.submit()
            time.sleep(1.5)
            list(map(lambda x: requested_urls_ctid.append(x[0]), ctid_url_list))
            update_count = update_system_report_date_from_dct(requested_urls_ctid)
            self.total_success_count += update_count

        self.driver.close()

        return {'total_success': self.total_success_count, 'total_fail': self.total_fail_count}


class TwitterReport(BaseReportObject):
    """
    _summary_

    _extended_summary_

    Args:
        BaseReportObject (_type_): _description_
    """
    def __init__(self):
        super().__init__()
        self.dmca_information = get_data(filename='')
        self.dmca_url = "https://help.twitter.com/ko/forms/ipi"

    def login(self, login_url='https://twitter.com/i/flow/login'):
        """
        _summary_

        _extended_summary_

        Args:
            login_url (str, optional): _description_. Defaults to 'https://twitter.com/i/flow/login'.
        """
        self.driver.get(login_url)
        time.sleep(5)
        iframe = self.driver.find_element(By.TAG_NAME, 'iframe')
        self.driver.switch_to.frame(iframe)
        google_login = self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[1]')
        google_login.click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        login_account_elem = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="credentials-picker"]/div[1]')))
        login_account_elem.click()
        self.driver.switch_to.window(self.driver.window_handles[0])
        try:
            already_login_modal = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[3]/div/div/div/div/div/div[2]/div[2]/div/div')))
        except TimeoutException:
            print('login success')
            return True
        else:
            already_login_modal.click()
            return True

    def click_reporter_option(self):
        """
        _summary_

        _extended_summary_
        """

        select_tag_1 = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="twtr-spa-main"]/div[1]/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[3]/div[1]/div/div[1]/div/div[1]/div/div[2]/fieldset/select')))
        select_1 = Select(select_tag_1) # 저작권 침해 가능성 신고
        select_1.select_by_value('/ko/forms/ipi/dmca') # option 중 '동영상'을 선택
        time.sleep(1)
        select_tag_2 = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="twtr-spa-main"]/div[13]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[3]/div[1]/div[2]/div[2]/fieldset/select')))
        select_2 = Select(select_tag_2) # 이 문제로 피해를 입은 사람
        select_2.select_by_value('/ko/forms/ipi/dmca/authorized-rep') # option 중 '저는 해당 저작권자의 공식 대리인입니다' 선택

    def input_common_informaton(self, c_id:int, copyright_work_title:str):
        """
        _summary_

        _extended_summary_

        Args:
            c_id (int): _description_
            copyright_work_title (str): _description_
        """
        # 권리 소유자 이름
        copyright_owner = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/input')))
        copyright_owner.send_keys(self.dmca_information[c_id]['copyright_owner'])
        your_name = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/input')  # 이름 element
        your_name.send_keys(self.dmca_information['common_information']['your_name'])
        company = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[3]/div[1]/div[2]/input')  # 회사 element
        company.send_keys(self.dmca_information['common_information']['company'])
        relationship = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[4]/div[1]/div[2]/input')  # 직책 element
        relationship.send_keys(self.dmca_information['common_information']['relationship'])
        detail_address = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[7]/div[1]/div[2]/input')  # 상세 주소 element
        detail_address.send_keys(self.dmca_information['common_information']['detail_address'])
        district = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[8]/div[1]/div[2]/input')  # 시 element
        district.send_keys(self.dmca_information['common_information']['district'])
        city = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[9]/div[1]/div[2]/input')  # 시/도 element
        city.send_keys(self.dmca_information['common_information']['city'])
        postal_code = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[10]/div[1]/div[2]/input')  # 우편 번호 element
        postal_code.send_keys(self.dmca_information['common_information']['postal_code'])
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[11]/div[1]/fieldset/select')) # 국가: select 태그의 XPATH로 요소를 찾음
        select.select_by_value('KR') # option 중 '대한민국'을 선택
        phone_number = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[12]/div[1]/div[2]/input')  # 전화 번호 element
        phone_number.send_keys(self.dmca_information['common_information']['phone_number'])
        fax_number = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div/div/div[2]/div[13]/div[1]/div[2]/input')  # 팩스 번호 element
        fax_number.send_keys(self.dmca_information['common_information']['fax_number'])
        platform_type = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div/span')
        platform_type.click()  # 플랫폼 유형: Twitter 선택
        copyright_work_type = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[3]/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[4]/div/span/input')
        copyright_work_type.click()  # 저작물 유형: 동영상/시청각 기록물 선택
        # 원저작물에 대한 설명 (필수 항목)
        copyright_work_description = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[3]/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/textarea')
        copyright_work_description.send_keys(self.dmca_information[c_id]['additional_information_1'])
        copyright_work_description.send_keys(f'<{copyright_work_title}>.')
        # 침해 사실에 대한 설명 (필수 항목)
        report_description = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[4]/div[1]/div/div/div[2]/div[3]/div[1]/div[2]/textarea')
        report_description.send_keys(self.dmca_information[c_id]['copyright_work_description_1'] + ' ' + f'<{copyright_work_title}>.')
        legal_condition_1 = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[5]/div[1]/div[2]/div[1]/div[2]/div/div/div/span')
        legal_condition_1.click()  # 해당 진술:1 선택
        legal_condition_2 = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[5]/div[1]/div[3]/div[1]/div[2]/div/div/div/span')
        legal_condition_2.click()  # 해당 진술:2 선택
        legal_condition_3 = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[5]/div[1]/div[4]/div[1]/div[2]/div/div/div/span')
        legal_condition_3.click()  # 해당 진술:3 선택
        signature = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[5]/div[1]/div[7]/div[1]/div[2]/input')  # 전자 서명
        signature.send_keys(self.dmca_information['common_information']['signature'])

    def input_infringing_copyright_work(self, report_cnt: int, infringing_url: str):
        """
        _summary_

        _extended_summary_

        Args:
            report_cnt (int): _description_
            infringing_url (str): _description_
        """
        input_url = self.driver.find_element(By.NAME, f'_1717781516@Infringing_Urls__c[{str(report_cnt)}].value')
        input_url.send_keys(infringing_url)

    def add_url(self):
        """
        _summary_

        _extended_summary_
        """
        next_link_btn = self.driver.find_element(By.XPATH, '//*[@id="twtr-spa-main"]/div[17]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div[5]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/form/div/div[4]/div[1]/div/div/div[2]/div[1]/div[1]/div/button')
        next_link_btn.click()

    def submit(self):
        """
        _summary_

        _extended_summary_

        Raises:
            Exception: _description_
        """
        submit_btn = self.driver.find_element(By.XPATH, '//button[contains(text(), "제출")]')
        if submit_btn.text == '제출':
            submit_btn.click()
        else:
            raise Exception('제출 버튼 element xpath 에러')

    def run(self, df: pd.DataFrame):
        """
        이 메소드는 객체 지향 프로그래밍을 사용하여 작성된 메소드로, self 파라미터를 통해 클래스 내부 변수 및 메소드에 접근할 수 있습니다.

        이 메소드는 pd.DataFrame 형식의 데이터프레임을 파라미터로 받으며, 각각의 고객(c_id)과 해당 고객이 등록한 작품(monitoring_title)을 그룹핑하여 작업 리스트를 생성합니다.
        이후 작업 리스트를 반복하면서, 해당 작품의 각 URL을 포함하는 저작권 침해 신고서를 생성합니다.

        Args:
            df (pd.DataFrame): D.ct_id, S.c_id, D.p_id, T.monitoring_title, D.url 을 컬럼 헤더로 갖는 데이터프레임을 파라미터로 받습니다.

        Returns:
            dict: 함수가 종료될 때, 총 신고서 작성에 성공하거나 실패한 게시물의 개수를 dictionary 형태로 반환합니다.
        """
        each_client_work = dict(list(df.groupby(['c_id'])))
        each_title_work = [(c_id, list(each_client_work[c_id].groupby(['monitoring_title'])['ct_id', 'url'])) for c_id in each_client_work.keys()]
        work_list:list[tuple[int, str, list]] = [(c_id, title, ctid_url_list.reset_index(drop=True).values.tolist()) for c_id, title_and_url_list in each_title_work for title, ctid_url_list in title_and_url_list]
        is_login = False
        for c_id, copyright_work_title, ctid_url_list in work_list:
            requested_urls_ctid:list[str] = []
            if not is_login:
                is_login_success = self.login()
                is_login = True
            self.driver.get(self.dmca_url)
            time.sleep(5)
            self.click_reporter_option()
            self.input_common_informaton(c_id, copyright_work_title)
            time.sleep(1.5)
            for report_cnt, ctid_url in enumerate(ctid_url_list, 0):
                if report_cnt >= 1:
                    self.add_url()
                    time.sleep(1.5)
                self.input_infringing_copyright_work(report_cnt, ctid_url[1])
                time.sleep(1.5)
                requested_urls_ctid.append(ctid_url[0])
                time.sleep(1.5)
            else:
                self.submit()
                time.sleep(1.5)
                update_count = update_system_report_date_from_dct(requested_urls_ctid)
                self.total_success_count += update_count

        self.driver.close()

        return {'total_success': self.total_success_count, 'total_fail': self.total_fail_count}

if __name__ == '__main__':
    # 삭제할 영상 URL Listing
    df = select_dct_to_delete()

    # deleter 객체 생성
    yt_report = YoutubeReport()
    yt_total_cnt = yt_report.run(yt_df := (df[df['p_id'] == 1]))
    print('YoutubeReport conduct this result:', yt_total_cnt)

    # TODO: Facebook, Instagram -> capcha 문제 해결 필요.
    fb_report = FacebookReport()
    fb_total_cnt = fb_report.run(fb_df := (df[df['p_id'] == 2]))
    print('FacebookReport conduct this result:', fb_total_cnt)

    insta_report = InstagramReport()
    insta_total_cnt = insta_report.run(insta_df := (df[df['p_id'] == 3]))
    print('InstagramReport conduct this result:', insta_total_cnt)

    tiktok_report = TiktokReport()
    tiktok_total_cnt = tiktok_report.run(tiktok_df := (df[df['p_id'] == 4]))
    print('TiktokReport conduct this result:', tiktok_total_cnt)

    twitter_report = TwitterReport()
    twitter_total_cnt = twitter_report.run(twitter_df := (df[df['p_id'] == 5]))
    print('TwitterReport conduct this result:', twitter_total_cnt)
