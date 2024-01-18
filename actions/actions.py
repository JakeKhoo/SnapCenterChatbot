# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from datetime import datetime
from typing import Any, Text, Dict, List
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset
import pandas as pd
import mysql.connector

class ActionCheckBooking(Action):

    def name(self) -> Text:
        return "action_check_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hello World!" + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") )

        return []
    
class ValidateBookingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_booking_form"
    
    def validate_email(self, 
                       slot_value, 
                       dispatcher: CollectingDispatcher, 
                       tracker: Tracker, 
                       domain: DomainDict) -> Dict[Text, Any]:
        """Validate `email` value."""
        if "@" not in slot_value:
            dispatcher.utter_message(text="Please enter a valid email address.")
            return {"email": None}
        return {"email": slot_value}
    
    def validate_date_time(self, 
                       slot_value, 
                       dispatcher: CollectingDispatcher, 
                       tracker: Tracker, 
                       domain: DomainDict) -> Dict[Text, Any]:
        """Validate `date_time` value."""
        try:
            datetime.strptime(slot_value, "%d/%m/%y %H %p")

        except Exception:
            dispatcher.utter_message(text="Please enter a valid date.")
            
            return {"date_time": None}
        
        connection = create_mysql_connection()
        query = f"select * from bookings where Date_Time = '{slot_value}'"
        try:
            df = pd.read_sql(query, connection)
            email = df.iloc[0,1]
        except:
            dispatcher.utter_message(text="This time slot does not exist.")
            return {"date_time": None}

        if email != "0":
            dispatcher.utter_message(text="This time slot is taken.")
            return {"date_time": None}  
        else:
            query = f"update bookings set email = '{tracker.get_slot('email')}' where Date_Time = '{slot_value}'"
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            return {"date_time": slot_value}

class ValidateFeedbackForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_feedback_form"
    
    def validate_email(self, 
                       slot_value, 
                       dispatcher: CollectingDispatcher, 
                       tracker: Tracker, 
                       domain: DomainDict) -> Dict[Text, Any]:
        """Validate `email` value."""
        if "@" not in slot_value:
            dispatcher.utter_message(text="Please enter a valid email address.")
            return {"email": None}
        return {"email": slot_value}

    def validate_feedback(self, 
                    slot_value, 
                    dispatcher: CollectingDispatcher, 
                    tracker: Tracker, 
                    domain: DomainDict) -> Dict[Text, Any]:
        e = tracker.get_slot('email')
        query = f"Insert INTO feedback (email, feedback) values ('{e}', '{slot_value}')"
        connection = create_mysql_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        return {"feedback": slot_value}
   
def create_mysql_connection():
    host = "scdatabase.cd6meu8aau2d.us-east-1.rds.amazonaws.com"
    user = "admin"
    password = "password"
    database = "sc_db"
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
    
class ActionResetAllSlots(Action):
    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]