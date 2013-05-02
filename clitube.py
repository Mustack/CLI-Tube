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
	video_feed = get_full_feed(yt_service.GetYouTubeVideoFeed(uri=uri))

	if not video_feed:
		print 'ERROR: invalid youtube user (channel) name'

	#Now for some sqlalchemy magic
	chan = Channel(
				name=username,
				pref_name=pref_name
			)
	session.add(chan)		

	videos = {get_id(video): Video(
					yt_id=get_id(video),
					name=video.title.text,
					channel=chan
				) for video in video_feed if not regex or re.match(regex, video.title.text)}

	playlists = get_full_feed(yt_service.GetYouTubePlaylistFeed(username=username))
	for playlist in playlists:
		pl = Playlist(
				yt_id=get_id(playlist),
				name=playlist.title.text,
				channel=chan
			)
		session.add(pl)

		playlist_video_feed = get_full_feed(yt_service.GetYouTubePlaylistVideoFeed(playlist_id=pl.yt_id))

		for vid in playlist_video_feed:
			yt_id = vid.link[3].href[vid.link[3].href.rfind('v=')+2:]
			videos[yt_id].playlist = pl


	session.add_all(videos.values())
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
	print query.first().videos
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

def play_playlist(id=None, name=None, new_pref_name=None, limit=1):
	query = session.query(Playlist)

	if id:
		playlist = query.get(id)
	elif name:
		playlist = query.filter(Playlist.name==name).first()
	else:
		print "ERROR: not a valid playlist name/id"

	if playlist:
		videos = [video for video in playlist.videos if not video.watched]
		play_video(videos[0:limit])

#useful for testing
# create_tables(engine)
add_channel('HuskyStarcraft', 'husky')
# play_video([session.query(Video).first()])
# play_channel('grumps', 17)
# play_playlist(id=1)
