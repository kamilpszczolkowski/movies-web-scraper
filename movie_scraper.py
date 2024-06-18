import csv
import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from mysql_handler import MySQLHandler
from gcp_sql_handler import GCPSQLHandler


def setup_webdriver():
    """Configuration and initialization of Selenium Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging']
    )
    
    chrome_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options = chrome_options)
    driver.implicitly_wait(3)

    return driver


def scrape_movie_data(driver):
    print("Loading the page")
    driver.get('https://www.filmweb.pl/ranking/film')

    # Handle cookies and advertisement
    cookies_bttn_id = "didomi-notice-agree-button"
    advert_bttn_class = "ws__skip"

    try:
        button = driver.find_element(By.ID, cookies_bttn_id)
        button.click()

        button = driver.find_element(By.CLASS_NAME, advert_bttn_class)
        time.sleep(4) #Wait for the ad to be fully loaded and clickable
        button.click()
    except NoSuchElementException as err:
        print(err.msg)

    # Scroll the page to the last element to load them all
    movies_qty = 500
    for position in range(5, movies_qty):
        Position_element = driver.find_element(By.ID, str(position))
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", 
            Position_element
        )

    # Extract movie data
    print("Extracting scrapped data")
    movies = []
    for movie_tile in driver.find_elements(By.CLASS_NAME, "rankingType"):
        title = movie_tile.find_element(
            By.CLASS_NAME, 
            'rankingType__title'
        ).text
        genres_elements = movie_tile.find_elements(
            By.XPATH, 
            './descendant::span[starts-with(@data-i18n,"entity@genre:")]'
        )

        genres = []
        for genre_element in genres_elements:
            genres.append(genre_element.text)

        rating = float(
            movie_tile.find_element(
                By.CLASS_NAME, 
                'rankingType__rate--value'
            ).text.replace(',','.')
        )
        
        movies.append({"title": title, "gerne":  genres, "rating": rating})

    return movies


def save_movie_data(movies, choice):
    if choice == 1:
        print("Saving data into CSV file")
        os.makedirs("exports", exist_ok=True)
        with open(
            'exports/movies.csv', 'w', 
            encoding="utf-8", newline = ''
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Title', 'Genre', 'Rating'])
            writer.writerows([movie.values() for movie in movies])
    elif choice == 2:
        print("Writing data with MySQL.connector")
        with MySQLHandler() as SQL_Connector:
            SQL_Connector.insert_movie_data(movies)
    elif choice == 3:
        print("Writing data with GCP MySQL connector")
        with GCPSQLHandler() as SQL_Connector:
            SQL_Connector.insert_movie_data(movies)


if __name__ == "__main__":
    driver = setup_webdriver()
    movies = scrape_movie_data(driver)
    driver.quit()

    while True:
        choice = input("Select the data source:\n 1) CSV file\n 2) "
                       "MySQL.connector server\n 3) GCP MySQL server\n")

        try:
            choice = int(choice)
            if 1 <= choice <= 3:
                save_movie_data(movies, choice)
                break
        except ValueError:
            print("Invalid character - number must be inserted")
        print("Invalid choice, please enter a number between 1 and 3")