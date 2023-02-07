from flask import Flask, render_template, redirect, url_for
from utils.sql_queries import *
from utils.prompts import *
import openai
import sqlite3

""""
    Here you can run the Flask application. 
    If you want to test our AI model, please add your openai key below.


--------------------------------- Put here your openai key ------------------------------------
"""

openai.api_key = "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"

""""
-----------------------------------------------------------------------------------------------
"""

app = Flask(__name__, template_folder='templates', static_folder='static')
model_engine = "text-davinci-003"


def get_db_connection():
    """
        Creates a connection to an SQLite database file named 'muza_database.sqlite' using the sqlite3 module.

        Returns:
            sqlite connection object
    """
    conn = sqlite3.connect('muza_database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    """
        This is the main route of the application.
        If the request method is POST, it redirects to the add_song route.

        Returns:
            index.html page
    """
    conn = get_db_connection()
    songs = get_songs_dict(conn)
    conn.close()
    if request.method == 'POST':
        return redirect(url_for('add_song'))
    return render_template('index.html', songs=songs)


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    """
        This route add new songs to the database.

        If the request method is POST, it handles two possible actions:
            - If the user clicked on "add_song_button", the 'add_song.html' template is rendered with the song list.
            - If the user clicked on "submit" button, a new song is uploaded to the database,
              and the user is redirected to the song route with the newly added song name.

            Returns:
            add_song.html page
    """
    conn = get_db_connection()
    songs = get_songs_dict(conn)
    conn.close()
    if request.method == 'POST':
        if "add_song_button" in request.form:
            return render_template('add_song.html', songs=songs)

        if "submit" in request.form:
            song_name = request.form['song_name']
            conn = get_db_connection()
            upload_new_song(conn, song_name, request.form['genre'], request.form['inspiration'])
            songs = get_songs_dict(conn)
            conn.close()
            return redirect(url_for('song', song_name=song_name, songs=songs))

    return render_template('add_song.html', songs=songs)


@app.route('/song/<song_name>', methods=['GET', 'POST'])
def song(song_name):
    """
        This route is for viewing, editing, and saving changes to a song's title and lyrics.
        The song to display is specified by the `song_name` parameter in the URL path.

        If the request method is POST, the following actions can be performed based on the form data:
        - Adding a new song (by clicking the 'add_song_button') will redirect to the 'add_song' route
        - Saving changes to the song title (by clicking the 'save_title' button) will update the title
          in the database and redisplay the song page with the updated title
        - Saving changes to a line of lyrics (by clicking the 'save_line' button) will update the line
          in the database and redisplay the song page with the updated lyrics

        Parameters:
            song_name (str): The name of the selected song

        Returns:
            song.html page
    """
    conn = get_db_connection()
    songs = get_songs_dict(conn)
    update_parameters_table(conn, song_name)
    conn.close()
    if request.method == 'POST':
        if "add_song_button" in request.form:
            return render_template('add_song.html', songs=songs)
        if "save_title" in request.form:
            conn = get_db_connection()
            new_title = request.form['new_title']
            update_title(conn, new_title)
            songs = get_songs_dict(conn)
            conn.close()
            song_name = new_title
            return render_template('song.html', song_name=song_name, text=songs[new_title], songs=songs)
        if any(['save_line' in key for key in request.form.keys()]):
            for key in request.form.keys():
                if 'save_line' in key:
                    line_num = key.split('-')[-1]
            conn = get_db_connection()
            line = request.form['text-'+line_num]
            update_line(conn, line, line_num)
            songs = get_songs_dict(conn)
            conn.close()
            return render_template('song.html', song_name=song_name, text=songs[song_name], songs=songs)
    return render_template('song.html', song_name=song_name, text=songs[song_name], songs=songs)


@app.route('/generate_title')
def generate_title():
    """
        Generates a new title given the current song

        Returns:
            The generated title by gpt3
    """
    conn = get_db_connection()
    s = get_ai_sentence(conn=conn, prompt_func=generate_title_prompt, model_engine=model_engine, openai=openai)
    conn.close()
    return s


@app.route('/generate')
def generate():
    """
        Generates a new line given the current song

        Returns:
            The generated sentence by gpt3
    """
    conn = get_db_connection()
    s = get_ai_sentence(conn=conn, prompt_func=generate_line_prompt, model_engine=model_engine, openai=openai)
    conn.close()
    return s


@app.route('/complete')
def complete():
    """
        Completes a line given the current line & song

        Returns:
            The generated sentence by gpt3
    """
    conn = get_db_connection()
    s = get_ai_sentence(conn=conn, prompt_func=complete_line_prompt, model_engine=model_engine, openai=openai)
    conn.close()
    return s


@app.route('/rephrase')
def rephrase():
    """
        Rephrases a line given the current line & song

        Returns:
            The generated sentence by gpt3
    """
    conn = get_db_connection()
    s = get_ai_sentence(conn=conn, prompt_func=rephrase_line_prompt, model_engine=model_engine, openai=openai)
    conn.close()
    return s


if __name__ == '__main__':
    app.run(debug=False)
