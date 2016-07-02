#!/usr/bin/env python

from notifications.pushbullet import PushBullet
from notifications.slack import Slack
from util.singleton import Singleton

@Singleton
class NotificationFactory():
    """
    Chooses the right subclass function to call.
    """

    def __init__(self):
        pass

    def get_instance(self, parameters):
        if not 'notificator' in parameters or not 'type' in parameters['notificator']:
            return None

        notificator_class = {
            'PushBullet': PushBullet,
            'Slack': Slack,
        }.get(parameters['notificator']['type'], None)

        if not notificator_class:
            raise NotImplementedError("Notificator Not Supported")

        return notificator_class(parameters['notificator'])
