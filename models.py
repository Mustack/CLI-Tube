from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import desc, ForeignKey, Column, Integer, String, Boolean
from string import rfind

Base = declarative_base()
class Channel(Base):
	__tablename__ = 'channels'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	pref_name = Column(String)  #TODO: enforce uniqueness across name and pref_name

	videos = relationship("Video", backref=backref('channel', order_by=id))

	def __init__(self, name, pref_name=None):
		self.name = name.decode('utf-8')
		self.pref_name = pref_name.decode('utf-8')

#TODO: Inherit from Channel
class Playlist(Base):
	__tablename__ = 'playlists'

	id = Column(Integer, primary_key=True)
	yt_id = Column(String, nullable=False, unique=True)
	name = Column(String, nullable=False, unique=True)
	pref_name = Column(String)

	channel_id = Column(Integer, ForeignKey('channels.id'))

	videos = relationship("Video", backref=backref('playlist'), order_by=desc('videos.id'))

	def __init__(self, yt_id, name, channel):
		self.yt_id = yt_id.decode('utf-8')
		self.name = name.decode('utf-8')
		self.channel = channel


class Video(Base):
	__tablename__ = 'videos'

	id = Column(Integer, primary_key=True)
	yt_id = Column(String, nullable=False, unique=True)
	name = Column(String, nullable=False)
	watched = Column(Boolean, nullable=False)

	channel_id = Column(Integer, ForeignKey('channels.id'))
	playlist_id = Column(Integer, ForeignKey('playlists.id'), nullable=True)

	def __init__(self, yt_id, name, channel):
		self.yt_id = yt_id.decode('utf-8')
		self.name = name.decode('utf-8')
		self.watched = False
		self.channel = channel

	@property
	def url(self):
		return 'http://www.youtube.com/watch?v='+ self.yt_id

def create_tables(engine):
	Base.metadata.create_all(bind=engine)