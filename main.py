import requests
import csv
import time
import datetime

from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver.common.by import By



def get_datetime_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)

    driver = webdriver.Chrome()
    driver.get(url)

    driver.implicitly_wait(15)
    content = driver.page_source
    response = requests.get(url)

    if response.status_code == 200:
        time.sleep(3)
        content = response.text
        soup = bs4(content, 'html.parser')

        target_element = soup.find('relative-time')
        datetime_value = target_element['datetime'] if target_element else None

        commit_message_element = soup.find('a', {'data-test-selector': 'commit-tease-commit-message'})
        commit_message = commit_message_element['title'] if commit_message_element and 'title' in commit_message_element.attrs else None

        driver.quit()
        return datetime_value, commit_message

    driver.quit()
    return None, None

def save_to_csv(course, url, datetime_value, commit_message, username):
    with open('data.csv', 'a', newline='') as csvfile:
        fieldnames = ['course', 'user', 'url', 'datetime', 'commit_message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the CSV file is empty and write the header if needed
        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'course': course, 'user': username, 'url': url, 'datetime': datetime_value, 'commit_message': commit_message})

def main():
    course = "n"
    urls = [

https://privnote.com/1vMfd9OC#L4XrYMKz6

    ]

    for url in urls:
        username = url[19:url.find('/', 19)]
        datetime_value, commit_message = get_datetime_from_url(url)

        if datetime_value:
            # Check if the datetime has changed for the given URL
            with open('data.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['url'] == url and row['datetime'] == datetime_value:
                        break
                else:
                    print(f"New commit found: {url[18::]} | {commit_message}")
                    save_to_csv(course, url, datetime_value, commit_message, username)
        time.sleep(1)

if __name__ == "__main__":
    while True:
        print(f"{datetime.datetime.now()} Running script")
        main()
        time.sleep(1800)
