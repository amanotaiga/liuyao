#!/usr/bin/env python3
"""
Script to create a GitHub repository and initialize git for the liuyao project.

This script will:
1. Initialize a git repository (if not already initialized)
2. Create a .gitignore file (if it doesn't exist)
3. Create a GitHub repository using the GitHub API
4. Add all files and make the initial commit
5. Push to GitHub

Requirements:
- Python 3.11+
- requests library: pip install requests
- GitHub Personal Access Token with 'repo' scope

Usage:
    python setup_github_repo.py --token YOUR_GITHUB_TOKEN [--name REPO_NAME] [--private]
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required.")
    print("Please install it using: pip install requests")
    sys.exit(1)


def run_command(cmd: list, check: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            shell=True if os.name == 'nt' else False
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def check_git_installed() -> bool:
    """Check if git is installed."""
    exit_code, _, _ = run_command(["git", "--version"], check=False)
    return exit_code == 0


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    return Path(".git").exists()


def init_git_repo() -> bool:
    """Initialize git repository if not already initialized."""
    if is_git_repo():
        print("✓ Git repository already initialized")
        return True
    
    if not check_git_installed():
        print("Error: Git is not installed or not in PATH.")
        print("Please install Git from https://git-scm.com/downloads")
        return False
    
    print("Initializing git repository...")
    exit_code, stdout, stderr = run_command(["git", "init"], check=False)
    if exit_code != 0:
        print(f"Error initializing git repository: {stderr}")
        return False
    
    print("✓ Git repository initialized")
    return True


def create_github_repo(token: str, repo_name: str, private: bool = False, description: str = "") -> Optional[dict]:
    """Create a GitHub repository using the GitHub API."""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False
    }
    
    print(f"Creating GitHub repository '{repo_name}'...")
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        repo_info = response.json()
        print(f"✓ Repository created successfully!")
        print(f"  URL: {repo_info['html_url']}")
        return repo_info
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_data = e.response.json() if e.response.content else {}
            error_msg = error_data.get('message', str(e))
            if 'name already exists' in error_msg.lower():
                print(f"⚠ Repository '{repo_name}' already exists on GitHub")
                # Try to get existing repo info - first get username
                try:
                    user_response = requests.get("https://api.github.com/user", headers=headers)
                    if user_response.status_code == 200:
                        username = user_response.json().get('login')
                        if username:
                            get_url = f"https://api.github.com/repos/{username}/{repo_name}"
                            get_response = requests.get(get_url, headers=headers)
                            if get_response.status_code == 200:
                                return get_response.json()
                except:
                    pass
            print(f"Error creating repository: {error_msg}")
        else:
            print(f"Error creating repository: {str(e)}")
        return None


def setup_git_remote(repo_url: str) -> bool:
    """Set up git remote origin."""
    print("Setting up git remote...")
    exit_code, _, stderr = run_command(["git", "remote", "remove", "origin"], check=False)
    
    exit_code, stdout, stderr = run_command(["git", "remote", "add", "origin", repo_url], check=False)
    if exit_code != 0:
        print(f"Error setting up remote: {stderr}")
        return False
    
    print("✓ Git remote configured")
    return True


def add_and_commit_files() -> bool:
    """Add all files and make initial commit."""
    print("Adding files to git...")
    exit_code, _, stderr = run_command(["git", "add", "."], check=False)
    if exit_code != 0:
        print(f"Error adding files: {stderr}")
        return False
    
    # Check if there are changes to commit
    exit_code, stdout, _ = run_command(["git", "status", "--porcelain"], check=False)
    if not stdout.strip():
        print("⚠ No changes to commit (repository may already be up to date)")
        return True
    
    print("Making initial commit...")
    exit_code, _, stderr = run_command(
        ["git", "commit", "-m", "Initial commit: Liu Yao Divination System"],
        check=False
    )
    if exit_code != 0:
        print(f"Error making commit: {stderr}")
        return False
    
    print("✓ Files committed")
    return True


def push_to_github(branch: str = "main") -> bool:
    """Push to GitHub."""
    print(f"Pushing to GitHub (branch: {branch})...")
    
    # Check if branch exists, if not create it
    exit_code, stdout, _ = run_command(["git", "branch", "--show-current"], check=False)
    current_branch = stdout.strip() if stdout.strip() else "main"
    
    # Set upstream and push
    exit_code, _, stderr = run_command(
        ["git", "push", "-u", "origin", current_branch],
        check=False
    )
    if exit_code != 0:
        print(f"Error pushing to GitHub: {stderr}")
        print("\nYou may need to push manually using:")
        print(f"  git push -u origin {current_branch}")
        return False
    
    print("✓ Pushed to GitHub successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Set up GitHub repository for liuyao project"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="GitHub Personal Access Token (with 'repo' scope)"
    )
    parser.add_argument(
        "--name",
        default="liuyao",
        help="Repository name (default: liuyao)"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create a private repository (default: public)"
    )
    parser.add_argument(
        "--description",
        default="A comprehensive Python implementation of the Liu Yao (六爻) divination system",
        help="Repository description"
    )
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Skip pushing to GitHub (just create repo and commit locally)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GitHub Repository Setup for Liu Yao Project")
    print("=" * 60)
    print()
    
    # Step 1: Initialize git
    if not init_git_repo():
        sys.exit(1)
    
    # Step 2: Create GitHub repository
    repo_info = create_github_repo(
        token=args.token,
        repo_name=args.name,
        private=args.private,
        description=args.description
    )
    
    if not repo_info:
        print("\nFailed to create GitHub repository. Exiting.")
        sys.exit(1)
    
    repo_url = repo_info.get("clone_url") or repo_info.get("html_url")
    if not repo_url:
        print("Error: Could not determine repository URL")
        sys.exit(1)
    
    # Step 3: Set up remote
    if not setup_git_remote(repo_url):
        sys.exit(1)
    
    # Step 4: Add and commit files
    if not add_and_commit_files():
        sys.exit(1)
    
    # Step 5: Push to GitHub
    if not args.skip_push:
        if not push_to_github():
            print("\n⚠ Setup completed, but push failed.")
            print("You can push manually later using:")
            print("  git push -u origin main")
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ Setup completed successfully!")
    print("=" * 60)
    print(f"\nRepository URL: {repo_info['html_url']}")
    print(f"Clone URL: {repo_info['clone_url']}")
    print()


if __name__ == "__main__":
    main()

