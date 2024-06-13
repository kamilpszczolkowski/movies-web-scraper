TABLES = {}

TABLES['genres'] = (
    "CREATE TABLE `genres` ("
    "genre_id int(11) NOT NULL AUTO_INCREMENT,"
    "name varchar(30) NOT NULL,"
    "PRIMARY KEY (`genre_id`)"
    ")"
)

TABLES['movies'] = (
    "CREATE TABLE `movies` ("
    "movie_id int(11) NOT NULL AUTO_INCREMENT,"
    "name varchar(100) NOT NULL,"
    "rating float(3, 2),"
    "PRIMARY KEY (`movie_id`)"
    ")"
)

TABLES['movie_genres'] = (
    "CREATE TABLE `movie_genres` ("
    "movie_id int(11) NOT NULL,"
    "genre_id int(11) NOT NULL,"
    "PRIMARY KEY (`movie_id`, `genre_id`),"
    "FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`) ON DELETE CASCADE,"
    "FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`) ON DELETE CASCADE"
    ")"
)

create_database = ("CREATE DATABASE (%s) DEFAULT CHARACTER SET 'UTF8'")

add_movie = ("INSERT INTO movies "
             "(name, rating) "
             "VALUES (%s, %s)")

add_genre =  ("INSERT INTO genres (name) "
              "SELECT %s WHERE NOT EXISTS ( "
              "SELECT 1 FROM genres WHERE name = %s);")

add_movie_genre = ("INSERT INTO movie_genres "
                   "(movie_id, genre_id) "
                   "VALUES (%s, %s);")

select_movie_genre_id = ("SELECT genre_id " 
                         "FROM genres "
                         "WHERE name = (%s);")

select_movies = ('SELECT * FROM movies ORDER BY rating DESC;')

select_movies_per_category = (
    "SELECT "
    "    movie_genres.genre, "
    "    ROUND(AVG(movies.rating), 2) AS average_rating, "
    "    COUNT(movies.movie_id) AS movies_count "
    "FROM movies "
    "LEFT JOIN movie_genres "
    "ON movie_genres.movie_id = movies.movie_id "
    "GROUP BY movie_genres.genre "
    "ORDER BY average_rating DESC; "
)

add_movie_gcp = ("INSERT INTO movies "
             "(name, rating) "
             "VALUES (:name, :rating)")

add_genre_gcp =  ("INSERT INTO genres (genre) "
                  "SELECT :genre WHERE NOT EXISTS ( "
                  "SELECT 1 FROM genres WHERE genre = :genre);")

add_movie_genre_gcp = ("INSERT INTO movie_genres "
                   "(movie_id, genre) "
                   "VALUES (:movie_id, :genre)")