"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#USERS

# get all users
@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()
    user_list = [element.serialize() for element in users]
    return jsonify(user_list), 200

# get one user
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):

    user = User.query.get(user_id)
    if user is None: 
        return "User Not Found", 400
    return jsonify(user), 200

# get one user favorite
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):

    user = User.query.get(user_id)
    if user is None: 
        return "User Not Found", 400
    favorites = [favorite.serialize() for favorite in user.favorites]
    #if user.favorites is None: 
    #    return "User doesn't have favorites", 400
    return jsonify(favorites), 200


# PEOPLE


# get all people
@app.route('/people', methods=['GET'])
def get_people():

    people = People.query.all()
    people_list = [element.serialize() for element in people]
    return jsonify(people_list), 200

# get one person
@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):

    person = People.query.get(person_id)
    if person is None: 
        return "Person Not Found", 400
    return jsonify(person.serialize()), 200

# add one favorite person to user
@app.route('/favorite/people/<int:person_id>/<int:user_id>', methods=['POST'])
def add_person_favorite(person_id, user_id):

    user = User.query.get(user_id)
    if user: 
        favorite = Favorites(user_id = user_id, people_id = person_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"Message": "Favorite added."})
    else: 
        return jsonify({"Message": "User Not Found"}), 400
    
# delete one favorite person to user
@app.route('/favorite/people/<int:person_id>/<int:user_id>', methods=['DELETE'])
def delete_person_favorite(person_id, user_id):

    user = User.query.get(user_id)
    if user: 
        favorite = Favorites.query.filter_by(user_id = user_id, people_id = person_id).first()
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"Message": "Favorite person removed."})
    else: 
        return jsonify({"Message": "User Not Found"}), 400


# PLANETS


# get all planets
@app.route('/planet', methods=['GET'])
def get_planets():

    planets = Planet.query.all()
    planet_list = [element.serialize() for element in planets]
    return jsonify(planet_list), 200

# get one planet
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    planet = Planet.query.get(planet_id)
    if planet is None: 
        return "Planet Not Found", 400
    return jsonify(planet.serialize()), 200

# add one favorite planet to user
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def add_planet_favorite(planet_id, user_id):

    user = User.query.get(user_id)
    if user: 
        favorite = Favorites(user_id = user_id, planet_id = planet_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"Message": "Favorite added."})
    else: 
        return jsonify({"Message": "User Not Found"}), 400
    
# delete one favorite planet to user
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id, user_id):

    user = User.query.get(user_id)
    if user: 
        favorite = Favorites.query.filter_by(user_id = user_id, planet_id = planet_id).first()
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"Message": "Favorite planet removed."})
    else: 
        return jsonify({"Message": "User Not Found"}), 400

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
