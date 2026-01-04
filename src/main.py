from flask import Flask, render_template, request, redirect, url_for, flash
from connection import DatabaseConnection
from tables.anime_gateway import AnimeGateway
from tables.user_gateway import UserGateway
from tables.genre_gateway import GenreGateway
from tables.anime_genre_gateway import AnimeGenreGateway
from tables.watchlist_entry_gateway import WatchlistEntryGateway
from tables.watchlist_history_gateway import WatchlistHistoryGateway

app = Flask(__name__, template_folder='frontend')
app.secret_key = 'animelist_secret_key'

db = DatabaseConnection()
anime_gw = AnimeGateway()
user_gw = UserGateway()
genre_gw = GenreGateway()
anime_genre_gw = AnimeGenreGateway()
watchlist_entry_gw = WatchlistEntryGateway()
watchlist_history_gw = WatchlistHistoryGateway()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/anime')
def anime_list():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anime_with_genres_view")
    anime = cursor.fetchall()
    cursor.close()
    return render_template('anime.html', anime=anime)


@app.route('/anime/add', methods=['GET', 'POST'])
def anime_add():
    if request.method == 'POST':
        title_romaji = request.form['title_romaji']
        title_english = request.form.get('title_english') or None
        episodes = int(request.form.get('episodes') or 0)
        status = request.form['status']
        start_date = request.form.get('start_date') or None
        external_score = float(request.form['external_score']) if request.form.get('external_score') else None
        genre_ids = request.form.getlist('genres')
        
        try:
            new_id = anime_gw.insert(title_romaji, status, title_english, episodes, start_date, external_score)
            for genre_id in genre_ids:
                anime_genre_gw.insert(new_id, int(genre_id))
            flash(f'Anime added successfully with ID: {new_id}', 'success')
            return redirect(url_for('anime_list'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    
    genres = genre_gw.select_all()
    return render_template('anime_add.html', genres=genres)


@app.route('/users')
def user_list():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('users.html', users=users)


@app.route('/users/add', methods=['GET', 'POST'])
def user_add():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        is_admin = 'is_admin' in request.form
        
        try:
            new_id = user_gw.insert(username, email, is_admin)
            flash(f'User added successfully with ID: {new_id}', 'success')
            return redirect(url_for('user_list'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    
    return render_template('user_add.html')


@app.route('/genres')
def genre_list():
    genres = genre_gw.select_all()
    return render_template('genres.html', genres=genres)


@app.route('/genres/add', methods=['GET', 'POST'])
def genre_add():
    if request.method == 'POST':
        name = request.form['name']
        
        try:
            new_id = genre_gw.insert(name)
            flash(f'Genre added successfully with ID: {new_id}', 'success')
            return redirect(url_for('genre_list'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    
    return render_template('genre_add.html')


@app.route('/watchlist')
def watchlist():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_watchlist_view")
    entries = cursor.fetchall()
    cursor.close()
    return render_template('watchlist.html', entries=entries)


@app.route('/watchlist/add', methods=['GET', 'POST'])
def watchlist_add():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        anime_id = int(request.form['anime_id'])
        status = request.form['status']
        score = int(request.form['score']) if request.form.get('score') else None
        progress = int(request.form.get('progress') or 0)
        
        try:
            watchlist_entry_gw.insert(user_id, anime_id, status, score, progress)
            flash('Watchlist entry added successfully', 'success')
            return redirect(url_for('watchlist'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT id, title_romaji FROM anime")
    anime = cursor.fetchall()
    cursor.close()
    return render_template('watchlist_add.html', users=users, anime=anime)


@app.route('/history')
def history_list():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('history_list.html', users=users)


@app.route('/history/<int:user_id>')
def history(user_id):
    entries = watchlist_history_gw.select_by_user_id(user_id)
    return render_template('history.html', entries=entries, user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
