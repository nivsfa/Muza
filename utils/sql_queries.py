""""

    Creating all the sql queries

"""


def get_songs_dict(conn):
    """
        Gets a dictionary representation of the songs stored in the database

    Parameters:
        conn (sqlite3 connection object): connection object to sqlite database

    Returns:
        dict: A dictionary mapping song names to list of tuples, where each tuple represents a line in the song and
              contains the line number and the text of the line
    """
    songs_list = conn.execute("SELECT s.title, s.id from song s").fetchall()
    songs_names = conn.execute("SELECT s.title from song s").fetchall()
    songs_names = list(map(lambda x: x[0], songs_names))
    id2name = {k: v for v, k in songs_list}
    songs = {k: [] for k in songs_names}
    songs_text = conn.execute("SELECT l.song_id, l.line_num, l.line from line l").fetchall()
    for line in songs_text:
        songs[id2name[line[0]]].append((line[1], line[2]))

    return songs


def update_parameters_table(conn, song_name):
    """
        Updates the parameters' table in the database with the latest song id

    Parameters:
        conn (sqlite3 connection object): connection object to an sqlite database.
        song_name (str): the name of the song to be set as the latest song.

    Returns:
        None
    """
    songs_list = conn.execute("SELECT s.title, s.id from song s").fetchall()
    name2id = {v: k for v, k in songs_list}
    conn.execute("UPDATE parameters SET last_song_id =? WHERE id = 1", (name2id[song_name],))
    conn.commit()


def update_title(conn, new_title):
    """

     Updates the title of the latest song in the database

    Parameters:
        conn (sqlite3 connection object): connection object to sqlite database
        new_title (str): the new title for the latest song

    Returns:
        None
    """
    song_id = conn.execute("SELECT p.last_song_id from parameters p").fetchall()[0][0]
    conn.execute("UPDATE song SET title=? WHERE id=?", (new_title, song_id))
    conn.commit()


def update_line(conn, new_line, line_num):
    """
        Updates a specific line of the latest song in the database

    Parameters:
        conn (sqlite3 connection object): connection object to sqlite database
        new_line (str): the new line to replace the existing line
        line_num (int): the number of the line to be updated

    Returns:
        None
    """
    song_id = conn.execute("SELECT p.last_song_id from parameters p").fetchall()[0][0]
    conn.execute("UPDATE line SET line=? WHERE song_id=? and line_num=?", (new_line, song_id, line_num))
    conn.commit()


def upload_new_song(conn, title, genre, inspiration):
    """
        Uploads a new song to the database with the given title, genre and inspiration.

    Parameters:
        conn (sqlite3.connect): The connection to the database.
        title (str): The title of the new song.
        genre (str): The genre of the new song.
        inspiration (str): The inspiration for the new song.

    Returns:
        None
    """
    song_id = conn.execute("SELECT MAX(s.id) from song s").fetchall()[0][0] + 1
    conn.execute("INSERT INTO song (id, title, genre, inspiration) VALUES(?,?,?,?)",
                 (song_id, title, genre, inspiration))
    conn.commit()

