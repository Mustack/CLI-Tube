from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Video, Channel, create_tables

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('CLI-Tube.ini')
GOOGLE_DEVELOPER_KEY = config.get('Google API', 'DeveloperKey')

engine = create_engine('sqlite:///clitube.db')
Session = sessionmaker(bind=engine)
session = Session()

def add_channel(username, pref_name=None):
	#Google/Youtube stuff n things
	import gdata.youtube
	import gdata.youtube.service

	yt_service = gdata.youtube.service.YouTubeService()
	yt_service.developer_key = GOOGLE_DEVELOPER_KEY

	uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % username
	feed = yt_service.GetYouTubeVideoFeed(uri)

	#Now for some sqlalchemy magic
	chan = Channel(
				name=username,
				pref_name=pref_name
			)
	session.add(chan)

	session.add_all(
		[Video(
			name = entry.title.text,
			url = entry.link[0].href,
			channel = chan
		) for entry in feed.entry]
	)

	session.commit()

	return feed #in case you might want it

def play_video(videos):
	from subprocess import call
	from time import time #Not kidding

	vlc = ['vlc', '--play-and-exit']

	tolerance = config.get('Options', 'Completion Tolerance')

	for video in videos:
		vlc.append(video.url)
		call(vlc)
		vlc.pop()
		
		video.watched = True
		session.commit()

#useful for testing
# create_tables(engine)
# add_channel('egoraptor', 'ego')
# play_video([session.query(Video).first()])
