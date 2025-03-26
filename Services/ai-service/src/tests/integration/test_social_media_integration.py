import unittest
from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime
import json
import os
from typing import Dict, Any
from src.services.social_media_service import SocialMediaService
from src.models.social_media_post import SocialMediaPost

# Assuming these are your actual service/model imports
from src.exceptions.social_media_exceptions import (
    SocialMediaConnectionError,
    PostCreationError,
    InvalidContentError
)

class TestSocialMediaIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        cls.test_credentials = {
            "api_key": os.getenv("SOCIAL_MEDIA_API_KEY", "test_key"),
            "api_secret": os.getenv("SOCIAL_MEDIA_API_SECRET", "test_secret"),
            "access_token": os.getenv("SOCIAL_MEDIA_ACCESS_TOKEN", "test_token")
        }

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.social_media_service = SocialMediaService(credentials=self.test_credentials)
        self.sample_post = SocialMediaPost(
            content="Test post content",
            media_urls=["http://example.com/image.jpg"],
            scheduled_time=datetime.now(),
            platforms=["twitter", "facebook"]
        )

    @pytest.mark.integration
    @patch('src.services.social_media_service.TwitterAPI')
    @patch('src.services.social_media_service.FacebookAPI')
    def test_post_creation_success(self, mock_facebook, mock_twitter):
        """Test successful post creation across multiple platforms"""
        # Configure mocks
        mock_twitter.post.return_value = {"id": "123", "status": "success"}
        mock_facebook.post.return_value = {"id": "456", "status": "success"}

        # Execute test
        result = self.social_media_service.create_post(self.sample_post)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.platform_responses), 2)
        self.assertEqual(result.platform_responses["twitter"]["id"], "123")
        self.assertEqual(result.platform_responses["facebook"]["id"], "456")

    @pytest.mark.integration
    def test_post_validation(self):
        """Test post content validation"""
        invalid_posts = [
            SocialMediaPost(content="", platforms=["twitter"]),  # Empty content
            SocialMediaPost(content="x" * 1001, platforms=["twitter"]),  # Too long
            SocialMediaPost(content="Valid", platforms=[]),  # No platforms
        ]

        for post in invalid_posts:
            with self.assertRaises(InvalidContentError):
                self.social_media_service.validate_post(post)

    @pytest.mark.integration
    @patch('src.services.social_media_service.TwitterAPI')
    def test_connection_error_handling(self, mock_twitter):
        """Test handling of connection errors"""
        mock_twitter.post.side_effect = SocialMediaConnectionError("Connection failed")

        post = SocialMediaPost(
            content="Test content",
            platforms=["twitter"]
        )

        with self.assertRaises(SocialMediaConnectionError):
            self.social_media_service.create_post(post)

    @pytest.mark.integration
    def test_media_upload(self):
        """Test media file upload functionality"""
        test_image_path = os.path.join(os.path.dirname(__file__), 'test_data/test_image.jpg')
        
        post_with_media = SocialMediaPost(
            content="Post with media",
            media_urls=[test_image_path],
            platforms=["instagram"]
        )

        # Mock the media upload process
        with patch.object(self.social_media_service, '_upload_media') as mock_upload:
            mock_upload.return_value = {"media_id": "789"}
            result = self.social_media_service.create_post(post_with_media)
            
            self.assertTrue(result.success)
            self.assertIn("media_id", result.platform_responses["instagram"])

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Create multiple posts in quick succession
        posts = [
            SocialMediaPost(content=f"Test post {i}", platforms=["twitter"])
            for i in range(5)
        ]

        with patch.object(self.social_media_service, '_check_rate_limit') as mock_rate_limit:
            for post in posts:
                self.social_media_service.create_post(post)
            
            # Verify rate limit was checked for each post
            self.assertEqual(mock_rate_limit.call_count, 5)

    def tearDown(self):
        """Clean up after each test method"""
        self.social_media_service = None

if __name__ == '__main__':
    unittest.main()