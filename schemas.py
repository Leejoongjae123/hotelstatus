from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import PlatformType

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    """사용자 생성 스키마 - 이메일과 패스워드만 필요"""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """로그인 스키마 - 이메일로 로그인"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """토큰 데이터 스키마"""
    username: Optional[str] = None

# HotelPlatform 관련 스키마
class HotelPlatformBase(BaseModel):
    """호텔 플랫폼 기본 스키마"""
    platform: PlatformType
    login_id: str
    login_password: str
    hotel_name: str
    mfa_id: Optional[str] = None
    mfa_password: Optional[str] = None
    mfa_platform: Optional[str] = None

class HotelPlatformCreate(HotelPlatformBase):
    """호텔 플랫폼 생성 스키마"""
    pass

class HotelPlatformUpdate(BaseModel):
    """호텔 플랫폼 수정 스키마"""
    login_id: Optional[str] = None
    login_password: Optional[str] = None
    hotel_name: Optional[str] = None
    mfa_id: Optional[str] = None
    mfa_password: Optional[str] = None
    mfa_platform: Optional[str] = None

class HotelPlatformResponse(BaseModel):
    """호텔 플랫폼 응답 스키마"""
    id: int
    user_id: int
    platform: PlatformType
    login_id: str
    hotel_name: str
    mfa_id: Optional[str] = None
    mfa_platform: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class HotelPlatformDetailResponse(HotelPlatformResponse):
    """호텔 플랫폼 상세 응답 스키마 (비밀번호 포함)"""
    login_password: str
    mfa_password: Optional[str] = None

class PlatformTypeResponse(BaseModel):
    """플랫폼 타입 응답 스키마"""
    value: str
    name: str 