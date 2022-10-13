import os
from typing import List
from requests import post

from libraries.string import gettext


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_API_URL = os.environ.get("MAILGUN_API_URL") # will be None if not present in environment varibles
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    FROM_EMAIL = os.environ.get("FROM_EMAIL")
    FROM_TITLE = "REST API Testing"

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str):
        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(gettext("mailgun_api_key_missing"))

        if cls.MAILGUN_API_URL is None:
            raise MailgunException(gettext("mailgun_api_url_missing"))

        if cls.FROM_EMAIL is None:
            raise MailgunException(gettext("from_email_missing"))

        response = post(f"http://api.mailgun.net/v3/{cls.MAILGUN_API_URL}/messages",
        auth=("api", cls.MAILGUN_API_KEY),
        data={
            "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
            "to": email,
            "subject": subject,
            "text": text,
            "html": html
        })

        if response.status_code != 200:
            raise MailgunException(gettext("confirm_email_not_sent"))

        return response
