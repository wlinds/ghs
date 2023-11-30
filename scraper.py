import os, requests, csv, time, datetime
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

# This scraper can be used instead of GitHub API
# Actually I haven't written the code for the API calls so this is the only way...

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
WAIT_TIME = 15 # Max time for selenium
CHECK_INTERVAL_SECONDS = 1800 # Interval between each scrape iteration (all repos)
CSV_FILE = "data.csv" # Replace if multiple projects

def get_latest_commit(url):
    """Fetch latest commit and timestamp for repo (url)."""

    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers)
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(url)
        driver.implicitly_wait(WAIT_TIME)
        content = driver.page_source

    if response.status_code == 200:
        soup = bs4(content, 'html.parser')
        target_element = soup.find('relative-time')
        datetime_value = target_element['datetime'] if target_element else None
        commit_message_element = soup.find('a', {'data-test-selector': 'commit-tease-commit-message'})
        commit_message = commit_message_element['title'] if commit_message_element and 'title' in commit_message_element.attrs else "Error fetching commit msg"
        
        # Idk why it doesn't find the message sometimes. Retrying once seem to work, but recursion could cause future issues.
        if commit_message == "Error fetching commit msg":
            print(f"Could not fetch commit message for {url[19:url.find('/', 19)]}. Retrying...")
            d, c = get_latest_commit(url)
            return d, c
        
        return datetime_value, commit_message

def save_to_csv(course, url, datetime_value, commit_message, username):
    with open(CSV_FILE, 'a', newline='') as csvfile:
        fieldnames = ['course', 'user', 'url', 'datetime', 'commit_message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the CSV file is empty and write the header if needed
        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'course': course, 'user': username, 'url': url, 'datetime': datetime_value, 'commit_message': commit_message})

def create_csv(filename=CSV_FILE):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['course', 'user', 'url', 'datetime', 'commit_message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    print("New CSV has been created.")

def main():
    course = "n"
    urls = []
    new_commits = 0

    with open('urls.csv', 'r', newline='') as csvfile:
        for row in csvfile:
            urls.append(row.strip())

    file_exists = os.path.exists(CSV_FILE)
    if not file_exists:
        create_csv()

    progress_bar = tqdm(urls, desc="Processing URLs")
    for url in progress_bar:
        username = url[19:url.find('/', 19)]
        datetime_value, commit_message = get_latest_commit(url)

        if datetime_value:
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['url'] == url and row['datetime'] == datetime_value:
                        break
                else:
                    tqdm.write(f"New commit found: {datetime_value}\n{url[18::]} | {commit_message}")
                    save_to_csv(course, url, datetime_value, commit_message, username)
                    new_commits += 1

        progress_bar.set_postfix(username=username)
        time.sleep(1)
    return new_commits

if __name__ == "__main__":
    while True:
        print(f"{datetime.datetime.now()} [+] Running script")
        n_commits = main()
        
        if n_commits == 0:
            print(f"No new updates.")
        else:
            print(f"{n_commits} new update(s).\n")

        next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=CHECK_INTERVAL_SECONDS)
        print(f"Next run: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(CHECK_INTERVAL_SECONDS)
