from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from models import Video, Channel, create_tables

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('CLI-Tube.ini')
GOOGLE_DEVELOPER_KEY = config.get('Google API', 'DeveloperKey')

engine = create_engine('sqlite:///clitube.db')
Session = sessionmaker(bind=engine)
session = Session()

def add_channel(username, pref_name=None, regex=None):
	#Google/Youtube stuff n things
	import gdata.youtube
	import gdata.youtube.service
	import re

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
		) for entry in feed.entry if not regex or re.match(regex, entry.title.text)]
	)

	session.commit()

	return feed #in case you might want it

def play_video(videos):
	from subprocess import call

	vlc = ['vlc', '--play-and-exit']

	for video in videos:
		vlc.append(video.url)
		call(vlc)
		vlc.pop()

		video.watched = True
	
	session.commit()

def play_channel(name, limit=1):
	query = session.query(Channel).filter(Channel.name == name)

	if not query.count():
		query = session.query(Channel).filter(Channel.pref_name == name)

	channel = query.first()
	if query.count():
		play_video(session.query(Video).filter(and_(Video.channel==channel, Video.watched==False)).limit(limit))
	else:
		print "ERROR: "+ name +" is not a valid channel name"

#useful for testing
# create_tables(edngine)
# add_channel('HuskyStarcraft', 'husky', r'(.*) vs (.*)')
# play_video([session.query(Video).first()])
# play_channel('husky', 17)