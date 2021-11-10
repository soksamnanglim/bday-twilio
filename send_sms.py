from datetime import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import pandas as pd
from twilio.rest import Client

app = Flask(__name__)


account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
sender = os.environ.get('TWILIO_NUMBER')
receiver = os.environ.get('TO_NUMBER')
client = Client(account_sid, auth_token)


def wish_happy_birthday(client, recipient_number, recipient_name):
    """"
    Wish your special person a happy birthday using their number.

    Args:
        client (object): Twilio API Client object
        recipient_number (str): the special person's number
        recipient_name (str): the special person's name

    Returns:
        True if wish successful, otherwise False

    """
    bday_msg = """
        Happy birthday {}! I hope you enjoy your special day today! Much Love, Lucky.
    """.format(recipient_name)

    try:
        message = client.messages.create(
            body=bday_msg,
            from_=sender,
            to=receiver,
        )
        print("Birthday wish sent to", recipient_name,
              "through phone number", recipient_number)
        return True
    except Exception as error:
        print("An error occurred. Your special person did not receive a birthday wish from you.")
        print(repr(error))
        return False


def create_birthdays_dataframe():
    """
    Creates a pandas dataframe containing bday information from a csv file.

    Args:
        None

    Returns:
        A dataframe if successful, otherwise False
    """

    try:
        def dateparse(x): return datetime.strptime(x, "%m-%d-%Y")
        birthdays_df = pd.read_csv(
            "bdays.csv",
            dtype=str,
            parse_dates=['Birth Date'],
            date_parser=dateparse
        )
        print(birthdays_df)
        return birthdays_df

    except Exception as error:
        print("An error occured. Did not succesfully create a data frame for bdays.")
        print(repr(error))
        return False


def check_for_bday():
    """
        Wishes your special person a happy birthday if the day is their birthday.

        Args:
            None
        Returns:
            True if successful, else False
    """

    try:
        bdays_df = create_birthdays_dataframe()
        bdays_df["day"] = bdays_df["Birth Date"].dt.day
        bdays_df["month"] = bdays_df["Birth Date"].dt.month
        today = datetime.now()

        for i in range(bdays_df.shape[0]):
            bday_day = bdays_df.loc[i, "day"]
            bday_month = bdays_df.loc[i, "month"]
            if today.day == bday_day and today.month == bday_month:
                wish_happy_birthday(
                    client, bdays_df.loc[i, "Phone Number"], bdays_df.loc[i, "Name"])

        return True

    except Exception as error:
        print("An error occurred. Could not check for birthday.")
        print(repr(error))
        return False

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(check_for_bday, 'cron',
                            day_of_week='mon-sun', hour=0, minute=1)
    scheduler.start()


if __name__ == '__main__':
    app.run()
