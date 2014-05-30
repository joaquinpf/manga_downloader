#! /usr/bin/python

class NotificationNotSent(Exception):
    def __init__(self, errorMsg=''):
        self.errorMsg = 'Unable to send notification. %s' % errorMsg

    def __str__(self):
        return self.errorMsg

class Notificator:
    def __init__(self, parameters):
        self.parameters = parameters

    def push_note(self, title, body):
        raise NotImplementedError('Should have implemented this')