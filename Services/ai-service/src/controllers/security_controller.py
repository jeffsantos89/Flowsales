from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional
from security.auth import create_token, verify_token, refresh_token
from security.encryption import encrypt_data, decrypt_data
from security.permissions import require_role, Role, get_current_user_role
from security.waf_rules import check_request_for_threats
from security.ratelimiter import get_rate_usage
from security.security_config import settings
from log_config import structured_log

router = APIRouter(prefix="/auth", tags=["Security & Auth"])

### === Schemas === ###
class LoginRequest(BaseModel):
    user_id: str
    role: Role

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class VerifyRequest(BaseModel):
    token: str

class EncryptRequest(BaseModel):
    data: dict

class DecryptRequest(BaseModel):
    token: str

class PermissionCheckRequest(BaseModel):
    role: Role

class PermissionCheckResponse(BaseModel):
    allowed: bool
    current_role: Role

class WAFTestRequest(BaseModel):
    url: Optional[str]
    headers: Optional[dict]
    body: Optional[dict]

### === Routes === ###

@router.post("/token", response_model=TokenResponse)
async def generate_token(request: LoginRequest):
    tokens = create_token(user_id=request.user_id, role=request.role)
    return TokenResponse(**tokens)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(payload: RefreshRequest):
    tokens = refresh_token(payload.refresh_token)
    return TokenResponse(**tokens)

@router.post("/verify")
async def verify_jwt(payload: VerifyRequest):
    return verify_token(payload.token)

@router.post("/encrypt")
async def encrypt(payload: EncryptRequest):
    token = encrypt_data(payload.data)
    return {"token": token}

@router.post("/decrypt")
async def decrypt(payload: DecryptRequest):
    return decrypt_data(payload.token)

@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_permission(payload: PermissionCheckRequest, role: Role = Depends(get_current_user_role)):
    return PermissionCheckResponse(
        allowed=role.value >= payload.role.value,
        current_role=role
    )

@router.post("/waf/test")
async def waf_inspection(payload: WAFTestRequest):
    threats = check_request_for_threats(payload.url, payload.headers, payload.body)
    return {"threats_detected": threats}

@router.get("/rate/usage")
async def rate_limit_usage(request: Request):
    usage = get_rate_usage(request)
    return {"rate_limit_usage": usage}

    # Health check endpoint
    @router.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "healthy", "service": "security-service"}

    # Security metrics endpoint
    @router.get("/metrics")
    @require_role(Role.ADMIN)
    async def security_metrics():
        return {
            "rate_limit_breaches": settings.rate_limiter.get_breach_count(),
            "waf_blocks": settings.waf.get_block_count(),
            "token_validations": settings.token_metrics.get_validation_count()
        }

    # Batch token validation
    @router.post("/verify/batch")
    async def verify_multiple_tokens(tokens: list[str]):
        results = [verify_token(token) for token in tokens]
        return {"results": results}

    # Emergency security lockdown
    @router.post("/emergency/lockdown")
    @require_role(Role.ADMIN)
    async def emergency_lockdown():
        settings.security_level = "MAXIMUM"
        structured_log.warning("Emergency security lockdown activated")
        return {"status": "locked_down", "security_level": "MAXIMUM"}

    # Token revocation
    @router.post("/token/revoke")
    @require_role(Role.ADMIN)
    async def revoke_token(token: str):
        settings.token_blacklist.add(token)
        structured_log.info("Token revoked", token_hash=hash(token))
        return {"status": "revoked"}

    # Security configuration status
    @router.get("/config/status")
    @require_role(Role.ADMIN)
    async def security_config_status():
        return {
            "waf_enabled": settings.waf_enabled,
            "rate_limit_enabled": settings.rate_limit_enabled,
            "encryption_algorithm": settings.encryption_algorithm,
            "token_expiry": settings.token_expiry,
            "security_level": settings.security_level
        }