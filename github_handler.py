import requests
import base64
import json

class GitHubHandler:
    def __init__(self, token, repo_name):
        """
        Args:
            token: GitHub Personal Access Token (repo scope)
            repo_name: "username/repo" string
        """
        self.token = token
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_name}/contents"

    def get_file_sha(self, file_path):
        """Gets the SHA of a file to allow updates."""
        try:
            url = f"{self.base_url}/{file_path}"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("sha")
            return None
        except Exception as e:
            print(f"Error getting SHA: {e}")
            return None

    def commit_file(self, file_path, content, message="Update config via Streamlit App"):
        """
        Commits a file to the repository.
        Args:
            file_path: Relative path in repo (e.g., "config/prompts.json")
            content: String content to write
            message: Commit message
        """
        try:
            url = f"{self.base_url}/{file_path}"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # 1. Get current SHA (if exists)
            sha = self.get_file_sha(file_path)
            
            # 2. Prepare payload
            # Content must be base64 encoded
            content_bytes = content.encode("utf-8")
            base64_content = base64.b64encode(content_bytes).decode("utf-8")
            
            data = {
                "message": message,
                "content": base64_content
            }
            if sha:
                data["sha"] = sha
                
            # 3. Send PUT request
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                return True, "Success"
            else:
                return False, f"GitHub API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"Exception: {e}"
