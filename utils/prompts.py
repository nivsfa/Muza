from flask import request

""""

    Creating all the prompts that are sent to gpt3

"""""


def get_prompt_parameters(conn):
    """
        This function retrieves parameters for song generation prompt from a SQL database connection.

        Parameters:
            conn (sqlite3.Connection): A connection to a SQLite database

        Returns:
            dict: A dictionary containing the parameters for the song generation prompt, including:
                - song_id (int): The id of the last song used
                - line_num (int): The number of lines to generate
                - ending_words (str): A string of words to use at the end of the lines
                - keywords (str): A string of keywords to include in the generated lines
                - uniqueness (float): the uniqueness generation level: between 0 and 1
                - rhyme (bool): A boolean indicating whether the lines should rhyme or not
                - add_emotion (bool): A boolean indicating whether the lines should have an added emotion
                - emotion (str): A string indicating the emotion to add to the lines
                - lyrics (list): A list of strings, each representing a line of the song
                - genre (str): A string indicating the genre of the song
                - inspiration (str): A string indicating the inspiration artist for the song
                - title (str): A string representing the title of the song
                - sentence (str): A string representing a line that we want to modify in the song
        """
    song_id = conn.execute("SELECT p.last_song_id from parameters p").fetchall()[0][0]
    try:
        line_num = int(request.args.get("line_num"))
    except:
        line_num = 0
    ending_words = request.args.get("ending_words")
    keywords = request.args.get("keywords")
    uniqueness = request.args.get("uniqueness")
    rhyme = request.args.get("rhyme")
    add_emotion = request.args.get("add_emotion")
    emotion = request.args.get("emotion")
    sentence = request.args.get("sentence")
    lyrics = conn.execute("SELECT l.line from line l where l.song_id=?", str(song_id)).fetchall()
    genre, inspiration, title = conn.execute("SELECT s.genre, s.inspiration, s.title from song s where s.id=?",
                                             str(song_id)).fetchall()[0]
    try:
        rhyme = '' if rhyme == 'false' else ' make it rhyme,'
        emotion = '' if add_emotion == 'false' else f' make it {emotion},'
        inspiration = '' if inspiration == 'Undetermined' else f' and inspired by the {inspiration} artist'
        genre = '' if genre == 'Enter genre' or genre == 'Undetermined' else f' make it with {genre} genre'
        ending_words = '' if len(
            ending_words) == 0 else f'use one of these words at the end of the line: {ending_words},'
        keywords = '' if len(keywords) == 0 else f' use these keywords words: {keywords},'
    except:
        pass
    params = {"song_id": song_id, "line_num": line_num, "ending_words": ending_words, "keywords": keywords,
              "uniqueness": uniqueness, "rhyme": rhyme, "add_emotion": add_emotion, "emotion": emotion,
              "lyrics": lyrics, "genre": genre, "inspiration": inspiration, "title": title, "sentence": sentence}
    return params


def generate_line_prompt(conn):
    """
        This function generates a prompt to write a line in a song

        Parameters:
            conn (sqlite3.Connection): A connection to a SQLite database

        Returns:
            str: A string prompt to write a line in the song
    """
    p = get_prompt_parameters(conn)
    lyrics = p["lyrics"]
    lyrics.pop(p["line_num"])
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    if len(lyrics) == 0:
        return f"Generate a short first line in a song," \
               f"{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}"
    elif p["line_num"] == 0:
        return f"Given the following song, generate a short first line," \
               f"{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}" \
               f'"{lyrics}"'
    elif len(lyrics) == p["line_num"]:
        return f"Given the following song, generate a one short line at the end of the song," \
               f"{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']} :\n" \
               f'"{lyrics}"'
    return f"Given the following song, generate one short line between line {p['line_num']} and {p['line_num'] + 1}," \
           f"{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']} :\n" \
           f'"{lyrics}"'


