import requests, csv

TOKEN = ''
REPOS = 'urls.csv' # Each row should contain a GitHub repo URL
CSV_OUTPUT = 'commit_data.csv' 
CATEGORY = 'n'

def fetch_commits(repo_url, TOKEN, commit_limit=None):

    str_strip = repo_url.rstrip('/').split('/')
    user, repo_name = str_strip[-2], str_strip[-1]
    url = f'https://api.github.com/repos/{user}/{repo_name}/commits'

    if commit_limit is not None:
        url += f'?per_page={commit_limit}'
    headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        commits = response.json()
        commit_data = []

        for commit in commits:
            commit_message = commit['commit']['message']
            commit_timestamp = commit['commit']['committer']['date']
            commit_url = commit['html_url']

            if 'author' in commit and commit['author'] is not None:
                user = commit['author']['login'] if 'login' in commit['author'] else None
                avatar_url = commit['author']['avatar_url'] if 'avatar_url' in commit['author'] else None
            else:
                avatar_url = None

            commit_data.append({
                'course': CATEGORY,
                'user': user,
                'repo_url': repo_url,
                'commit_url': commit_url,
                'datetime': commit_timestamp,
                'commit_message': commit_message,
                'gravatar_url': avatar_url
            })

        write_commit_data_to_csv(commit_data, CSV_OUTPUT)
        return commit_data
    else:
        print(f"Failed to fetch {user}/{repo_name}: {response.status_code}")
        return None

def write_commit_data_to_csv(commit_data, CSV_OUTPUT):
    existing_commits = set()
    try:
        with open(CSV_OUTPUT, 'r', newline='', encoding='utf-8') as existing_file:
            reader = csv.DictReader(existing_file)
            for row in reader:
                existing_commits.add((
                    row['course'],
                    row['user'],
                    row['repo_url'],
                    row['commit_url'],
                    row['datetime'],
                    row['commit_message'],
                    row['gravatar_url']))

    except FileNotFoundError:
        pass

    # Filter out already existing commits
    new_commit_data = [commit for commit in commit_data
                       if (commit['course'],
                           commit['user'],
                           commit['repo_url'],
                           commit['commit_url'],
                           commit['datetime'],
                           commit['commit_message'],
                           commit['gravatar_url']) not in existing_commits]

    with open(CSV_OUTPUT, 'a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['course', 'user', 'repo_url', 'commit_url', 'datetime', 'commit_message', 'gravatar_url']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerows(new_commit_data)

    if new_commit_data != []:
        for i in range(len(new_commit_data)):
            print(f"\n{new_commit_data[i]['user']} made a new commit {new_commit_data[i]['datetime']}:")
            print(new_commit_data[i]['commit_message'])
            print(new_commit_data[i]['commit_url'])
            print(len(new_commit_data[i]['commit_url'])*"=")

def fetch_all_repos(REPOS, commit_limit=None):
    with open(REPOS, 'r') as repos_file:
        reader = csv.reader(repos_file)
        for row in reader:
            repo_url = row[0]
            commits = fetch_commits(repo_url, TOKEN, commit_limit)

if __name__ == "__main__":
    fetch_all_repos(REPOS, commit_limit=None)