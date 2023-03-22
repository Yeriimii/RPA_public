# built-in module
import time
import log
import os

# third-party module
from dotenv import load_dotenv

# local module
from rpa.chrome_browser.custom_webdriver import *
from rpa.mysql.db_manage import select_delete_check, update_delete_yn_from_dct
from utilities.pickle_util import get_data

class WebhardDeleteChecker():

    load_dotenv('.env')
    DB_HOST = os.getenv('DB_HOST')
    DB_SUPER_USER = os.getenv('DB_SUPER_USER')
    DB_SUPER_PW = os.getenv('DB_SUPER_PW')
    DB_NAME = os.getenv('DB_NAME')

    def __init__(self) -> None:
        self.platform_info:dict = get_data(filename='')
        self.total_success_cnt = 0
        self.total_fail_cnt = 0

    def alert_case(self, dc_id, site_name) -> bool:
        try:
            alert_1 = WebDriverWait(driver, 3).until(EC.alert_is_present())
        except TimeoutException:
        # except:
            return False
        else:
            alert_1.accept()
            time.sleep(1)
            try:
                alert_2 = WebDriverWait(driver, 1).until(EC.alert_is_present())
            except:
                update_delete_yn_from_dct(dc_id, site_name)

                return True
            else:
                alert_2.accept()
                update_delete_yn_from_dct(dc_id, site_name)

                return True
        finally:
            if len(driver.window_handles) == 2:
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

    def body_empty_case(self, dc_id, site_name) -> bool:
        try:
            body_elem = driver.find_element(By.XPATH, '/html/body').text
        except UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            alert.accept()
        if body_elem == "":
            update_delete_yn_from_dct(dc_id, site_name)
            return True
        else:
            return False

    def delete_page_move_case(self, dc_id, site_name) -> bool:
        if site_name == '':
            time.sleep(5)
            driver.switch_to.window(driver.window_handles[1])
            if 'install' in driver.current_url:
                driver.close()
        try:
            time.sleep(1.5)
            driver.switch_to.window(driver.window_handles[-1])
            delete_reason_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, self.platform_info[site_name]["delete_check_XPATH"])))
        except UnexpectedAlertPresentException:
            update_delete_yn_from_dct(dc_id, site_name)
            return True
        except TimeoutException:
            return False
        else:
            if ("알려" in delete_reason_elem.text) or ("존재" in delete_reason_elem.text) or ("삭제" in delete_reason_elem.text) or ("제재" in delete_reason_elem.text):
                update_delete_yn_from_dct(dc_id, site_name)
                return True
            else:
                return False
        finally:
            if len(driver.window_handles) == 2:
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

    def homepage_move_case(self, dc_id, site_name):
        if driver.current_url == self.platform_info[site_name]["home_url"]:
            update_delete_yn_from_dct(dc_id, site_name)
            return True
        else:
            return False

    def run(self, df):
        for i in range(len(df)):
            dc_id = df[""].iloc[i]
            url = df[""].iloc[i]
            uploader = df[""].iloc[i]
            site_name = uploader

            if self.platform_info[site_name][''] == 0:
                self.webhard_login(site_name)
                self.platform_info[site_name][''] = 1

            if site_name in ('', ''):
                self.delete_check_wedisk(url, dc_id, site_name)
                continue

            if url.startswith("http"):
                driver.get(url)
                time.sleep(1)
            else:
                if self.platform_info[site_name]["frame_name_1"] != '':
                    frame_name_1 = self.platform_info[site_name]["frame_name_1"]
                    driver.switch_to.frame(frame_name_1)
                    time.sleep(1)
                driver.execute_script(url)
                time.sleep(2)

            if self.platform_info[uploader]['delete_case'] == 'alert_case':
                result = self.alert_case(dc_id, site_name)
            elif self.platform_info[uploader]['delete_case'] == 'body_empty_case':
                result = self.body_empty_case(dc_id, site_name)
            elif self.platform_info[uploader]['delete_case'] == 'delete_page_move_case':
                result = self.delete_page_move_case(dc_id, site_name)
            elif self.platform_info[uploader]['delete_case'] == 'homepage_move_case':
                result = self.homepage_move_case(dc_id, site_name)

            if result:
                self.total_success_cnt += 1
            else:
                self.total_fail_cnt += 1
            continue
        else:
            return {'total_success_cnt': self.total_success_cnt, 'total_fail_cnt': self.total_fail_cnt}

    def delete_check_wedisk(self, url, dc_id, site_name):
        current_window_handle = driver.current_window_handle
        driver.switch_to.frame('main')
        driver.execute_script(url)
        new_window_handle = None
        while not new_window_handle:
            try:
                for handle in driver.window_handles:
                    if handle != current_window_handle:
                        new_window_handle = handle
                        break
            except UnexpectedAlertPresentException:
                new_window_handle = driver.window_handles[-1]
                break
        driver.switch_to.window(new_window_handle)
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            update_delete_yn_from_dct(dc_id, site_name)
        except TimeoutException as e:
            driver.execute_script('window.close();')
        finally:
            driver.switch_to.window(current_window_handle)

    def webhard_login(self, site_name):
        driver.get(self.platform_info[site_name]["home_url"])
        if self.platform_info[site_name]["frame_name_1"] != '':
            frame_name_1 = self.platform_info[site_name]["frame_name_1"]
            driver.switch_to.frame(frame_name_1)
            time.sleep(1)
            if self.platform_info[site_name]["frame_name_2"] != '':
                frame_name_2 = self.platform_info[site_name]["frame_name_2"]
                try:
                    driver.switch_to.frame(frame_name_2)
                except:
                    pass
                time.sleep(1)
        try:
            logout_btn_XPATH = self.platform_info[site_name]["login_info"]["logout_btn_XPATH"]
            logout_element = driver.find_element(By.XPATH, logout_btn_XPATH)
            logout_element.is_displayed()
            driver.get(self.platform_info[site_name]['home_url'])
            return
        except:
            if self.platform_info[site_name]["login_info"]["login_btn_XPATH"] != '':
                login_box = driver.find_element(By.XPATH, self.platform_info[site_name]["login_info"]["login_btn_XPATH"])
                login_box.click()
                time.sleep(1)
            id_box = driver.find_element(By.XPATH, self.platform_info[site_name]["login_info"]["id_box_XPATH"])
            id_box.click()
            id_box.clear()
            id_box.send_keys(self.platform_info[site_name]["login_info"]["login_id"])
            time.sleep(1)
            pw_box = driver.find_element(By.XPATH, self.platform_info[site_name]["login_info"]["pw_box_XPATH"])
            pw_box.click()
            pw_box.clear()
            pw_box.send_keys(self.platform_info[site_name]["login_info"]["login_pw"])
            time.sleep(1)
            logbtn = driver.find_element(By.XPATH, self.platform_info[site_name]["login_info"]["login_submit_XPATH"])
            logbtn.click()
            time.sleep(1)
            try:
                driver.get(self.platform_info[site_name]['home_url'])
            except UnexpectedAlertPresentException:
                time.sleep(5)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                driver.get(self.platform_info[site_name]['home_url'])
                time.sleep(5)


