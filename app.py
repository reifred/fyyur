#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Show, Venue

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  distinct_cities_and_states_for_venues = Venue.query.distinct(Venue.city, Venue.state).all()
  for venue in distinct_cities_and_states_for_venues:
    data.extend([{
        "city": venue.city,
        "state": venue.state,
    }])

  for venue_data in data:
    venues_in_city_and_state = Venue.query.filter_by(city=venue_data["city"], state=venue_data["state"]).all()
    venue_data["venues"] = [venue for venue in venues_in_city_and_state]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # search for a venue
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  data = []
  for venue in venues:
    data.extend([{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": venue.upcoming_shows_count,
    }])

  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  past_shows = {"past_shows": venue.past_shows}
  upcoming_shows = {"upcoming_shows": venue.upcoming_shows}
  past_shows_count = {"past_shows_count": venue.past_shows_count}
  upcoming_shows_count = {"upcoming_shows_count": venue.upcoming_shows_count}
  data = {**venue.__dict__, **past_shows, **upcoming_shows, **past_shows_count, **upcoming_shows_count}
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

  try:
    new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
    )

    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')  
  except:
    flash('Error occurred. Venue ' + form.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)

    db.session.delete(venue)
    db.session.commit()
    flash('The venue has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except:
    flash('It was not possible to delete this Venue')
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search for artists
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  data = []
  for artist in artists:
    data.extend([{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": artist.upcoming_shows_count,
    }])

  response={
    "count": len(data),
    "data": data
  }
  
  return render_template(
  'pages/search_artists.html', 
  results=response, 
  search_term=search_term
  )

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  past_shows = {"past_shows": artist.past_shows}
  upcoming_shows = {"upcoming_shows": artist.upcoming_shows}
  past_shows_count = {"past_shows_count": artist.past_shows_count}
  upcoming_shows_count = {"upcoming_shows_count": artist.upcoming_shows_count}
  data = {**artist.__dict__, **past_shows, **upcoming_shows, **past_shows_count, **upcoming_shows_count}
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.name.default = artist.name
  form.phone.default = artist.phone
  form.genres.default = artist.genres
  form.state.default = artist.state
  form.city.default = artist.city
  form.facebook_link.default = artist.facebook_link
  form.image_link.default = artist.image_link
  form.website.default = artist.website
  form.seeking_description.default = artist.seeking_description
  form.seeking_venue.default = artist.seeking_venue
  form.process()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)

  try:
    artist = Artist.query.get(artist_id)

    artist.city = form.city.data
    artist.seeking_description = form.seeking_description.data
    artist.seeking_venue = form.seeking_venue.data
    artist.phone = form.phone.data
    artist.state = form.state.data
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website.data
    artist.image_link = form.image_link.data

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + form.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)
  
  form = VenueForm()
  form.name.default = venue.name
  form.phone.default = venue.phone
  form.genres.default = venue.genres
  form.state.default = venue.state
  form.city.default = venue.city
  form.address.default = venue.address
  form.facebook_link.default = venue.facebook_link
  form.image_link.default = venue.image_link
  form.website.default = venue.website
  form.seeking_description.default = venue.seeking_description
  form.seeking_talent.default = venue.seeking_talent
  form.process()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)

  try:
    venue = Venue.query.get(venue_id)
    venue.city = form.city.data
    venue.seeking_description = form.seeking_description.data
    venue.seeking_talent = form.seeking_talent.data
    venue.phone = form.phone.data
    venue.state = form.state.data
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.address = form.address.data

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + form.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)
  try:
    new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
    )

    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + form.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = Show.query.all()
  for show in shows:
    data.extend([{
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }])
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)

  try:
    new_show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data,
    )

    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
