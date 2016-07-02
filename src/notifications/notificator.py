#! /usr/bin/python


class NotificationNotSent(Exception):
    def __init__(self, error_msg=''):
        self.errorMsg = 'Unable to send notification. %s' % error_msg

    def __str__(self):
        return self.errorMsg


class Notificator:
    def __init__(self, parameters):
        self.parameters = parameters

    def push_note(self, title, body, url):
        raise NotImplementedError('Should have implemented this')