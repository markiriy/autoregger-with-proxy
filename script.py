from pytempmailsapi import tempMailApi
import requests, requests.utils
from time import sleep
from capmonster_python.turnstile import TurnstileTask
import http.client as http_client
import logging


def WloReger(passwd):
    http_client.HTTPConnection.debuglevel = 1

    # логирование
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    proxies = {'http': 'YOURPROXYHERE'}

    url = 'YOURREGISTERURL'
    verurl = 'YOUREMAILVERIFICATIONURL'

    s = requests.session()
    headers = {'client-id': 'CLIENTID',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/110.0.0.0 Safari/537.36 OPR/96.0.0.0'}



    #РЕШЕНИЕ КАПЧИ
    capmonster = TurnstileTask("YOURAPIKEY")
    capmonster.set_proxy("http", "YOURPROXYINFO")
    task_id = capmonster.create_task("YOURREGISTERURL", "SITEKEY")
    result = capmonster.join_task_result(task_id)
    captcha_result = result.get('token')

    # ПОЛУЧЕНИЕ ИМЕЙЛА
    regAccount = tempMailApi().createNewMailBox()
    userTempMail = tempMailApi(token=regAccount['token'])
    # gets the name of the mailbox (token required)
    mailBox = userTempMail.getMailBox()


    datas = {
        'agree': True,
        "captcha_token": captcha_result,
        'email': mailBox,
        'locale': "ru-RU",
        'password': passwd,
        "username": ""
    }
    sleep(5)
    register = s.post(url, json=datas, headers=headers, proxies=proxies)

    #ПОЛУЧЕНИЕ КОДА ИЗ ПИСЬМА
    while True:
        sleep(5)
        getMessages = userTempMail.getMailsList()
        if getMessages[0]['from']=='SENDERNAME':
            mail_id = getMessages[0].get('_id')
            letter = userTempMail.getMailById(id=mail_id)
            letter_body = letter.get('bodyHtml').replace(" ", "").replace("\r\n", "").replace("\n", "").replace("=", "")
            formmsg = letter_body.split(
                'address.</p><divstyle"margin-bottom:24px;border-radius:8px;background-color:#E3E8EB;padding:16px;text-align:center;font-size:30px;line-height:1.5;color:#000">')
            verlist = formmsg[1].split('</div><pstyle"margin:0">Ifyou')
            code_result = verlist[0]
            break

    verifdatas = {
        'email': mailBox,
        'code': code_result,
        'tfa_code': ''}

    verif = s.post(verurl, proxies=proxies, headers=headers, json=verifdatas)


    with open('acc.txt', 'a+') as info:
        info.seek(0)
        data = info.read(100)
        if len(data) > 0:
            info.write("\n")
        info.write(mailBox + ':' + passwd)
    print(f"Пользователь {mailBox} зарегистрирован!")
    return register
    pass

if __name__ == "__main__":
    password = input('Пароль: ')
    WloReger(password)
