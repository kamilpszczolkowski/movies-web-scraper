# movies-web-scraper

This project is a hands-on exploration of building a simple data pipeline. The focus is on scraping movie data from the web and then storing it in either a MySQL database or a CSV file for further analysis.

## Project Goals

*   Learn the fundamentals of web scraping using Python and Selenium.
*   Understand how to extract structured data from websites.
*   Practice interacting with databases (MySQL) and CSV files.
*   Gain experience in designing a basic data pipeline flow.

## How It Works

1.  **Web Scraping with Selenium:** The Python script utilizes Selenium to automate a web browser (Chrome/Firefox) for data extraction. This enables interaction with dynamic website elements, making it suitable for sites that rely on JavaScript.

2.  **Data Transformation:** The scraped data is cleaned, parsed, and formatted for storage.

3.  **Storage Options:**
    *   **MySQL Database:** If you choose this option, the data is inserted into a MySQL database. You'll need to set up a MySQL server and configure the database connection details in the `config.ini` file. There are two MySQL connectors available:
        *   **myslq.connector** - allows to configure a connection trhough a hostname, login, password and db_name (used for locally hosted mysql server)
        *   **google.cloud.sql.connector** - allows to configure connection to the instance of MySQL server hosted on GCP
    *   **CSV File:** Alternatively, you can save the data in a CSV file for easy viewing and analysis in spreadsheets or other tools.

## Getting Started

1.  **Prerequisites:**
    *   Anaconda (environment config included in `environment.yml` file)
    *   MySQL server installed and running

2.  **Configuration:**
    *   **Anaconda Environment:** As mentioned before, envronment can be recreated with `environment.yml` file: `conda env create -f environment.yml`
    *   **Database Connection:** Update the `config.ini` file with your MySQL database credentials:
        * for mysql.connector provide login, password, hostname and db_name
        * for gcp provide project_id, region, instance_name, db_user, db_pass, db_name

3.  **Running the Scraper:**
    *   Activate your Anaconda environment (if using): `conda activate <your_env_name>`
    *   Execute `python movie_scraper.py`

## Database Schema (MySQL)

The MySQL database consists of three tables:

*   **`movies`:**
    *   `id`: (INT, primary key) Unique identifier for each movie.
    *   `name`: (VARCHAR) Title of the movie.
    *   `rating`: (DECIMAL) Movie rating.

*   **`genres`:**
    *   `genre`: (VARCHAR, primary key) Unique name of the genre.

* **`movie_genres`:**
    * `movie_id`: (INT, foreign key) References the `id` in the `movies` table.
    * `genre`: (VARCHAR, foreign key) References the `genre` in the `genres` table.

The `movie_genres` table serves as a junction table to create a many-to-many relationship between movies and genres, allowing a movie to have multiple genres and a genre to be associated with multiple movies.

## Future Enhancements

*   Create a web interface to visualize the scraped data
*   Scrape additional data and expand the database schema