import configparser

from mysql.connector import connect, Error, errorcode

from query_strings import add_movie, add_genre, add_movie_genre
from query_strings import create_database, TABLES

class MySQLHandler():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        mysql_config = config["mysql_connector"]
        
        self._cnx = connect(
            user=mysql_config["login"], 
            password=mysql_config["password"], 
            host=mysql_config["hostname"]
        )
        self._cursor = self._cnx.cursor(buffered=True)
        self._ensure_database_exists(mysql_config["db_name"])

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close_connection()

    def close_connection(self):
        print("Closing connection")
        self._cursor.close()
        self._cnx.close()

    def _ensure_database_exists(self, db_name):
        try:
            self._cursor.execute(f"USE {db_name}")
        except Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Database {db_name} does not exist")
                self._cursor.execute(create_database, db_name)
                self._cnx.database = db_name
            else:
                raise
 
    def insert_movie_data(self, movies):
        self._create_tables()

        print("Inserting data into the tables")
        for movie in movies:
            movie_data = (movie["title"], movie["rating"]) 
            movie_genres = movie["gerne"]

            self._cursor.execute(add_movie, movie_data)
            movie_id = self._cursor.lastrowid

            for genre in movie_genres:    
                try:
                    self._cursor.execute(
                        add_genre, 
                        (genre, genre)
                    )
                    self._cursor.execute(
                        add_movie_genre, 
                        (movie_id, genre)
                    )
                except Error as err:
                    if err.errno != errorcode.ER_DUP_ENTRY:
                        raise
        
        self._cnx.commit()

    def _create_tables(self):
        print("Creating tables")
        for table_name, table_description in TABLES.items():
            try:
                print(f"Creating table: {table_name}")
                self._cursor.execute(table_description)
            except Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print(f"Table {table_name} already exists." 
                          "Clearing table context.")
                    self._cursor.execute(f"DELETE FROM {table_name};")
                else:
                    raise