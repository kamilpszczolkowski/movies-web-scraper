SELECT * FROM movies;
SELECT * FROM genres;
SELECT * FROM movie_genres;

DESCRIBE movies;
DESCRIBE movie_genres;
DESCRIBE genres;

-- Get all movies with their genres (in one column)
SELECT 
    movies.movie_id,
    movies.name, 
    movies.rating,
    GROUP_CONCAT(movie_genres.genre SEPARATOR ', ') as Genres
FROM
    movies
LEFT JOIN 
    movie_genres
ON
    movie_genres.movie_id = movies.movie_id
GROUP BY
    movies.movie_id;

-- Get number of movies per specific category and average rating
SELECT
    movie_genres.genre,
    ROUND(AVG(movies.rating), 2) AS average_rating,
    COUNT(movies.movie_id) AS movies_count
FROM
    movies
LEFT JOIN
    movie_genres
ON
    movie_genres.movie_id = movies.movie_id
GROUP BY 
    movie_genres.genre
ORDER BY
    average_rating DESC;

-- Get average rating of a movie in top 500
SELECT
    ROUND(AVG(movies.rating), 2) AS average_rating
FROM
    movies;

-- Get median score from top 500
SELECT
    AVG(rating) As Median_rating
FROM (
    SELECT
        rating,
        ROW_NUMBER() OVER (ORDER BY rating DESC) AS ranked_id
    FROM
        movies
    ) AS ranked_table
WHERE 
    ranked_id = 250 OR ranked_id = 251;
