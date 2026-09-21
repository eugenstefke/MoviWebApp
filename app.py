from flask import Flask, request, render_template, url_for 
from data_manager import DataManager
from models import db, Movie

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Link the database and the app. This is the reason you need to import db from models

data_manager = DataManager() # Create an object of your DataManager class


@app.route('/', methods=['GET'])
def home():
    users = data_manager.get_users()

    return render_template('index.html', users=users)

@app.route('/users', methods=['GET', 'POST'])
def create_user():

    if request.method == 'POST':
        name = request.form.get("name")
        data_manager.add_user(name)
        return render_template('add_user.html')

    return render_template('add_user.html')  # Temporarily returning users as a string

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):

    movies = data_manager.get_movies(user_id)

    return render_template('get_movie.html', movies=movies, user_id=user_id)

@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):

    movie_title = request.form.get("title")

    title = data_manager.add_movie(movie_title)
    if title:
        data_manager.connect_userid_with_movieid(user_id, title)
    else:
        pass # muss noch überlegen was passiert, bei else

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie_title(user_id, movie_id):

    if request.method == 'POST':
        new_movie_title = request.form.get("title")
        data_manager.update_movie(movie_id, new_movie_title)

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):

    data_manager.delete_movie_from_user(user_id, movie_id)

if __name__ == '__main__':
  with app.app_context():
    db.create_all()

  app.run(host="0.0.0.0", port=5000, debug=True)