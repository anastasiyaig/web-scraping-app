import time

import certifi
import requests
import selectorlib
import smtplib, ssl
import os
import sqlite3

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

connection = sqlite3.connect("data.db")


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
    data_row = extracted.split(",")
    data_row = [item.strip() for item in data_row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", data_row)
    connection.commit()


def read(data):
    data_row = extracted.split(",")
    data_row = [item.strip() for item in data_row]
    band, city, date = data_row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


if __name__ == "__main__":
    while True:

        scraped = scrape(url=URL)
        extracted = extract(source=scraped)
        print(extracted)

        if extracted != SCRAPING_PATTERN:
            row = read(data=extracted)
            if not row:
                store(data=extracted)
                body = f"Subject: {EMAIL_SUBJECT}" + "\n" + extracted
                composed_email = str(body).encode("utf-8")
                send_email(composed_email)
        time.sleep(2)
