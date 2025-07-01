from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class PlatformType(enum.Enum):
    """플랫폼 타입 열거형"""
    YANOLJA = "야놀자"
    YEOGI_BOSS = "여기어때_사장님"
    YEOGI_PARTNER = "여기어때_파트너"
    NAVER = "네이버"
    AIRBNB = "에어비앤비"
    AGODA = "아고다"
    BOOKING = "부킹닷컴"
    EXPEDIA = "익스피디아"

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    hotel_platforms = relationship("HotelPlatform", back_populates="user", cascade="all, delete-orphan")

class HotelPlatform(Base):
    """호텔 플랫폼 로그인 정보 모델"""
    __tablename__ = "hotel_platforms"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum(PlatformType), nullable=False)
    login_id = Column(String(255), nullable=False)
    login_password = Column(String(255), nullable=False)  # 암호화하여 저장
    hotel_name = Column(String(255), nullable=False)
    mfa_id = Column(String(255), nullable=True)
    mfa_password = Column(String(255), nullable=True)  # 암호화하여 저장
    mfa_platform = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="hotel_platforms")
    
    # 유니크 제약 조건: 한 사용자는 플랫폼당 하나의 설정만 가질 수 있음
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='unique_user_platform'),
    ) 