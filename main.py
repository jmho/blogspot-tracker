import base64
import threading
import time
import requests as req
import schedule
import pickle
import os
import logging

from config import EMAIL, BLOG, TO

from threading import Event
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from bs4 import BeautifulSoup
from infi.systray import SysTrayIcon
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors
from googleapiclient.discovery import build
from pathlib import Path


class blogspot_tracker:
    def __init__(self):
        self.job = schedule.every().day.at("12:00").do(self.check_and_mail)
        self.base_dir = Path(__file__).parent
        self.is_stopped = Event()
        self.worker_thread = threading.Thread(target=self.scheduled_check, args=())
        self.cur_date = self.read_pickle()
        logging.basicConfig(
            filename=os.path.join(self.base_dir, "blogspot-tracker.log"),
            filemode="a",
            encoding="utf-8",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )

    def read_pickle(self):
        with open(os.path.join(self.base_dir, "date.pk"), "rb") as f:
            return pickle.load(f)

    def write_pickle(self, date):
        with open(os.path.join(self.base_dir, "date.pk"), "wb") as f:
            pickle.dump(date, f)

    def get_gmail_service(self):

        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
        ]

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(os.path.join(self.base_dir, "token.pickle")):
            with open(os.path.join(self.base_dir, "token.pickle"), "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(self.base_dir, "credentials.json"), SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(self.base_dir, "token.pickle"), "wb") as token:
                pickle.dump(creds, token)

        service = build("gmail", "v1", credentials=creds)
        return service

    def send_message(service, sender, message):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        try:
            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw = raw.decode()
            body = {"raw": raw}

            sent_message = (
                service.users().messages().send(userId=sender, body=body).execute()
            )
            logging.info("Message Id: %s", sent_message["id"])
            return sent_message
        except errors.HttpError as error:
            logging.error("An HTTP error occurred: %s", error)

    def create_message(sender, to, subject="New Blog Post", body="New Blog Post"):
        msg = MIMEMultipart()

        msg["to"] = to
        msg["from"] = sender
        msg["subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        return msg

    def mail(self):
        logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

        try:
            service = self.get_gmail_service()

            message = self.create_message(EMAIL, TO, "New Blog Post!", BLOG)

            self.send_message(service, EMAIL, message)

        except Exception as e:
            logging.error(e)
            raise

    def get_date(self):
        resp = req.get(BLOG)

        soup = BeautifulSoup(resp.text, "html.parser")

        curdate = soup.find("h2", "date-header").find("span", recursive=False)

        return curdate.text

    def check_and_mail(self):
        temp_date = self.get_date()
        if datetime.strptime(temp_date, "%A, %B %d, %Y") > datetime.strptime(
            self.cur_date, "%A, %B %d, %Y"
        ):
            self.mail()
            self.write_pickle(temp_date)
            self.cur_date = temp_date
            logging.info("New post")
        else:
            logging.info("No new post")

    def scheduled_check(self):
        while not self.is_stopped.is_set():
            schedule.run_pending()
            time.sleep(1)

    def start(self, sysTrayIcon):
        sysTrayIcon.update(hover_text="Blogspot Tracker - Running!")
        self.worker_thread = threading.Thread(target=self.scheduled_check, args=())
        self.job = schedule.every().day.at("12:00").do(self.check_and_mail)
        self.is_stopped.clear()
        self.worker_thread.start()

    def quit(self, sysTrayIcon):
        self.is_stopped.set()
        schedule.cancel_job(self.job)

    def stop_tracking(self, sysTrayIcon):
        sysTrayIcon.update(hover_text="Blogspot Tracker - Not Running!")
        self.is_stopped.set()
        schedule.cancel_job(self.job)

    def main(self):

        menu_options = (
            ("Start Tracking", None, self.start),
            ("Stop Tracking", None, self.stop_tracking),
        )

        systray = SysTrayIcon(
            os.path.join(self.base_dir, "resources\email.ico"),
            "Blogspot Tracker - Not Running!",
            menu_options,
            on_quit=self.quit,
        )

        systray.start()


if __name__ == "__main__":
    tracker = blogspot_tracker()
    tracker.main()
