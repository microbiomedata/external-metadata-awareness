import csv
import os
import click
import pprint
from tqdm import tqdm

from typing import List, Any, Dict
from dotenv import load_dotenv
from github import Github, Repository, RateLimitExceededException, UnknownObjectException, GithubException

dotenv_path = os.path.join('local', '.env')
load_dotenv(dotenv_path, verbose=True)


@click.command()
@click.option('--org-name', default="microbiomedata", help='The name of the GitHub organization.')
@click.option('--repo-type', default='public', help='Type of repositories to fetch (e.g., "public", "private").')
@click.option('--output-file', default='local/inferred-first-commiter.tsv', help='File to write the commit data to.')
def main(org_name: str, repo_type: str, output_file: str):
    """
    Fetch and display information about the earliest commit from each repository of a specified GitHub organization,
    and write this data to a TSV file.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Please set the GITHUB_TOKEN environment variable.")
        exit(1)

    repos = get_all_org_repos(org_name, github_token, repo_type)
    commit_data = []

    for repo in tqdm(repos, desc="Processing Repositories"):
        repo_name = f"{org_name}/{repo.name}"
        commits = get_all_repo_commits(repo_name, github_token)
        if commits:
            first_commit = sorted(commits, key=lambda c: c.commit.author.date)[0]  # Sort and get the earliest commit
            if first_commit.commit.author:
                commit_info = {
                    "Repository": repo.name,
                    "SHA": first_commit.sha,
                    "Date": first_commit.commit.author.date,
                    "Author Email": first_commit.commit.author.email
                }
                commit_data.append(commit_info)

    write_commits_to_tsv(commit_data, output_file)


def get_all_org_repos(org_name: str, token: str, repo_type: str) -> List[Any]:  # -> List[Repository]:
    """ Fetches all repositories for a given organization from GitHub.

    Args:
        org_name (str): GitHub organization name.
        token (str): GitHub API token.
        repo_type (str): Type of repositories to fetch.

    Returns:
        List[Repository]: List of Repository objects.
    """
    g = Github(token)
    try:
        org = g.get_organization(org_name)
    except UnknownObjectException:
        print(f"Organization '{org_name}' not found. Please check the organization name.")
        return []
    except RateLimitExceededException:
        print("GitHub API rate limit exceeded. Please try again later.")
        return []

    repos = []
    page = 1
    while True:
        try:
            new_repos = org.get_repos(type=repo_type).get_page(page - 1)
            if not new_repos:
                break
            repos.extend(new_repos)
            page += 1
        except GithubException as e:
            handle_github_exceptions(e, org_name, "repositories")
            break
        except RateLimitExceededException:
            print("GitHub API rate limit exceeded while fetching repositories. Returning partial results.")
            break

    return repos


def get_all_repo_commits(repo_name: str, token: str) -> List:
    """ Fetches all commits from a specific repository.

    Args:
        repo_name (str): Full name of the repository (organization/repository).
        token (str): GitHub API token.

    Returns:
        List: List of commit objects.
    """
    g = Github(token)
    try:
        repo = g.get_repo(repo_name)
    except UnknownObjectException:
        print(f"Repository '{repo_name}' not found. Please check the repository name.")
        return []
    except RateLimitExceededException:
        print("GitHub API rate limit exceeded. Please try again later.")
        return []

    commits = []
    page = 1
    while True:
        try:
            new_commits = repo.get_commits().get_page(page - 1)
            if not new_commits:
                break
            commits.extend(new_commits)
            page += 1
        except GithubException as e:
            handle_github_exceptions(e, repo_name, "commits")
            break
        except RateLimitExceededException:
            print("GitHub API rate limit exceeded while fetching commits. Returning partial results.")
            break

    commits.sort(key=lambda x: x.commit.author.date, reverse=True)
    return commits


def handle_github_exceptions(e: GithubException, name: str, resource_type: str):
    """ Handle common GitHub API exceptions.

    Args:
        e (GithubException): Exception object.
        name (str): Name of the organization or repository.
        resource_type (str): Type of resource (e.g., "repositories", "commits").
    """
    if e.status == 409:
        print(f"Error accessing {resource_type} for '{name}'. Some resources might be empty.")
    elif e.status == 404:
        print(f"Unable to access {resource_type} for '{name}'. You might not have the necessary permissions.")
    else:
        print(f"An error occurred while fetching {resource_type}: {str(e)}")


def write_commits_to_tsv(commit_data: List[Dict], file_name: str):
    """
    Write commit data to a TSV file.
    """
    with open(file_name, mode='w', newline='') as file:
        fieldnames = ['Repository', 'SHA', 'Date', 'Author Email']
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for data in commit_data:
            writer.writerow(data)


if __name__ == "__main__":
    main()
