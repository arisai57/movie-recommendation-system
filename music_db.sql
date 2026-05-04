CREATE TABLE artists(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(75) NOT NULL,
    CONSTRAINT unique_artist_name UNIQUE (name)
);

CREATE TABLE genres(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT unique_genre_name UNIQUE (name)
);

CREATE TABLE albums(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    artist_id INT NOT NULL, 
    album_release DATE NOT NULL,
    genre_id INT NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    CONSTRAINT unique_album_artist UNIQUE (title, artist_id)
);

CREATE TABLE songs(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    artist_id INT NOT NULL,
    album_id INT NULL,-- songs can be a single
    song_release DATE NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (album_id) REFERENCES albums(id),
    CONSTRAINT unique_song_artist UNIQUE (title, artist_id)
);

CREATE TABLE users(
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    CONSTRAINT unique_username UNIQUE (username)
);

CREATE TABLE ratings(
    user_id INT NOT NULL,
    song_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    rating_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (song_id) REFERENCES songs(id)
);


CREATE TABLE song_genre(
    song_id INT NOT NULL,
    genre_id INT NOT NULL,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    CONSTRAINT unique_song_genre UNIQUE (song_id, genre_id)
);
