from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')

songs = {}
conn = sqlite3.connect('muza_database.sqlite',  check_same_thread=False)
cur = conn.cursor()


def add_song_record(title, genre, inspiration):
    id = cur.execute("SELECT COUNT(*) from song").fetchall()[0][0]
    cur.execute("INSERT INTO song (id, title, genre, inspiration) \
          VALUES (?, ?, ?, ?)", (id, title, genre, inspiration))
    conn.commit()


def add_line_song_record(title, line_num, words_num, max_words_num, uniqueness, rhyme, emotion):
    id = cur.execute("SELECT s.id from song s WHERE s.title = ?", title)
    cur.execute("INSERT INTO line (song_id, line_num, words_num, max_words_num, uniqueness, rhyme, emotion) \
          VALUES (?, ?, ?, ?, ?, ?, ?)", (id, line_num, words_num, max_words_num, uniqueness, rhyme, emotion))
    conn.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('add_new_song'))
    return render_template('index.html', songs=songs)


@app.route('/add_new_song', methods=['GET', 'POST'])
def add_new_song():
    if request.method == 'POST':
        # Get the song name from the form
        song_name = request.form['song_name']
        genre = request.form['genre']
        inspiration = request.form['inspiration']
        add_song_record(song_name, genre, inspiration)
        # Add the new song to the songs dictionary
        songs[song_name] = ''
        # Redirect to the new song page using the song name
        return redirect(url_for('song', song_name=song_name))

    # show the form, it wasn't submitted
    return render_template('add_new_song.html', songs=songs)


@app.route('/get_text')
def get_text():
    i = random.random()
    return jsonify(text=f"This is the generated text. {i}")


@app.route('/upload_line')
def upload_line(line, line_id, song_title):
    i = random.random()
    return jsonify(text=f"This is the generated text. {i}")


@app.route('/song/<song_name>', methods=['GET', 'POST'])
def song(song_name):
    if request.method == 'POST':
        # if request.form.get("generate"):
        #     generated_text = 'generated text'  # function that returns the generated text
        #     return render_template('song.html', generated_text=generated_text,
        #                            song_name=song_name, text=songs[song_name], songs=songs)
        if 'save' in request.form:
            # Read the text from the textarea
            text = request.form['text']
            # Save the changes made to the song
            songs[song_name] = text
            # Redisplay the song page with the updated text
            return render_template('song.html', song_name=song_name, text=songs[song_name], songs=songs)
        elif 'add_song' in request.form:
            # Add a new song and redirect to the new song page
            new_song_name = request.form['song_name']
            songs[new_song_name] = ''
            return redirect(url_for('song', song_name=new_song_name))
    return render_template('song.html', song_name=song_name, text=songs[song_name], songs=songs)

# @app.route('/song/<song_title>', methods=['GET', 'POST'])
# def song(song_title):
#     # Render the song page with the song title, genre, and inspiration
#     return render_template('song.html', song_title=song_title)

# @app.route('/song/<song_name>/add-line', methods=['POST'])
# def add_line(song_name):
#     line = request.form['line']
#     # Save the line to a variable here
#     return 'Success'


if __name__ == '__main__':
    app.run(debug=True)