import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GitHubClientError(Exception):
    """Base exception for GitHub client errors"""

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPOSITORY")
        self.pr_number = os.getenv("PR_NUMBER")

        if not all([self.token, self.repo, self.pr_number]):
            missing = []
            if not self.token: missing.append("GITHUB_TOKEN")
            if not self.repo: missing.append("GITHUB_REPOSITORY")
            if not self.pr_number: missing.append("PR_NUMBER")
            raise GitHubClientError(f"Missing environment variables: {', '.join(missing)}")

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Universal request handler with error catching"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            **kwargs.pop('headers', {})
        }

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()

            # Check rate limits
            if int(response.headers.get('X-RateLimit-Remaining', 1000)) < 100:
                logger.warning("GitHub API rate limit approaching: %s/%s remaining",
                               response.headers['X-RateLimit-Remaining'],
                               response.headers['X-RateLimit-Limit'])

            return response

        except requests.exceptions.HTTPError as e:
            logger.error("GitHub API error: %s", e.response.text)
            raise GitHubClientError(f"API request failed: {e}") from e
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error: %s", str(e))
            raise GitHubClientError("Network connection failed") from e
        except Exception as e:
            logger.error("Unexpected error: %s", str(e), exc_info=True)
            raise GitHubClientError("Unexpected error occurred") from e

    def get_pr_diff(self) -> Optional[str]:
        """Retrieve PR diff with error handling"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/pulls/{self.pr_number}"
            response = self._make_request('GET', url, headers={'Accept': 'application/vnd.github.v3.diff'})
            return response.text
        except GitHubClientError as e:
            logger.error("Failed to get PR diff: %s", str(e))
            return None

    def post_comment(self, body: str) -> bool:
        """Post PR comment with validation"""
        if not body.strip():
            logger.error("Attempted to post empty comment")
            return False

        try:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"
            self._make_request('POST', url, json={'body': body})
            logger.info("Successfully posted PR comment")
            return True
        except GitHubClientError as e:
            logger.error("Failed to post comment: %s", str(e))
            return False