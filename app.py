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
    """
    home pages rout ('/')

    All users are retrieved from the table and then passed to index.html.
    All existing users are displayed there.
    """
    users = data_manager.get_users()
    return render_template('index.html', users=users)

@app.route('/users', methods=['POST'])
def create_user():
    """
    Route for creating a new user (“/users”)

    The ‘name’ input is retrieved and passed to `data_manager.add_user`
    Once the data has been successfully passed, the user is redirected back to the home page.
    If the input is an empty string, the user is redirected to the 400.html page and
    informed why the user could not be create.
    """
    name = request.form.get("name", "").strip()
    if not name:
        message = "User name can not be empty"
        return render_template('400.html', message=message), 400
    data_manager.add_user(name)
    return redirect(url_for('home'))

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """
    Route to the user page

    All films associated with the logged-in user’s ID are retrieved.

    If a user logs in with an invalid ID, they are redirected to 404.html with the message ‘User user_id not found’.
    """
    if not data_manager.user_exists(user_id):
        return render_template('404.html', message=f"User {user_id} not found"), 404

    movies = data_manager.get_movies(user_id)
    user_name = User.query.filter_by(id=user_id).first()
    message = request.args.get('message')
    return render_template('get_movie.html', movies=movies, user_id=user_id, user_name=user_name, message=message)

@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """
    Route for adding a new movie

    The title input is retrieved and passed to `data_manager.add_movie`

    If an existing title is returned,
    a message is generated stating “Movie added successfully”;
    the connection between the `movie_id` and the `user_id` is then established.
    Once the link has been successfully established, the user is redirected to `get_movie`;
    the newly added movie appears in the list

    Error handling
    If no title is returned, the 500.html page is displayed with the message ‘movie not found’.
    Should anything go wrong whilst linking the `user_id` and `movie_id` – for example,
    if a movie is already linked to the `user_id` –
    the user is redirected to 500.html with the appropriate message.
    (The message is generated in `data_mananger.connect_userid_with_movieid`.)
    """

    if not data_manager.user_exists(user_id):
        return render_template('404.html', message=f"User {user_id} not found"), 404

    movie_title = request.form.get("title")
    publication_year = request.form.get("publication_year")

    title = data_manager.add_movie(movie_title, publication_year)
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
    """
    Route for changing a movie title

    The new movie title is retrieved as input and passed to `data_manager.update_movie`.

    If the operation is successful, the user is redirected to `get_movies` and the new movie title is displayed as the movie title.

    Error handling:
    If an error occurs whilst updating a movie title, the user is redirected to `404.html` with an appropriate message.
    (The message is generated in `data_mananger.update_movie`.)
    """
    new_movie_title = request.form.get("title")
    message = data_manager.update_movie(movie_id, new_movie_title)
    if message:
        return render_template('404.html', message=message), 404
    return redirect(url_for('get_movies', user_id=user_id))

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Route for deleting a movie.

    If the input is a delete command, `data_manager.delete_movie_from_user`
    is called and `user_id` and `movie_id` are passed to it.

    Once the movie has been successfully deleted, the page is redirected to `get_movie`
    and the deleted movie is no longer displayed in the list.

    """
    data_manager.delete_movie_from_user(user_id, movie_id)
    return redirect(url_for('get_movies', user_id=user_id))

@app.errorhandler(404)
def page_not_found(e):
    """route for Error handling 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """route for Error handling 500"""
    return render_template('500.html'), 500

@app.errorhandler(400)
def incorrect_client_input(e):
    """route for Error handling 400"""
    return render_template('400.html'), 400

if __name__ == '__main__':
  with app.app_context():
    db.create_all()

  app.run(host="0.0.0.0", port=5100, debug=True)