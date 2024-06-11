import mysql.connector
import configparser
from mysql.connector import errorcode

import Query_strings

class MySQL_handler():
    """Creates connection to the MySQL server with mysql.connector.
       Database connection is configured in config.ini file - within mysql_connector section.
    """
    def __init__(self):
        # Connect to database - use existing database or create one if it doesn't exist

        config = configparser.ConfigParser()
        config.read("config.ini")

        uid = config.get("mysql_connector", "login")
        pwd = config.get("mysql_connector", "password")
        hostname = config.get("mysql_connector", "hostname")
        db_name = config.get("mysql_connector", "db_name")
        
        self.__cnx__ = mysql.connector.connect(user=uid, password=pwd, host=hostname)
        self.__cursor__ = self.__cnx__.cursor(buffered=True)
    
        try:
            self.__cursor__.execute("USE {}".format(db_name))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database {} does not exist".format(db_name))
                try:
                    self.__cursor__.execute(Query_strings.create_database.format(db_name))
                except mysql.connector.Error as err:
                    print("Failed creating database: {}".format(err))
                    exit(1)

                print("Database {} created succesfully.".format(db_name))
                self.__cnx__.database = db_name
 
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close_connection()

    def close_connection(self):
        print("Closing connection")
        self.__cursor__.close()
        self.__cnx__.close()
    
    def insert_movie_data(self, movies):
        print("Building tables")
        for table_name in Query_strings.TABLES:
            table_description = Query_strings.TABLES[table_name]

            try:
                print("Creating table: {}".format(table_name))
                self.__cursor__.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("Table already exists. Clearing table context.")
                    self.__cursor__.execute("DELETE FROM {};".format(table_name))
                else:
                    print(err.msg)
                    exit(1)

        print("Inserting data into the tables")
        for movie in movies:
            movie_data = (movie["title"], movie["rating"]) 
            movie_genres = movie["gerne"]
            movie_id = None

            self.__cursor__.execute(Query_strings.add_movie, movie_data)

            for genre in movie_genres:    
                try:
                    self.__cursor__.execute(Query_strings.add_genre, [genre, genre])
                except mysql.connector.Error as err:
                    if err.errno != errorcode.ER_DUP_ENTRY:
                        print(err.msg)
                        exit(1)

            self.__cursor__.execute(Query_strings.select_last_id)
            movie_id = self.__cursor__.fetchone()[0]

            for genre in movie_genres:
                values_to_insert = (movie_id, genre)
                self.__cursor__.execute(Query_strings.add_movie_genre, values_to_insert)

        self.__cnx__.commit()