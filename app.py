from email import message

from flask import Flask, request, render_template, url_for, redirect
from data_manager import DataManager
from models import db, Movie, User

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

@app.route('/users', methods=['POST'])
def create_user():

    name = request.form.get("name", "").strip()
    if not name:
        message = "User name can not be empty"
        return render_template('400.html', message=message), 400
    data_manager.add_user(name)
    return redirect(url_for('home'))

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):

    if not data_manager.user_exists(user_id):
        return render_template('404.html', message=f"User {user_id} not found"), 404

    movies = data_manager.get_movies(user_id)
    user_name = User.query.filter_by(id=user_id).first()
    message = request.args.get('message')
    return render_template('get_movie.html', movies=movies, user_id=user_id, user_name=user_name, message=message)

@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):

    if not data_manager.user_exists(user_id):
        return render_template('404.html', message=f"User {user_id} not found"), 404

    movie_title = request.form.get("title")

    title = data_manager.add_movie(movie_title)
    if title:
        message = f"{movie_title}, successfully added"
        error = data_manager.connect_userid_with_movieid(user_id, title)
        if error:
            message = error
            return render_template('500.html', message=message), 500
        return redirect(url_for('get_movies', user_id=user_id, message=message))
    else:
        message = f"{movie_title}, not found"
        return render_template('500.html', message=message), 500


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie_title(user_id, movie_id):

    new_movie_title = request.form.get("title")
    message = data_manager.update_movie(movie_id, new_movie_title)
    if message:
        return render_template('404.html', message=message), 404
    return redirect(url_for('get_movies', user_id=user_id))

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):

    data_manager.delete_movie_from_user(user_id, movie_id)
    return redirect(url_for('get_movies', user_id=user_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
  with app.app_context():
    db.create_all()

  app.run(host="0.0.0.0", port=5100, debug=True)