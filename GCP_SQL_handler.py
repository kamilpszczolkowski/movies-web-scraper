
import configparser

from google.cloud.sql.connector import Connector
import sqlalchemy

from query_strings import add_movie_gcp, add_genre_gcp, add_movie_genre_gcp
from query_strings import TABLES


class GCPSQLHandler():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        gcp_config = config["gcp"]
        instance_connection_name = (
            f"{gcp_config["project_id"]}:"
            f"{gcp_config["region"]}:"
            f"{gcp_config["instance_name"]}"
        )

        self._connector = Connector()

        def getconn():
            return self._connector.connect(
                instance_connection_name,
                "pymysql",
                user=gcp_config["db_user"],
                password=gcp_config["db_pass"],
                db=gcp_config["db_name"]
            )

        self._pool = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close_connection()

    def close_connection(self):
        print("Closing connection")
        self._connector.close()

    def insert_movie_data(self, movies):
        with self._pool.connect() as db_conn:
            self._create_tables(db_conn)

            print("Inserting data into the tables")
            for movie in movies:
                movie_genres = movie["gerne"]

                result = db_conn.execute(
                    sqlalchemy.text(add_movie_gcp), 
                    parameters={
                        "name": movie["title"], 
                        "rating": movie["rating"]
                    }
                )
                movie_id = result.lastrowid

                for genre in movie_genres:   
                    db_conn.execute(
                        sqlalchemy.text(add_genre_gcp),
                        parameters={"genre": genre}  
                    )
                    db_conn.execute(
                        sqlalchemy.text(add_movie_genre_gcp), 
                        parameters={"movie_id": movie_id, "genre": genre}
                    )    

            db_conn.commit()
    
    def _create_tables(self, db_conn):
        print("Creating tables")
        for table_name, table_description in TABLES.items():
            try:
                print(f"Creating table: {table_name}")
                db_conn.execute(sqlalchemy.text(table_description))
            except sqlalchemy.exc.OperationalError:
                print(f"table {table_name} already exists, deleting data")
                db_conn.execute(sqlalchemy.text(f"DELETE FROM {table_name};")
)
