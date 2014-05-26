#!/usr/bin/env python

#####################

import datetime
import threading
import os
try:
	import socks
	NO_SOCKS = False
except ImportError:
	NO_SOCKS = True
import socket
#####################

from parsers.base import SiteParserBase
from parsers.factory import SiteParserFactory
from util import updateNode

#####################

class SiteParserThread( threading.Thread ):

	def __init__ ( self, optDict, dom, node):
		threading.Thread.__init__(self)

		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))

		self.dom = dom
		self.node = node
		self.siteParser = SiteParserFactory.getInstance(self)

		# create download directory if not found
		try:
			if os.path.exists(self.downloadPath) is False:
				os.makedirs(self.downloadPath)
		except OSError:
			print("""Unable to create download directory. There may be a file
				with the same name, or you may not have permissions to write
				there.""")
			raise

		print('\n')

	def run (self):
		try:
			self.siteParser.parseSite()
			self.downloadNewChapters()

		except self.siteParser.NoUpdates:
			print ("Manga ("+self.manga+") up-to-date.")

		except SiteParserBase.MangaNotFound as Instance:
			print("Error: Manga ("+self.manga+")")
			print(Instance)
			print("\n")
			return

	def downloadNewChapters(self):

		for current_chapter in self.siteParser.chapters:
			#print "Current Chapter =" + str(current_chapter[0])
			iLastChap = current_chapter[1]

		success = self.siteParser.download()

		# Update the XML File only when all the chapters successfully download. If 1 of n chapters failed
		# to download, the next time the script is run the script will try to download all n chapters. However,
		# autoskipping (unless the user specifies the --overwrite Flag) should skip the chapters that were already
		# downloaded so little additional time should be added.

		if self.xmlfile_path != None and success:
			updateNode(self.dom, self.node, 'LastChapterDownloaded', str(iLastChap))
			self.updateTimestamp()

	def updateTimestamp(self):
		t = datetime.datetime.today()
		timeStamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)

		updateNode(self.dom, self.node, 'timeStamp', timeStamp)
