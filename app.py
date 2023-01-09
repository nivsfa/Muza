from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='templates', static_folder='static')

songs = {}


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
        # Add the new song to the songs dictionary
        songs[song_name] = ''
        # Redirect to the new song page using the song name
        return redirect(url_for('song', song_name=song_name))

    # show the form, it wasn't submitted
    return render_template('add_new_song.html', songs=songs)


@app.route('/song/<song_name>', methods=['GET', 'POST'])
def song(song_name):
    if request.method == 'POST':
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
    app.run()