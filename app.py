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
from flask_wtf import Form
from sqlalchemy.sql.elements import and_
from forms import *


from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *

#Functions 
#_________________________________________________________________________

#function to bring shows data for venue
def get_shows_dates(venue_id):
    upcoming_shows=[]
    past_shows=[]
    show_dict={}
   #Getting required data for venue upcoming shows using join statement
    Upcoming_shows_data = db.session.query(Show).join(Artist).filter(
      and_(Show.id_venue==venue_id,Show.start_time> datetime.now())).all()
    #compare every show time to the current time to know if it's an upcoming show or not
    for show in Upcoming_shows_data:
        upcoming_shows.append(
          {
            "artist_id": show.id_artist,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link ,
            "start_time":str(show.start_time)
          }
          )
    #Getting required data for venue past shows using join statement
    Past_shows_data = db.session.query(Show).join(Artist).filter(
      and_(Show.id_venue==venue_id,Show.start_time < datetime.now())).all()
    for show in Past_shows_data:
        past_shows.append(
          {
            "artist_id": show.id_artist,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link ,
            "start_time":str(show.start_time)
          }
          )
    show_dict['upcoming_shows']= upcoming_shows
    show_dict['past_shows']= past_shows
    show_dict['num_upcoming_shows'] =len(upcoming_shows)
    show_dict['num_past_shows']= len(past_shows)


    return show_dict
    
