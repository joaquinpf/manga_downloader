#!/usr/bin/env python

from notifications.pushbullet import PushBullet

class NotificationFactory():
    """
    Chooses the right subclass function to call.
    """
    @staticmethod
    def getInstance(parameters):
        if not 'notificator' in parameters:
            return None

        NotificatorClass = {
                'PushBullet'    : PushBullet,
                }.get(parameters['notificator'], None)

        if not NotificatorClass:
            raise NotImplementedError("Notificator Not Supported")

        return NotificatorClass(parameters)
