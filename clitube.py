from subprocess import call
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import gdata.youtube
import gdata.youtube.service
from models import Video, Channel, create_tables

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('CLI-Tube.ini')
GOOGLE_DEVELOPER_KEY = config.get('Google API', 'DeveloperKey')

engine = create_engine('sqlite:///clitube.db')
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_channel(username, pref_name=None):
	#Google/Youtube stuff n things
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

	videos = [Video(name=entry.title.text, url=entry.link[0].href, channel=chan) for entry in feed.entry]
	session.add_all(videos)

	session.commit()

	return chan #in case you might want it

add_channel('egoraptor', 'ego')