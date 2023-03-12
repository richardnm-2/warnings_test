import time
import requests
import json
import threading

import sys

print(sys.argv)


def get_warn():
    resp_warn = requests.get('http://127.0.0.1:8000/warnings')
    resp_body = json.loads(resp_warn.content)
    if sys.argv[1] == 'warn':
        print(resp_body)
    return resp_body


def get_no_warn():
    resp_no_warn = requests.get('http://127.0.0.1:8000/no_warnings')
    resp_body = json.loads(resp_no_warn.content)

    if resp_body.get('alerts'):
        print('ALERT ON NON ALERT')

    if sys.argv[1] == 'no_warn':
        print(resp_body)
        if resp_body.get('alerts'):
            print('ALERT ON NON ALERT')
            raise ValueError
    return resp_body


while True:
    try:
        if sys.argv[1] == 'warn':
            t1 = threading.Thread(target=get_warn)
            t1.start()
            t1.join()

        elif sys.argv[1] == 'no_warn':
            t2 = threading.Thread(target=get_no_warn)
            t2.start()
            t2.join()

        else:
            t1 = threading.Thread(target=get_warn)
            t2 = threading.Thread(target=get_no_warn)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

    finally:
        pass
