import time

import certifi
import requests
import selectorlib
import smtplib, ssl
import os

URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = \
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
EMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAIL_SUBJECT = "New event found!"

SCRAPING_PATTERN = "No upcoming tours"


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url=url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465
    context = ssl.create_default_context(cafile=certifi.where())

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(
            user=SENDER_EMAIL,
            password=EMAIL_PASSWORD
        )
        server.sendmail(
            from_addr=SENDER_EMAIL,
            to_addrs=RECEIVER_EMAIL,
            msg=message)


def store(data):
    with open("data.txt", "a") as file:
        file.write(data + "\n")


def read(data):
    with open("data.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    while True:

        scraped = scrape(url=URL)
        extracted = extract(source=scraped)
        print(extracted)
        content = read(data=extracted)

        if extracted != SCRAPING_PATTERN:
            if extracted not in content:
                store(data=extracted)
                body = f"Subject: {EMAIL_SUBJECT}" + "\n" + extracted
                composed_email = str(body).encode("utf-8")
                send_email(composed_email)
        time.sleep(2)
