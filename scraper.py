from git import Repo
import requests, os
from utils import create_folder

GITHUB_API_URL = "https://api.github.com/search/repositories"
QUERY = "language:typescript"
MAX_REPOS = 10
CLONE_DIR = "./typescript_repos"




def clone_repository(repo_url, clone_dir):
    try:
        Repo.clone_from(repo_url, clone_dir)
    except Exception as e:
        print(f"Error cloning {repo_url}: {e}")


def search_and_clone_repositories(query, max_repos):
    repos = []
    page = 1
    while len(repos) < max_repos:
        response = requests.get(f"{GITHUB_API_URL}?q={query}&per_page=10&page={page}")
        data = response.json()
        repos.extend(data['items'])
        for repo in data['items']:
            repoName = repo['name']
            repoUrl = repo['clone_url']
            repoCloneDir = os.path.join(CLONE_DIR, repoName)
            # check si le repo est déjà cloné
            if os.path.exists(repoCloneDir):
                print(f"{repoName} déjà cloné")
                continue
            else:
                print(f"Clonage de {repoName}")
                clone_repository(repoUrl, repoCloneDir)
        page += 1
    return repos[:max_repos]




if __name__ == "__main__":

    create_folder(CLONE_DIR)

    allRepositories = search_and_clone_repositories(QUERY, MAX_REPOS)
    for repo in allRepositories:
        print(f"Cloned {repo['name']}")