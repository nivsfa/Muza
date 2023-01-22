from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import sqlite3
import openai

# Set the API key
openai.api_key = "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"

app = Flask(__name__, template_folder='templates', static_folder='static')

model_engine = "text-davinci-003"
conn = sqlite3.connect('muza_database.sqlite', check_same_thread=False)
cur = conn.cursor()


def get_data():
    songs_list = cur.execute("SELECT s.title, s.id from song s").fetchall()
    songs_names = cur.execute("SELECT s.title from song s").fetchall()
    songs_names = list(map(lambda x: x[0], songs_names))
    id2name = {k: v for v, k in songs_list}
    name2id = {k: v for k, v in songs_list}
    songs_text = cur.execute("SELECT l.song_id, l.line_num, l.line from line l").fetchall()
    songs = {k: [] for k in songs_names}
    for line in songs_text:
        songs[id2name[line[0]]].append((line[1], line[2]))
    return songs_list, songs_names, id2name, name2id, songs_text, songs


songs_list, songs_names, id2name, name2id, songs_text, songs = get_data()


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
    ending_words = request.args.get("ending_words")
    keywords = request.args.get("keywords")
    uniqueness = request.args.get("uniqueness")
    rhyme = request.args.get("rhyme")
    add_emotion = request.args.get("add_emotion")
    emotion = request.args.get("emotion")
    lyrics = cur.execute("SELECT l.line from line l where l.song_id=?", str(song_id)).fetchall()
    genre, inspiration, title = cur.execute("SELECT s.genre, s.inspiration, s.title from song s where s.id=?",
                                            str(song_id)).fetchall()[0]
    rhyme = '' if rhyme == 'false' else ' make it rhyme,'
    emotion = '' if add_emotion == 'false' else f' make it {emotion},'
    genre = '' if genre == 'Enter genre' or genre == 'Undetermined' else f' make it with {genre} genre'
    ending_words = '' if len(ending_words) == 0 else f'use one of these words at the end of the line: {ending_words},'
    keywords = '' if len(keywords) == 0 else f' use these keywords words: {keywords},'
    return song_id, line_num, ending_words, keywords, uniqueness, rhyme, add_emotion, emotion, lyrics, \
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
        print(request.form)
        if "add_song_button" in request.form:
            return render_template('add_new_song.html', songs=songs)

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
    song_id, line_num, ending_words, keywords, uniqueness, rhyme, add_emotion, emotion, lyrics, \
    genre, inspiration, title = get_prompt_parameters()
    lyrics.pop(line_num)
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    if len(lyrics) == 0:
        prompt = f"Generate a short first line in a song," \
                 f"{rhyme}{emotion}{genre}{ending_words}{keywords}"
    elif line_num == 0:
        prompt = f"Given the following song, generate a short first line," \
                 f"{rhyme}{emotion}{genre}{ending_words}{keywords}\n" \
                 f'"{lyrics}"'
    elif len(lyrics) == line_num:
        prompt = f"Given the following song, generate a one short line at the end of the song," \
                 f"{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f'"{lyrics}"'
    else:
        prompt = f"Given the following song, generate one short line between line {line_num} and {line_num + 1}," \
                 f"{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f'"{lyrics}"'
    print(prompt)
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=float(uniqueness),
    )
    return jsonify(text=completions.choices[0].text.lstrip('"\'.').rstrip('"\'.'))


@app.route('/complete')
def complete():
    song_id, line_num, ending_words, keywords, uniqueness, rhyme, add_emotion, emotion, lyrics, \
    genre, inspiration, title = get_prompt_parameters()
    ending_words = '' if len(ending_words) == 0 else ', ' + ending_words
    line = lyrics[line_num][0]
    lyrics.pop(line_num)
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    if len(lyrics) == 0:
        prompt = f"Complete the following line as short first line in a song," \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f"{line}"
    elif line_num == 0:
        prompt = f"Complete the following line as short first line in a song," \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}\n" \
                 f'"{line}"' + f"And given the following song: \n" + f'"{lyrics}"'
    elif len(lyrics) == line_num:
        prompt = f"Complete the following line: \n" \
                 f'"{line}" \n' \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f"And given the following song: \n" + f'"{lyrics}"'
    else:
        prompt = f"Complete the following line between line {line_num} and {line_num + 1}: \n" \
                 f'"{line}" \n' \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f"And given the following song: \n" + f'"{lyrics}"'
    print(prompt)
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=float(uniqueness),
    )
    return jsonify(text=completions.choices[0].text.lstrip('"\'.').rstrip('"\'.'))


@app.route('/rephrase')
def rephrase():
    song_id, line_num, ending_words, keywords, uniqueness, rhyme, add_emotion, emotion, lyrics, \
    genre, inspiration, title = get_prompt_parameters()
    ending_words = '' if len(ending_words) == 0 else ', ' + ending_words
    line = lyrics[line_num][0]
    lyrics.pop(line_num)
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    if len(lyrics) == 0:
        prompt = f"Rephrase the following line as short first line in a song," \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f"{line}"
    elif line_num == 0:
        prompt = f"Rephrase the following line as short first line in a song," \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}\n" \
                 f'"{line}"' + f"And given the following song: \n" + f'"{lyrics}"'
    elif len(lyrics) == line_num:
        prompt = f"Rephrase the following line: \n" \
                 f'"{line}" \n' \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f"And given the following song: \n" + f'"{lyrics}"'
    else:
        prompt = f"Rephrase the following line between line {line_num} and {line_num + 1}: \n" \
                 f'"{line}" \n' \
                 f"Also,{rhyme}{emotion}{genre}{ending_words}{keywords}:\n" \
                 f"And given the following song: \n" + f'"{lyrics}"'
    print(prompt)
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=float(uniqueness),
    )
    return jsonify(text=completions.choices[0].text.lstrip('"\'.').rstrip('"\'.'))


@app.route('/save_row')
def save_row():
    line_text = request.args.get("line_text")
    line_num = int(request.args.get("line_num"))
    song_id = cur.execute("SELECT p.last_song_id from parameters p").fetchall()[0][0]
    cur.execute("UPDATE line SET line = ? WHERE song_id = ? AND line_num = ?", (line_text, song_id, line_num))
    conn.commit()
    return 'None'


@app.route('/song/<song_name>', methods=['GET', 'POST'])
def song(song_name):
    cur.execute("UPDATE parameters SET last_song_id =? WHERE id = 1", (name2id[song_name],))
    conn.commit()
    if request.method == 'GET':
        return render_template('song.html', song_name=song_name, text=songs[song_name], songs=songs)

    if request.method == 'POST':
        if "add_song_button" in request.form:
            return redirect(url_for('add_new_song'))
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


if __name__ == '__main__':
    app.run(debug=True)