def complete_line_prompt(conn):
    """
    This function returns a string that represents the prompt to complete a line in a song

    Parameters:
        conn (sqlite3.Connection): A connection to a SQLite database

    Returns:
        str: A string prompt to write a line in the song
    """
    p = get_prompt_parameters(conn)
    p['ending_words'] = '' if len(p['ending_words']) == 0 else ', ' + p['ending_words']
    line = p['sentence']
    lyrics = p['lyrics']
    lyrics.pop(p['line_num'])
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    line = " ".join(line.split(" ")[:4])

    if len(lyrics) == 0:
        return f"Complete the following line as short first line in a song," \
               f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}:\n" \
               f"{line}"
    elif p['line_num'] == 0:
        return f"Complete the following line as short first line in a song," \
               f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}\n" \
               f'"{line}"' + f"And given the following song: \n" + f'"{lyrics}"'
    elif len(lyrics) == p['line_num']:
        return f"Complete the following line: \n" \
               f'"{line}" \n' \
               f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}:\n" \
               f"And given the following song: \n" + f'"{lyrics}"'
    return f"Complete the following line between line {p['line_num']} and {p['line_num'] + 1}: \n" \
           f'"{line}" \n' \
           f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}:\n" \
           f"And given the following song: \n" + f'"{lyrics}"'


def rephrase_line_prompt(conn):
    """
        This function generates a prompt for rephrasing a line in a song

    Parameters:
        conn (sqlite3.Connection): A connection to a SQLite database

    Returns:
        str: A string prompt to write a line in the song
    """
    p = get_prompt_parameters(conn)
    p['ending_words'] = '' if len(p['ending_words']) == 0 else ', ' + p['ending_words']
    line = p['sentence']
    lyrics = p['lyrics']
    lyrics.pop(p['line_num'])
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    if len(lyrics) == 0:
        return f"Rephrase to one short line the following line as the first line in a song," \
               f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}:\n" \
               f"{line}"
    elif p['line_num'] == 0:
        return f"Rephrase to one short line the following line as the first line in a song," \
               f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}\n" \
               f'"{line}"' + f"And given the following song: \n" + f'"{lyrics}"'
    elif len(lyrics) == p['line_num']:
        return f"Rephrase to one short line the following line: \n" \
               f'"{line}" \n' \
               f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}:\n" \
               f"And given the following song: \n" + f'"{lyrics}"'
    return f"Rephrase to one short line the following line between line {p['line_num']} and {p['line_num'] + 1}: \n" \
           f'"{line}" \n' \
           f"Also,{p['rhyme']}{p['emotion']}{p['genre']}{p['inspiration']}{p['ending_words']}{p['keywords']}:\n" \
           f"And given the following song: \n" + f'"{lyrics}"'


def generate_title_prompt(conn):
    """
        This function generates a prompt for a song title

    Parameters:
        conn (sqlite3.Connection): A connection to a SQLite database

    Returns:
        str: The prompt for the song title

    """
    p = get_prompt_parameters(conn)
    song_id = conn.execute("SELECT p.last_song_id from parameters p").fetchall()[0][0]
    genre, inspiration, title = conn.execute("SELECT s.genre, s.inspiration, s.title from song s where s.id=?",
                                             str(song_id)).fetchall()[0]
    genre = '' if genre == 'Enter genre' or genre == 'Undetermined' else f'from {genre} genre'
    lyrics = p["lyrics"]
    lyrics = '\n'.join(list(map(lambda x: x[0], lyrics)))
    if len(lyrics) == 0:
        return f"Generate a short title for a song" \
               f" {genre}"

    return f"Given the following song, generate a short title {genre}: \n" \
           f'"{lyrics}"'


def get_ai_sentence(conn, prompt_func, model_engine, openai):
    """
        Gets a sentence for a given prompt from the OpenAI API

    Parameters:
        conn (sqlite3 connection object): connection object to an sqlite database
        prompt_func (function): A function that generates the prompt text
        model_engine (str): The ID of the OpenAI engine to use
        openai (OpenAI client object): An authenticated client to the OpenAI API

    Returns:
        str: A string representing the completed sentence based on the prompt

    """
    prompt = prompt_func(conn)
    uniqueness = request.args.get("uniqueness")
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=float(uniqueness),
    )
    return completions.choices[0].text.replace('\n', '').replace('"', '').replace('\'', '').replace('.', '')