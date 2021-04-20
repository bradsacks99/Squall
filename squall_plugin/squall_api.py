"""Squall API Client"""

import requests
import json

class SquallAPI:
    """SquallAPI"""

    def __init__(self) -> None:
        pass

    def get(self, uid: str = None):
        url = 'http://localhost:30080/tasks/'
        if uid is not None:
            url = 'http://localhost:30080/tasks/' + uid + '/'

        r = requests.get(url)
        json_obj = json.loads(r.text)
        json_formatted = json.dumps(json_obj, indent=2)

        print(json_formatted)

    def update(self, uid: str = None, data: str = None):
        url = 'http://localhost:30080/tasks/'
        if uid is not None:
            url = 'http://localhost:30080/tasks/' + uid + '/'

        r = requests.patch(url, data=data)
        json_obj = json.loads(r.text)
        json_formatted = json.dumps(json_obj, indent=2)

        print(json_formatted)
