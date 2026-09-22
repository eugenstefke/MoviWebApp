from models import db, User, Movie, UserMovie
from data_collector.data_collector_OMDB import retrieve_data

class DataManager():


    def add_user(self, name):

        if not name:
            return "The name can not be empty"

        db.session.add(User(name=name))
        db.session.commit()

    def get_users(self):

        return User.query.all()

    def get_movies(self, user_id):

        return (Movie.query.join(UserMovie, Movie.id == UserMovie.movie_id).filter(UserMovie.user_id == user_id).all())

    def add_movie(self, title):

        if not title:
            return None

        movie_omdb_info = retrieve_data(title)
        if movie_omdb_info ["Response"] != "True":
            return None
        try:
            title = movie_omdb_info["Title"]
            movie_exist = Movie.query.filter_by(title=title).first()
            if movie_exist:
                return title

            publication_year = movie_omdb_info["Year"]
            if not publication_year.isdigit() or len(publication_year) != 4: #OMDB sometimes returns N/A or 2019–2022, so this handles it
                publication_year = None
            else:
                publication_year = int(publication_year)
            director = (movie_omdb_info["Director"])
            poster_url = movie_omdb_info["Poster"]
        except KeyError:
            return None
        except Exception:
            db.session.rollback() # When have Error by save the movie
            return None

        new_movie = Movie(title=title, publication_year=publication_year, director=director, poster_url=poster_url)
        db.session.add(new_movie)
        db.session.commit()
        return title

    def update_movie(self, movie_id, new_title):

        movie = Movie.query.get(movie_id)
        if movie is None:
            return "Movie not found"
        if not new_title.strip():
            return "Title can not be empty"

        movie.title = new_title
        db.session.commit()

    def delete_movie_from_user(self, user_id, movie_id):

        user_movie = UserMovie.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if user_movie:
            db.session.delete(user_movie)
            db.session.commit()

    def connect_userid_with_movieid(self, user_id, title):

        user_id_exist = User.query.get(user_id)
        if not user_id_exist:
            return "User not exist"

        movie = Movie.query.filter_by(title=title).first()
        if not movie:
            return "Error Movie not Found "

        already_connected = UserMovie.query.filter_by(user_id=user_id, movie_id=movie.id).first()
        if already_connected:
            return "Movie already in your list"

        user_movie = UserMovie(user_id=user_id, movie_id=movie.id)
        db.session.add(user_movie)
        db.session.commit()

    def user_exists(self, user_id):

        return User.query.get(user_id) is not None