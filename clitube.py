from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from models import Video, Channel, Playlist, create_tables

engine = create_engine('sqlite:///clitube.db')
Session = sessionmaker(bind=engine)
session = Session()

def add_channel(username, pref_name=None, regex=None):
	#Google/Youtube stuff n things
	import gdata.youtube
	import gdata.youtube.service
	import re

	def get_id(entry):
		return entry.id.text[entry.id.text.rfind('/')+1:]

	#The api does not return all results. This function does.
	def get_full_feed(feed):
		entries = feed.entry

		while feed.GetNextLink():
			feed = yt_service.GetYouTubePlaylistFeed(uri=feed.GetNextLink().href)
			entries.extend(feed.entry)

		return entries


	yt_service = gdata.youtube.service.YouTubeService()

	uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % username
	videos = get_full_feed(yt_service.GetYouTubeVideoFeed(uri=uri))

	if not videos:
		print 'ERROR: invalid youtube user (channel) name'

	playlists = get_full_feed(yt_service.GetYouTubePlaylistFeed(username=username))

	#Now for some sqlalchemy magic
	chan = Channel(
				name=username,
				pref_name=pref_name
			)
	session.add(chan)		

	session.add_all(
		[Video(
			yt_id=get_id(video),
			name=video.title.text,
			channel=chan
		) for video in videos if not regex or re.match(regex, video.title.text)]
	)

	for playlist in playlists:
		pl = Playlist(
				yt_id=get_id(playlist),
				name=playlist.title.text,
				channel=chan
			)
		session.add(pl)

		videos = get_full_feed(yt_service.GetYouTubePlaylistVideoFeed(playlist_id=pl.yt_id))

		for index, video in enumerate(videos, start=1):
			id = video.link[6].href[video.link[6].href.rfind('/')+1:]
			vid = session.query(Video).filter(Video.yt_id==id)
			vid.playlist_position = index
			vid.playlist = pl
			session.commit()


	session.commit()

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

	if query.count():
		play_video(session.query(Video)
			.filter(
				and_(
					Video.channel==query.first(),
					Video.watched==False)
				)
			.limit(limit)
		)
	else:
		print "ERROR: "+ name +" is not a valid channel name"

#useful for testing
# create_tables(engine)
# add_channel('GameGrumps', 'grumps')
# play_video([session.query(Video).first()])
play_channel('grumps', 17)
