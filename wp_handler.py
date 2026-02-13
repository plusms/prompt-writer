import requests
import base64
from typing import Dict, Any

class WPHandler:
    def __init__(self, site_config: Dict[str, str]):
        self.url = site_config['url'].rstrip('/')
        self.user = site_config['user']
        self.password = site_config['app_password']
        self.api_url = f"{self.url}/wp-json/wp/v2"

    def _get_headers(self):
        credentials = f"{self.user}:{self.password}"
        token = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }

    def post_draft(self, title: str, content: str, slug: str, image_prompts: str = "") -> str:
        """
        Creates a draft post in WordPress. 
        Returns the edit URL (or public URL if published, but we aim for draft).
        """
        # Append image prompts to the bottom of the content for reference, or keep separate?
        # User asked for URL in Col H, Image Prompts in Col I.
        # So we just post the content to WP.
        
        post_data = {
            "title": title,
            "content": content,
            "status": "draft",
            "slug": slug
        }

        try:
            response = requests.post(
                f"{self.api_url}/posts",
                headers=self._get_headers(),
                json=post_data
            )
            response.raise_for_status()
            result = response.json()
            # Return the draft link or edit link
            # 'link' is the view link. 'id' can be constructed to edit link.
            # Usually users want the Preview Link or Edit Link.
            # Let's return the standard link for now.
            return result.get('link')
        except Exception as e:
            print(f"Error posting to WP: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
