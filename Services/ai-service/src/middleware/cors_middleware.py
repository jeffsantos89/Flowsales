from fastapi.middleware.cors import CORSMiddleware
from typing import List
from decouple import config
from functools import lru_cache

@lru_cache()
def get_allowed_origins() -> List[str]:
    """Get allowed origins from environment variables"""
    origins_str = config('ALLOWED_ORIGINS', default='http://localhost:3000,http://localhost:8000')
    return origins_str.split(',')

def configure_cors(app):
    """Configure CORS with secure settings for production"""
    
    # Get environment
    ENV = config('ENV', default='development')
    
    # Security headers
    security_headers = [
        'Authorization',
        'Content-Type',
        'Accept',
        'Origin',
        'X-Requested-With',
    ]

    # Allowed methods
    allowed_methods = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins() if ENV == 'production' else ["*"],
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=security_headers,
        max_age=3600,  # Cache preflight requests for 1 hour
        expose_headers=["Content-Disposition"]  # Needed for file downloads
    )
