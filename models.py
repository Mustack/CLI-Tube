from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean

Base = declarative_base()
class Channel(Base):
	__tablename__ = 'channels'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	pref_name = Column(String)

	videos = relationship("Video", backref=backref('channel', order_by=id))

	def __init__(self, name, pref_name=None):
		self.name = name
		self.pref_name = pref_name


class Video(Base):
	__tablename__ = 'videos'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	url = Column(String, nullable=False)
	channel_id = Column(Integer, ForeignKey('channels.id'))
	watched = Column(Boolean)

	def __init__(self, name, url, channel):
		self.name = name
		self.url = url.replace('https:', 'http:')
		self.channel = channel
		self.watched = False

def create_tables(engine):
	Base.metadata.create_all(bind=engine)