import requests
import os

SOCIAL_MEDIA_APIS = {
    "facebook": os.getenv("FACEBOOK_GRAPH_API"),
    "instagram": os.getenv("INSTAGRAM_API"),
    "linkedin": os.getenv("LINKEDIN_API")
}

def post_social_media(platform: str, content: dict):
    """ Publica um post em redes sociais (Facebook, Instagram, LinkedIn) """
    if platform not in SOCIAL_MEDIA_APIS:
        raise ValueError(f"Plataforma '{platform}' não suportada")

    url = f"{SOCIAL_MEDIA_APIS[platform]}/posts"
    response = requests.post(url, json=content)
    return response.json()

    class SocialMediaError(Exception):
        """Custom exception for social media operations"""
        pass

    def get_social_media_post(platform: str, post_id: str) -> dict:
        """Retrieve a post from social media platform"""
        if platform not in SOCIAL_MEDIA_APIS:
            raise ValueError(f"Platform '{platform}' not supported")
        
        url = f"{SOCIAL_MEDIA_APIS[platform]}/posts/{post_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise SocialMediaError(f"Failed to get post: {str(e)}")

    def delete_social_media_post(platform: str, post_id: str) -> bool:
        """Delete a post from social media platform"""
        if platform not in SOCIAL_MEDIA_APIS:
            raise ValueError(f"Platform '{platform}' not supported")
        
        url = f"{SOCIAL_MEDIA_APIS[platform]}/posts/{post_id}"
        try:
            response = requests.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise SocialMediaError(f"Failed to delete post: {str(e)}")
