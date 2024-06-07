from google.cloud.sql.connector import Connector
import sqlalchemy
import configparser

import Query_strings

# In next step implement context manager!
class GCP_SQL_handler:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        project_id = config.get("gcp", "project_id")
        region = config.get("gcp", "region")
        instance_name = config.get("gcp", "instance_name")

        INSTANCE_CONNECTION_NAME = f"{project_id}:{region}:{instance_name}"

        DB_USER = config.get("gcp", "db_user")
        DB_PASS = config.get("gcp", "db_pass")
        DB_NAME = config.get("gcp", "db_name")

        self.__connector__ = Connector()

        getconn = lambda : self.__connector__.connect(
                INSTANCE_CONNECTION_NAME,
                "pymysql",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME
            )

        self.__pool__ = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )

    def close_connection(self):
        print("Closing connection")
        self.__connector__.close()

    def insert_movie_data(self, movies):
        with self.__pool__.connect() as db_conn:
        # create tables if not present, remove data if anything present
            print("Building tables")
            for table_name in Query_strings.TABLES:
                table_description = Query_strings.TABLES[table_name]
                print("Creating table: {}".format(table_name))

                db_conn.execute(sqlalchemy.text(table_description))
                db_conn.execute(sqlalchemy.text("DELETE FROM {};".format(table_name)))

            db_conn.commit() 

            print("Inserting data")
            for movie in movies:
                movie_genres = movie["gerne"]
                movie_id = None

                db_conn.execute(
                    sqlalchemy.text(Query_strings.add_movie_gcp), 
                    parameters={"name": movie["title"], "rating": movie["rating"]}
                )

                for genre in movie_genres:   
                    db_conn.execute(
                        sqlalchemy.text(Query_strings.add_genre_gcp),
                        parameters={"genre": genre}  
                    )


                movie_id = db_conn.execute(sqlalchemy.text(Query_strings.select_last_id)).fetchone()[0]

                for genre in movie_genres:

                    db_conn.execute(
                        sqlalchemy.text(Query_strings.add_movie_genre_gcp), 
                        parameters={"movie_id": movie_id, "genre": genre}
                    )

            db_conn.commit()

