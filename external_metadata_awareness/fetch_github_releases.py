import os
import click
import requests
from pathlib import Path
from typing import Optional, Dict

def get_github_api_url(owner: str, repo: str) -> str:
    """Generate the GitHub API URL for a repository's releases."""
    return f"https://api.github.com/repos/{owner}/{repo}/releases"

def create_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Create headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github+json",
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    return headers

def fetch_releases(api_url: str, headers: Dict[str, str], verbose: bool = False) -> list:
    """Fetch all releases from a GitHub repository using pagination."""
    releases = []
    url = api_url
    page = 1
    
    if verbose:
        click.echo(f"Fetching releases from {api_url}")
    
    while url:
        if verbose:
            click.echo(f"Fetching page {page}...")
        
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        releases.extend(data)
        
        url = res.links.get("next", {}).get("url")
        page += 1
    
    if verbose:
        click.echo(f"Found {len(releases)} releases in total")
    
    return releases

def save_notes(releases: list, min_tag: str, output_path: str, verbose: bool = False) -> None:
    """Save release notes to a file, filtering by minimum tag version."""
    # Filter releases from the specified min_tag onward
    sorted_releases = sorted(releases, key=lambda r: r["created_at"])
    start = False if min_tag else True  # If no min_tag, include all releases
    included_count = 0
    
    # Create parent directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_path, "w") as f:
        for r in sorted_releases:
            tag = r["tag_name"]
            if min_tag and tag == min_tag:
                start = True
            if not start:
                continue
            
            included_count += 1
            f.write(f"# {tag} — {r['published_at']}\n\n")
            f.write(r["body"] or "(No release notes provided)")
            f.write("\n\n---\n\n")
    
    if verbose:
        msg = f"Saved notes for {included_count} releases"
        if min_tag:
            msg += f" (from {min_tag} onwards)"
        click.echo(msg)
        click.echo(f"Output written to: {os.path.abspath(output_path)}")

@click.command()
@click.option("--owner", default="microbiomedata", show_default=True,
              help="GitHub repository owner/organization name")
@click.option("--repo", default="nmdc-schema", show_default=True,
              help="GitHub repository name")
@click.option("--min-tag", default="v7.1.0", show_default=True,
              help="Minimum tag version to include (inclusive). Empty string includes all releases.")
@click.option("--output", default="local/github-release-notes.md", show_default=True,
              help="Output markdown file path")
@click.option("--token", envvar="GITHUB_TOKEN",
              help="GitHub API token (can also be set via GITHUB_TOKEN environment variable)")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def main(owner: str, repo: str, min_tag: str, output: str, token: Optional[str], verbose: bool) -> None:
    """
    Fetch GitHub release notes and compile them to a markdown file.
    
    This tool fetches release notes from a GitHub repository and compiles them
    into a single markdown document, optionally starting from a specified minimum tag version.
    
    By default, it fetches notes from the NMDC schema repository, but can be used with any GitHub repo.
    """
    api_url = get_github_api_url(owner, repo)
    headers = create_headers(token)
    
    try:
        # Create a custom output filename if using non-default repo
        if output == "local/github-release-notes.md" and (owner != "microbiomedata" or repo != "nmdc-schema"):
            output = f"local/{repo}-release-notes.md"
            if verbose:
                click.echo(f"Using auto-generated output filename: {output}")
        
        releases = fetch_releases(api_url, headers, verbose)
        save_notes(releases, min_tag, output, verbose)
        if not verbose:
            click.echo(f"✅ Successfully fetched GitHub release notes to {os.path.abspath(output)}")
    except requests.RequestException as e:
        click.echo(f"Error: Failed to fetch releases: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()
