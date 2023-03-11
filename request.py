import time
import requests
import json
import threading


def get_warn():
    resp_warn = requests.get('http://127.0.0.1:8000/warnings')
    resp_body = json.loads(resp_warn.content)
    return resp_body


def get_no_warn():
    resp_no_warn = requests.get('http://127.0.0.1:8000/no_warnings')
    resp_body = json.loads(resp_no_warn.content)

    if resp_body.get('alerts'):
        print('ALERT ON NON ALERT')

    return resp_body


while True:
    try:
        t1 = threading.Thread(target=get_warn)
        t2 = threading.Thread(target=get_no_warn)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    finally:
        pass
