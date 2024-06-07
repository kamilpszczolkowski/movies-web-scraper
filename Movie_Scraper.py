import csv
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from MySQL_handler import MySQL_handler
from GCP_SQL_handler import GCP_SQL_handler

def setup_webdriver():
    """Configuration and initialization of Selenium Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    chrome_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options = chrome_options)
    driver.implicitly_wait(3)

    return driver

def scrape_movie_data(driver):
    print("Loading the page")
    driver.get('https://www.filmweb.pl/ranking/film')

    # Handle cookies and advertisement
    for element_id in ["didomi-notice-agree-button", "ws__skip"]:
        try:
            button = driver.find_element(By.ID, element_id)
            if element_id == "ws__skip":
                time.sleep(4)  # Wait for the ad to be fully loaded and clickable
            button.click()
        except:
            print(f"Element with ID '{element_id}' not found, skipping")
    
    # Scroll the page to the last element to load them all
    for position in range(5, 50):
        Position_element = driver.find_element(By.ID, str(position))
        driver.execute_script("arguments[0].scrollIntoView(true);", Position_element)

    # Extract movie data
    print("Extracting scrapped data")
    movies = []
    for movie_tile in driver.find_elements(By.CLASS_NAME, "rankingType"):
        title = movie_tile.find_element(By.CLASS_NAME, 'rankingType__title').text
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
        with open('exports/movies.csv', 'w', encoding="utf-8", newline = '') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Title', 'Genre', 'Rating'])
            writer.writerows([movie.values() for movie in movies])
    elif choice == 2:
        print("Writing data with MySQL.connector")
        MySQL_handler().insert_movie_data(movies)
    elif choice == 3:
        print("Writing data with GCP MySQL connector")
        SQL_Connector = GCP_SQL_handler()
        SQL_Connector.insert_movie_data(movies)
        SQL_Connector.close_connection()

if __name__ == "__main__":
    driver = setup_webdriver()
    movies = scrape_movie_data(driver)

    while True:
        choice = input("Select the data source:\n 1) CSV file\n 2) MySQL.connector server\n 3) GCP MySQL server\n")

        try:
            choice = int(choice)
            if 1 <= choice <= 3:
                save_movie_data(movies, choice)
                break
        except ValueError:
            pass
        print("Invalid choice, please enter a number between 1 and 3")