class YoutubeDeleteChecker():


    def __init__(self) -> None:
        self.platform_info:dict = get_data(filename='')

    def run(self, df):
        for i in range(len(df)):
            dc_id = df[""].iloc[i]
            p_id = df[""].iloc[i]
            url = df[""].iloc[i]
            site_name = "youtube"

            driver.get(url)
            try:
                delete_msg = driver.find_element(By.XPATH, self.platform_info[p_id]["XPATH"]["ko"]).text
            except NoSuchElementException as e:
                pass
            else:
                update_delete_yn_from_dct(dc_id, site_name)


class FacebookDeleteChecker():


    def __init__(self) -> None:
        self.platform_info:dict = get_data(filename='')

    def run(self, df):
        for i in range(len(df)):
            dc_id = df[""].iloc[i]
            p_id = df[""].iloc[i]
            url = df[""].iloc[i]
            site_name = "facebook"
            driver.get(url)
            try:
                current_url = driver.current_url
                if current_url == self.platform_info[p_id]["HOME"]:
                    update_delete_yn_from_dct(dc_id, site_name)
                    continue
                delete_msg = driver.find_element(By.XPATH, self.platform_info[p_id]["XPATH"]["ko"]).text
            except NoSuchElementException as e:
                pass
            else:
                update_delete_yn_from_dct(dc_id, site_name)


