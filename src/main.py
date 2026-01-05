from flask import Flask, render_template
from connection import Config, ConfigError, DatabaseError
from database_setup import DatabaseSetup

from routes.anime_routes import anime_bp
from routes.users_routes import users_bp
from routes.genres_routes import genres_bp
from routes.watchlist_routes import watchlist_bp
from routes.other_routes import other_bp

config = Config()
app_config = config.get_app_config()

app = Flask(__name__, template_folder='frontend', static_folder='frontend/static')
app.secret_key = app_config.get('secret_key', 'animelist_secret_key')

app.register_blueprint(anime_bp)
app.register_blueprint(users_bp)
app.register_blueprint(genres_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(other_bp)


@app.errorhandler(ConfigError)
def handle_config_error(e):
    return render_template('error.html', title='Configuration Error', message=str(e)), 500


@app.errorhandler(DatabaseError)
def handle_database_error(e):
    return render_template('error.html', title='Database Error', message=str(e)), 500


@app.errorhandler(404)
def handle_not_found(e):
    return render_template('error.html', title='Page Not Found', message='The requested page does not exist'), 404


@app.errorhandler(500)
def handle_server_error(e):
    return render_template('error.html', title='Server Error', message='An unexpected error occurred'), 500


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    db_setup = DatabaseSetup()
    
    if db_setup.is_first_run():
        print("=" * 60)
        print("FIRST RUN DETECTED")
        print("=" * 60)
        
        if db_setup.setup_database_if_needed():
            print("\nIMPORTANT STEPS:")
            print("1. Open MySQL console or phpMyAdmin")
            print("2. Run the 'databaze.sql' file (created in the root folder)")
            print("3. After creating the database, run the application again")
            print("\nApplication will now exit - run it again after creating the database")
            print("=" * 60)
        else:
            print("\nError creating databaze.sql file!")
        
        exit(0)
    
    print("Starting AnimeList application...")
    app.run(debug=app_config.get('debug', True), port=app_config.get('port', 5000))
