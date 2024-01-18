import pandas as pd
from datetime import datetime
import numpy as np
import math
import mysql.connector
from sqlalchemy import create_engine

# Replace these with your RDS connection details
host = "scdatabase.cd6meu8aau2d.us-east-1.rds.amazonaws.com"
user = "admin"
password = "password"
database = "sc_db"


def create_mysql_connection(host, user, password, database):
    try:
        # Create a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        # Check if the connection was successful
        if connection.is_connected():
            print(f"Connected to MySQL database: {database}")
            return connection
        else:
            print("Connection failed")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

connection = create_mysql_connection(host, user, password, database)
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:3306/{database}")

def generate_dataframe(start, end, engine):
    # Generate dates
    dates = pd.date_range(start, end)

    # Generate hourly blocks
    hours_weekday = pd.date_range(start='11:00', end='21:00', freq='H').time
    hours_weekend = pd.date_range(start='10:00', end='22:00', freq='H').time

    # Create DataFrame
    data = []
    for date in dates:
        if date.weekday() < 5:  # Weekday
            for hour in hours_weekday:
                data.append([date.date().strftime("%d/%m/%y") + " " + hour.strftime("%I %p"), 0])
    df = pd.DataFrame(data, columns=['Date_Time', 'email'])
    df.to_sql(name = 'bookings', con=engine, if_exists='append', index=False)

def create_feedback(connection):
    query = "CREATE TABLE IF NOT EXISTS feedback (email varchar(255), feedback varchar(1023));"
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    return 
e = "@"
feedback = "good"
# query = f"Insert INTO feedback (email, feedback) values ('{e}', '{feedback}')"
# cursor = connection.cursor()
# cursor.execute(query)
# connection.commit()
dataframe = pd.read_sql_query("select * from feedback", connection)
print(dataframe)