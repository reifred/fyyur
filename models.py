from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class BaseModel(db.Model):
  __abstract__ = True

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
    
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime())

    def __repr__(self):
      return f"<Show {self.id}>"

class Venue(BaseModel):
    __tablename__ = 'Venue'

    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref=db.backref('venue', cascade="delete"))

    @property
    def past_shows(self):
      data = []
      shows = db.session.query(Show).filter(self.id == Show.venue_id).filter(Show.start_time < datetime.now()).all()
      for show in shows:
        data.extend([{
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
      return data

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def upcoming_shows(self):
      data = []
      shows = db.session.query(Show).filter(self.id == Show.venue_id).filter(Show.start_time > datetime.now()).all()
      for show in shows:
        data.extend([{
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
      return data

    @property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    def __repr__(self):
      return f"<Venue {self.id} {self.name}>"

class Artist(BaseModel):
    __tablename__ = 'Artist'

    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref=db.backref('artist', cascade="delete"))

    @property
    def past_shows(self):
      data = []
      shows = db.session.query(Show).filter(self.id == Show.artist_id).filter(Show.start_time < datetime.now()).all()
      for show in shows:
        data.extend([{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
      return data

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def upcoming_shows(self):
      data = []
      shows = db.session.query(Show).filter(self.id == Show.artist_id).filter(Show.start_time > datetime.now()).all()
      for show in shows:
        data.extend([{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
      return data

    @property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    def __repr__(self):
      return f"<Artist {self.id} {self.name}>"
