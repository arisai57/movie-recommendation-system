from typing import Tuple, List, Set

def clear_database(mydb):
    cursor = mydb.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM song_genre")
    cursor.execute("DELETE FROM ratings")
    cursor.execute("DELETE FROM songs")
    cursor.execute("DELETE FROM albums")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM genres")
    cursor.execute("DELETE FROM artists")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    mydb.commit()


def get_id(cursor, table, column, value):
    query = "SELECT id FROM " + table + " WHERE " + column + " = %s"
    cursor.execute(query, (value,))
    row = cursor.fetchone()
    if row == None:
        return None
    return row[0]


def load_single_songs(mydb, single_songs):
    cursor = mydb.cursor()
    rejects = set()

    for song, genres, artist, date in single_songs:
        artist_id = get_id(cursor, "artists", "name", artist)

        if artist_id == None:
            cursor.execute("INSERT INTO artists (name) VALUES (%s)", (artist,))
            artist_id = cursor.lastrowid

        cursor.execute("SELECT id FROM songs WHERE title = %s AND artist_id = %s", (song, artist_id))
        if cursor.fetchone() != None:
            rejects.add((song, artist))
            continue

        cursor.execute(
            "INSERT INTO songs (title, artist_id, album_id, song_release) VALUES (%s, %s, NULL, %s)",
            (song, artist_id, date)
        )
        song_id = cursor.lastrowid

        for genre in genres:
            genre_id = get_id(cursor, "genres", "name", genre)

            if genre_id == None:
                cursor.execute("INSERT INTO genres (name) VALUES (%s)", (genre,))
                genre_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO song_genre (song_id, genre_id) VALUES (%s, %s)",
                (song_id, genre_id)
            )

    mydb.commit()
    return rejects


def get_most_prolific_individual_artists(mydb, n, year_range):
    cursor = mydb.cursor()
    cursor.execute("""
        SELECT a.name, COUNT(*)
        FROM artists a, songs s
        WHERE a.id = s.artist_id
        AND s.album_id IS NULL
        AND YEAR(s.song_release) BETWEEN %s AND %s
        GROUP BY a.id, a.name
        ORDER BY COUNT(*) DESC, a.name ASC
        LIMIT %s
    """, (year_range[0], year_range[1], n))
    return cursor.fetchall()


def get_artists_last_single_in_year(mydb, year):
    cursor = mydb.cursor()
    cursor.execute("""
        SELECT a.name
        FROM artists a, songs s
        WHERE a.id = s.artist_id
        AND s.album_id IS NULL
        GROUP BY a.id, a.name
        HAVING YEAR(MAX(s.song_release)) = %s
    """, (year,))
    result = set()
    for row in cursor.fetchall():
        result.add(row[0])
    return result


def load_albums(mydb, albums):
    cursor = mydb.cursor()
    rejects = set()

    for album, genre, artist, date, songs in albums:
        artist_id = get_id(cursor, "artists", "name", artist)

        if artist_id == None:
            cursor.execute("INSERT INTO artists (name) VALUES (%s)", (artist,))
            artist_id = cursor.lastrowid

        cursor.execute("SELECT id FROM albums WHERE title = %s AND artist_id = %s", (album, artist_id))
        if cursor.fetchone() != None:
            rejects.add((album, artist))
            continue

        genre_id = get_id(cursor, "genres", "name", genre)

        if genre_id == None:
            cursor.execute("INSERT INTO genres (name) VALUES (%s)", (genre,))
            genre_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO albums (title, artist_id, album_release, genre_id) VALUES (%s, %s, %s, %s)",
            (album, artist_id, date, genre_id)
        )
        album_id = cursor.lastrowid

        for song in songs:
            cursor.execute("SELECT id FROM songs WHERE title = %s AND artist_id = %s", (song, artist_id))
            row = cursor.fetchone()

            if row != None:
                continue

            cursor.execute(
                "INSERT INTO songs (title, artist_id, album_id, song_release) VALUES (%s, %s, %s, %s)",
                (song, artist_id, album_id, date)
            )
            song_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO song_genre (song_id, genre_id) VALUES (%s, %s)",
                (song_id, genre_id)
            )

    mydb.commit()
    return rejects


def get_top_song_genres(mydb, n):
    cursor = mydb.cursor()
    cursor.execute("""
        SELECT g.name, COUNT(*)
        FROM genres g, song_genre sg
        WHERE g.id = sg.genre_id
        GROUP BY g.id, g.name
        ORDER BY COUNT(*) DESC, g.name ASC
        LIMIT %s
    """, (n,))
    return cursor.fetchall()


def get_album_and_single_artists(mydb):
    cursor = mydb.cursor()
    cursor.execute("""
        SELECT DISTINCT a.name
        FROM artists a, albums al, songs s
        WHERE a.id = al.artist_id
        AND a.id = s.artist_id
        AND s.album_id IS NULL
    """)
    result = set()
    for row in cursor.fetchall():
        result.add(row[0])
    return result


def load_users(mydb, users):
    cursor = mydb.cursor()
    rejects = set()

    for username in users:
        user_id = get_id(cursor, "users", "username", username)

        if user_id != None:
            rejects.add(username)
        else:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))

    mydb.commit()
    return rejects


def load_song_ratings(mydb, song_ratings):
    cursor = mydb.cursor()
    rejects = set()

    for username, artist_song, rating, date in song_ratings:
        artist = artist_song[0]
        song = artist_song[1]

        if rating < 1 or rating > 5:
            rejects.add((username, artist, song))
            continue

        user_id = get_id(cursor, "users", "username", username)
        if user_id == None:
            rejects.add((username, artist, song))
            continue

        artist_id = get_id(cursor, "artists", "name", artist)
        if artist_id == None:
            rejects.add((username, artist, song))
            continue

        cursor.execute("SELECT id FROM songs WHERE title = %s AND artist_id = %s", (song, artist_id))
        row = cursor.fetchone()
        if row == None:
            rejects.add((username, artist, song))
            continue

        song_id = row[0]

        cursor.execute("SELECT user_id FROM ratings WHERE user_id = %s AND song_id = %s", (user_id, song_id))
        if cursor.fetchone() != None:
            rejects.add((username, artist, song))
            continue

        cursor.execute(
            "INSERT INTO ratings (user_id, song_id, rating, rating_date) VALUES (%s, %s, %s, %s)",
            (user_id, song_id, rating, date)
        )

    mydb.commit()
    return rejects


def get_most_rated_songs(mydb, year_range, n):
    cursor = mydb.cursor()
    cursor.execute("""
        SELECT s.title, a.name, COUNT(*)
        FROM ratings r, songs s, artists a
        WHERE r.song_id = s.id
        AND s.artist_id = a.id
        AND YEAR(r.rating_date) BETWEEN %s AND %s
        GROUP BY s.id, s.title, a.name
        ORDER BY COUNT(*) DESC, s.title ASC
        LIMIT %s
    """, (year_range[0], year_range[1], n))
    return cursor.fetchall()


def get_most_engaged_users(mydb, year_range, n):
    cursor = mydb.cursor()
    cursor.execute("""
        SELECT u.username, COUNT(*)
        FROM users u, ratings r
        WHERE u.id = r.user_id
        AND YEAR(r.rating_date) BETWEEN %s AND %s
        GROUP BY u.id, u.username
        ORDER BY COUNT(*) DESC, u.username ASC
        LIMIT %s
    """, (year_range[0], year_range[1], n))
    return cursor.fetchall()


def main():
    pass


if __name__ == "__main__":
    main()
