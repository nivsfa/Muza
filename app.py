from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import sqlite3
import openai
from copy import deepcopy

# Set the API key
openai.api_key = "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"

app = Flask(__name__, template_folder='templates', static_folder='static')

model_engine = "text-davinci-002"
# model_engine = 'text-ada-001'
songs = {}
conn = sqlite3.connect('muza_database.sqlite', check_same_thread=False)
cur = conn.cursor()

songs_list = cur.execute("SELECT s.title, s.id from song s").fetchall()
songs_names = cur.execute("SELECT s.title from song s").fetchall()
songs_names = list(map(lambda x: x[0], songs_names))
id2name = {k: v for v, k in songs_list}
name2id = {k: v for k, v in songs_list}
songs_text = cur.execute("SELECT l.song_id, l.line_num, l.line from line l").fetchall()
songs = {k: [] for k in songs_names}
for line in songs_text:
    songs[id2name[line[0]]].append((line[1], line[2]))


def add_song_record(title, genre, inspiration):
    id = cur.execute("SELECT COUNT(*) from song").fetchall()[0][0]
    if title in songs_names:
        title = title + '+'
    cur.execute("INSERT INTO song (id, title, genre, inspiration) \
          VALUES (?, ?, ?, ?)", (id, title, genre, inspiration))
    conn.commit()
    name2id[title] = id
    id2name[id] = title
    songs[title] = []


def get_prompt_parameters():
    song_id = cur.execute("SELECT p.last_song_id from parameters p").fetchall()[0][0]
    line_num = int(request.args.get("line_num"))
    words_num = int(request.args.get("words_num"))
    add_words_num = request.args.get("add_words_num")
    add_max_words = request.args.get("add_max_words")
    max_words = int(request.args.get("max_words"))
    uniqueness = request.args.get("uniqueness")
    rhyme = request.args.get("rhyme")
    add_emotion = request.args.get("add_emotion")
    emotion = request.args.get("emotion")
    lyrics = cur.execute("SELECT l.line from line l where l.song_id=?", str(song_id)).fetchall()
    genre, inspiration, title = cur.execute("SELECT s.genre, s.inspiration, s.title from song s where s.id=?",
                                            str(song_id)).fetchall()[0]
    return song_id, line_num, words_num, add_words_num, add_max_words, max_words, uniqueness, rhyme, add_emotion, emotion, lyrics, \
           genre, inspiration, title


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


@app.route('/generate')
def generate():
    song_id, line_num, words_num, add_words_num, add_max_words, max_words, uniqueness, rhyme, add_emotion, emotion, \
    lyrics, genre, inspiration, title = get_prompt_parameters()
    lyrics.pop(line_num)
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    print(add_words_num)

    number_of_words = '' if add_words_num != 'on' else f' with {words_num} words,'
    max_number_of_words = max_words if add_max_words == 'on' and add_words_num != 'on' else 15
    rhyme = '' if rhyme != 'on' else ' make it rhyme,'
    rhyme = ' make it rhyme,'
    emotion = '' if add_emotion != 'on' else f' make it {emotion},'
    genre = '' if genre == 'Enter genre' or genre == 'Undetermined' else f' make it with {genre} genre'
    first_or_new = 'the first' if len(lyrics) == 0 else 'one'
    add_line = f'for a song with the "{title}" title' if len(lyrics) == 0 \
        else f"between line {line_num} and {line_num + 1} in the following song: \n{lyrics}"

    if len(lyrics) == 0:
        prompt = ""
    else:
        prompt = f"Given the following song, generate one line between line {line_num} and {line_num+1}," \
                 f"{number_of_words}{rhyme}{emotion}{genre}:\n" \
                 f'"{lyrics}"'

    print(prompt)

    # lyrics = lyrics[line_num-1:line_num+1]
    # lyrics.pop(1)
    # lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    # generate_prompt = f'", generate a new line between these two lines. Make it rhyme, and make it start ' \
    #                   f'with the first word of the first line." '
    #
    # prompt = 'Given the song "' \
    #          + lyrics + \
    #          generate_prompt
    print(max_number_of_words)
    print(float(uniqueness))
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=float(uniqueness),
    )
    # return jsonify(text='generate')
    return jsonify(text=completions.choices[0].text)


@app.route('/complete')
def complete():
    song_id, line_num, words_num, add_words_num, add_max_words, max_words, uniqueness, rhyme, add_emotion, emotion, \
    lyrics, genre, inspiration, title = get_prompt_parameters()
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    return jsonify(text="And if you want to eat a fish, it's free in every nation")


@app.route('/rephrase')
def rephrase():
    song_id, line_num, words_num, add_words_num, add_max_words, max_words, uniqueness, rhyme, add_emotion, emotion, \
    lyrics, genre, inspiration, title = get_prompt_parameters()
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    return jsonify(text="And if you want to dream like this, it's USA-ization")


@app.route('/upload_line')
def upload_line(line, line_id, song_title):
    i = random.random()
    return jsonify(text=f"This is the generated text. {i}")


@app.route('/song/<song_name>', methods=['GET', 'POST'])
def song(song_name):
    cur.execute("UPDATE parameters SET last_song_id =? WHERE id = 1", (name2id[song_name],))
    conn.commit()
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
