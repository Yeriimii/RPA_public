import datetime
from rpa.mysql.db_manage import update_from_today_to_sdt, insert_from_sdt_to_dct, insert_from_sdt_to_art
from rpa.email.webhard import send_mail_to_webhard_for_delete, send_mail_to_webhard_for_affiliation
from rpa.email.fmkorea import send_mail_to_fmkorea_for_delete


if __name__ == '__main__':
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9))
    if today.weekday() not in [5, 6]: # 주중에만 today -> sdt 업데이트
        update_count = update_from_today_to_sdt()
        print('update_count:', update_count)
    dct_insert_count = insert_from_sdt_to_dct()
    print('dct_insert_count:', dct_insert_count)
    art_insert_count = insert_from_sdt_to_art()
    print('art_insert_count:', art_insert_count)
    send_delete_webhard_mail_count = send_mail_to_webhard_for_delete()
    print('send_delete_webhard_mail_count:', send_delete_webhard_mail_count)
    send_affiliation_webhard_mail_count = send_mail_to_webhard_for_affiliation()
    print('send_affiliation_webhard_mail_count:', send_affiliation_webhard_mail_count)
    send_fmkorea_mail_count = send_mail_to_fmkorea_for_delete()
    print('send_fmkorea_mail_count:', send_fmkorea_mail_count)
