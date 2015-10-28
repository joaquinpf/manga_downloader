#! /usr/bin/python

import requests

from notifications.notificator import Notificator, NotificationNotSent


class PushBullet(Notificator):
    PUSH_URL = 'https://api.pushbullet.com/v2/pushes'

    def __init__(self, parameters):
        Notificator.__init__(self, parameters)

    def push_note(self, title, body):
        data = dict(api_key=self.parameters['api_key'], device_iden=self.parameters['device_id'], title=title,
                    body=body, type='note')
        r = requests.post(self.PUSH_URL, auth=(data['api_key'], ''), verify=False, data=data)
        if r.status_code != 200:
            raise NotificationNotSent()
