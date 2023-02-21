#Importing required packages
from app import db
#Models

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genre = db.Column(db.String(150))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #added fields
    website_link = db.Column(db.String(500))
    look_for_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    #A oneToMany relationship between venue and show
    shows = db.relationship('Show',backref='venue',lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #added fields
    website_link = db.Column(db.String(500))
    look_for_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    #A oneToMany relationship between artist and show
    shows = db.relationship('Show',backref='artist',lazy=True)

    #CRUD functions
    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__='Show'
  id = db.Column(db.Integer,primary_key=True)
  start_time = db.Column(db.DateTime,nullable=False)
  id_artist = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  id_venue = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)

  #CRUD functions
  def create(self):
        db.session.add(self)
        db.session.commit()
  def delete(self):
        db.session.delete(self)
        db.session.commit()
    
  def update(self):
        db.session.commit()
   
   
  

