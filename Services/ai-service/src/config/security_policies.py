class SecurityPolicies:
    PASSWORD_COMPLEXITY = {
        "min_length": 12,
        "require_uppercase": True,
        "require_special_char": True
    }
    JWT_EXPIRATION_TIME = 3600  # 1 hora
    MAX_FAILED_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION = 600  # 10 minutos

security_policies = SecurityPolicies()
class SecurityPolicies:
    def __init__(self):
        self._initialize_policies()

    def _initialize_policies(self):
        self.PASSWORD_COMPLEXITY = {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_char": True,
            "max_length": 128,
            "forbidden_patterns": ['password', '123', 'admin']
        }
        
        self.JWT_CONFIG = {
            "access_token_expire": 3600,  # 1 hour
            "refresh_token_expire": 604800,  # 7 days
            "algorithm": "HS256",
            "token_type": "Bearer"
        }
        
        self.ACCOUNT_SECURITY = {
            "max_failed_attempts": 5,
            "lockout_duration": 600,  # 10 minutes
            "password_history": 5,  # remember last 5 passwords
            "password_expiry_days": 90,
            "session_timeout": 1800  # 30 minutes
        }
        
        self.RATE_LIMITING = {
            "window_size": 300,  # 5 minutes
            "max_requests": 100
        }

security_policies = SecurityPolicies()