#function to bring shows data for artist
def get_artist_shows(artist_id):
    upcoming_shows=[]
    past_shows=[]
    Artist_shows_dict={}
   #Getting required data for artist upcoming shows using join statement
    Upcoming_shows_data = db.session.query(Show).join(Venue).filter(
      and_(Show.id_artist==artist_id,Show.start_time> datetime.now())).all()
    #compare every show time to the current time to know if it's an upcoming show or not
    for show in Upcoming_shows_data:
        upcoming_shows.append(
          {
            "venue_id": show.id_venue,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link ,
            "start_time":str(show.start_time)
          }
          )
    #Getting required data for artist past shows using join statement
    Past_shows_data = db.session.query(Show).join(Venue).filter(
      and_(Show.id_artist==artist_id,Show.start_time> datetime.now())).all()
    for show in Past_shows_data:
     past_shows.append(
          {
            "venue_id": show.id_venue,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link ,
            "start_time":str(show.start_time)
          }
          )

    Artist_shows_dict['upcoming_shows']= upcoming_shows
    Artist_shows_dict['past_shows']= past_shows
    Artist_shows_dict['num_upcoming_shows'] =len(upcoming_shows)
    Artist_shows_dict['num_past_shows']= len(past_shows)


    return Artist_shows_dict

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]

  venues = Venue.query.all()
  #get cities and states
  states_cities = []
  for venue in venues:
    states_cities.append((venue.city,venue.state))
  states_cities = list(set(states_cities))
  for state_city in states_cities:
    data.append({
      'city':state_city[0],
      'state':state_city[1],
      'venues':[]
    })
  for venue in venues:
    for StoredVenue in data:
      #function get_shows_dates declared bellow class Venue
        num_upcoming_shows=get_shows_dates(venue.id)['num_upcoming_shows']
        if((StoredVenue['city']==venue.city) and (StoredVenue['state']==venue.state)):
          #add the necessery data to venues
          StoredVenue['venues'].append(
            {
              'id':venue.id,
              'name':venue.name,
              'num_shows':num_upcoming_shows
            }
          )
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #Getting the string search provided by user
  search_term=request.form.get('search_term')
  #Search throw venues table using search string provided by user
  venues=Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))
  #get the number of search results for search string
  count = venues.count() 
  #Bringing the necessary data to show result for user
  data = []
  for venue in venues:
    data.append({
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows":get_shows_dates(venue.id)['num_upcoming_shows']
    })
  response={
    "count":count,
    "data":data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #getting the venue using the id passed by user
  venue=Venue.query.get(venue_id)
  #getting shows data using get_shows_dates function 
  past_shows = get_shows_dates(venue_id)['past_shows']
  upcoming_shows= get_shows_dates(venue_id)['upcoming_shows']
  past_shows_count = get_shows_dates(venue_id)['num_past_shows']
  upcoming_shows_count = get_shows_dates(venue_id)['num_upcoming_shows']
  #affecting data to data dictionary that will be passed to template
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genre,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website":venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.look_for_talent,
    "image_link": venue.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count":past_shows_count,
    "upcoming_shows_count":upcoming_shows_count
    }
 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #Bringing data from the venue form
  form = VenueForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  genre = form.genres.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  website_link = form.website_link.data
  seeking_talent = form.seeking_talent.data
  seeking_description = form.seeking_description.data
  try:
    #create new venue record
    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,
    genre=genre,image_link=image_link,facebook_link=facebook_link,website_link=website_link,
    look_for_talent=seeking_talent,seeking_description=seeking_description)
    #try to send data to database
    venue.create()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!','success')
  #if the insert fails
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + name+ ' could not be listed.','error')
  finally:
    db.session.close()
    return render_template('pages/home.html')




  
  

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail
  #get venue using venue_id
  venue = Venue.query.get(venue_id)
  #try to delete it
  try:
    venue.delete()
    flash('Venue was deleted successfully','success')
  except :
    #if the delete operation fails
    db.session.rollback()
    flash('The delete process failed','error')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  #Bringing all artists dat from Artist table
  artists = Artist.query.all()
  #loop throw all artists and get wanted data
  for artist in artists:
    data.append(
      {
      'id': artist.id,
      'name':artist.name
      }
    )
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #Getting the string search provided by user
  search_term=request.form.get('search_term')
  #Search throw artists table using search string provided by user
  artists=Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))
  #get the number of search results for search string
  count = artists.count() 
  #Bringing the necessary data to show result for user
  data = []
  for artist in artists:
    data.append({
      "id":artist.id,
      "name":artist.name,
      #get num_upcoming shows using get_artist_shows function 
      "num_upcoming_shows":get_artist_shows(artist.id)
    })
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  #get shows data using get_artist_shows function 
  past_shows = get_artist_shows(artist_id)['past_shows']
  upcoming_shows = get_artist_shows(artist_id)['upcoming_shows']
  past_shows_count =get_artist_shows(artist_id)['num_past_shows']
  upcoming_shows_count = get_artist_shows(artist_id)['num_upcoming_shows']

  data={
    "id":artist.id,
    "name":artist.name ,
    "genres":artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.look_for_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_shows ,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #get the right venue using passed id
  artiste =Artist.query.get(artist_id)
  #add wanted data to pass it  to template
  artist={
    "id": artiste.id,
    "name": artiste.name,
    "genres": [artiste.genres],
    "city": artiste.city,
    "state": artiste.state,
    "phone": artiste.phone,
    "website": artiste.website_link,
    "facebook_link": artiste.facebook_link,
    "seeking_venue": artiste.look_for_venue,
    "seeking_description": artiste.seeking_description,
    "image_link": artiste.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genre = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
      #try to edit artist record
    try: 
      artist.name = name
      artist.state = state
      artist.city = city
      artist.phone = phone
      artist.genre = genre
      artist.image_link = image_link
      artist.facebook_link = facebook_link
      artist.website_link = website_link
      artist.look_for_venue = seeking_venue
      artist.seeking_description = seeking_description
      #try to send data to database
      artist.update()
      # on successful db update, flash success
      flash('Artist was successfully updated!','success')
    #if the update fails
    except:
      db.session.rollback()
      flash('An error occurred during the updated.','error')
    finally:
      db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  #get the right venue using passed id
  venuee = Venue.query.get(venue_id)
  venue={
    "id": venuee.id,
    "name": venuee.name,
    "genres": [venuee.genre],
    "address": venuee.address,
    "city": venuee.city,
    "state": venuee.state,
    "phone": venuee.phone,
    "website": venuee.website_link,
    "facebook_link": venuee.facebook_link,
    "seeking_talent": venuee.look_for_talent,
    "seeking_description":venuee.seeking_description ,
    "image_link":venuee.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    
    venue = Venue.query.get(venue_id)
    form = VenueForm()
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genre = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
      #try to update venue record
    try: 
      venue.name = name
      venue.state = state
      venue.city = city
      venue.address = address
      venue.phone = phone
      venue.genre = genre
      venue.image_link = image_link
      venue.facebook_link = facebook_link
      venue.website_link = website_link
      venue.look_for_talent = seeking_talent
      venue.seeking_description = seeking_description
      #try to send data to database
      venue.updtae()
      # on successful db update, flash success
      flash('Venue was successfully updated!','sucess')
    #if the update fails
    except:
      db.session.rollback()
      flash('An error occurred during the updated.','error')
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #Bringing data from the Artist form
  form = ArtistForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genre = form.genres.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  website_link = form.website_link.data
  seeking_venue = form.seeking_venue.data
  seeking_description = form.seeking_description.data
  try:
    #create new artist record
    artist = Artist(name=name,city=city,state=state,phone=phone,
    genres=genre,image_link=image_link,facebook_link=facebook_link,website_link=website_link,
    look_for_venue=seeking_venue,seeking_description=seeking_description)
    #try to send data to database
    artist.create()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!','success')
  #if the insert fails
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + name + ' could not be listed.','error')
  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  #get all shows data from Show table
  shows = Show.query.all()
  for show in shows :
    data.append(
      {
        "venue_id": show.id_venue,
        "venue_name":show.venue.name ,
        "artist_id": show.id_artist,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time":str(show.start_time) 
      }
      )
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  #Bringing data from the show form
  form = ShowForm()
  artist_id = form.artist_id.data
  venue_id = form.venue_id.data
  start_time = form.start_time.data
  try:
    #create new form record
    show = Show(id_venue=venue_id,id_artist=artist_id,start_time=start_time)
    #try to send data to database
    show.create()
    # on successful db insert, flash success
    flash('Show was successfully listed!','sucess')
  #if the insert fails
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.','error')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