class InstagramDeleteChecker():


    def __init__(self) -> None:
        self.platform_info:dict = get_data(filename='')

    def run(self, df):
        for i in range(len(df)):
            dc_id = df[""].iloc[i]
            p_id = df[""].iloc[i]
            url = df[""].iloc[i]
            site_name = "instagram"
            driver.get(url)
            try:
                delete_msg = driver.find_element(By.XPATH, self.platform_info[p_id]["XPATH"]["ko"]).text  # 각 사이트 별 삭제됐음을 식별할 수 있는 TAG의 XPATH. 존재하면 삭제.
            except NoSuchElementException as e:
                pass
            else:
                update_delete_yn_from_dct(dc_id, site_name)


class TiktokDeleteChecker():


    def __init__(self) -> None:
        self.platform_info:dict = get_data(filename='')

    def run(self, df):
        for i in range(len(df)):
            dc_id = df[""].iloc[i]
            p_id = df[""].iloc[i]
            url = df[""].iloc[i]
            site_name = "tiktok"
            driver.get(url)
            try:
                delete_msg = driver.find_element(By.XPATH, self.platform_info[p_id]["XPATH"]["ko"]).text  # 각 사이트 별 삭제됐음을 식별할 수 있는 TAG의 XPATH. 존재하면 삭제.
            except NoSuchElementException as e:
                pass
            else:
                update_delete_yn_from_dct(dc_id, site_name)


class TwitterDeleteChecker():


    def __init__(self) -> None:
        self.platform_info:dict = get_data(filename='')

    def run(self, df):
        for i in range(len(df)):
            dc_id = df[""].iloc[i]
            p_id = df[""].iloc[i]
            url = df[""].iloc[i]
            site_name = "twitter"
            driver.get(url)

            try:
                button = driver.find_element(By.XPATH, "//*[@class='css-1dbjc4n r-1ndi9ce']/div[1]") # 민감한 콘텐츠를 포함할 수 있습니다. '보기' 버튼 클릭해야 나옴
            except:
                pass
            else:
                button.click()
            try:
                delete_msg = driver.find_element(By.XPATH, self.platform_info[p_id]["XPATH"]["ko"]).text  # 각 사이트 별 삭제됐음을 식별할 수 있는 TAG의 XPATH. 존재하면 삭제.
            except NoSuchElementException as e:
                pass
            else:
                update_delete_yn_from_dct(dc_id, site_name)



if __name__ == "__main__":

    logger:log.logging = log.get_logger("delete checker logger")
    driver = CustomWebDriver.run_chrome()
    driver.implicitly_wait(10)

    df = select_delete_check()

    webhard_checker = WebhardDeleteChecker()
    webhard_checker.run(webhard_df := (df[df['p_id'] == 9]))

    yt_checker = YoutubeDeleteChecker()
    yt_checker.run(yt_df := (df[df['p_id'] == 1]))

    fb_checker = FacebookDeleteChecker()
    fb_checker.run(fb_df := (df[df['p_id'] == 2]))

    insta_checker = InstagramDeleteChecker()
    insta_checker.run(insta_df := (df[df['p_id'] == 3]))

    tiktok_checker = TiktokDeleteChecker()
    tiktok_checker.run(tiktok_df := (df[df['p_id'] == 4]))

    twitter_checker = TwitterDeleteChecker()
    twitter_checker.run(twitter_df := (df[df['p_id'] == 5]))

    driver.close()
