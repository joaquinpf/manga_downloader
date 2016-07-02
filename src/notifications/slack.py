#! /usr/bin/python

from slacker import Slacker

from notifications.notificator import Notificator, NotificationNotSent


class Slack(Notificator):

    def __init__(self, parameters):
        Notificator.__init__(self, parameters)
        self.slack = Slacker(parameters['api_key'])
        self.parameters = parameters

    def push_note(self, title, body, url):
        # Send a message to #general channel
        try:
            self.slack.chat.post_message(self.parameters['channel'], "*MangaDownloader*: Finished downloading <%s|%s>" % (url, title), unfurl_links=True)
        except:
            raise NotificationNotSent()
