#!/usr/bin/env python

from notifications.pushbullet import PushBullet


class NotificationFactory():
    """
    Chooses the right subclass function to call.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_instance(parameters):
        if not 'notificator' in parameters:
            return None

        notificator_class = {
            'PushBullet': PushBullet,
        }.get(parameters['notificator'], None)

        if not notificator_class:
            raise NotImplementedError("Notificator Not Supported")

        return notificator_class(parameters)
