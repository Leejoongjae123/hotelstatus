from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, HotelPlatform
from schemas import TokenData
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
import base64

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# 비밀번호 해시 컨텍스트 (사용자 패스워드용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 플랫폼 비밀번호 암호화용 키 생성 (환경변수에서 가져오거나 생성)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # 키가 없으면 새로 생성 (실제 운영환경에서는 미리 생성해서 환경변수에 저장해야 함)
    ENCRYPTION_KEY = Fernet.generate_key()
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()

cipher_suite = Fernet(ENCRYPTION_KEY)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해시화"""
    return pwd_context.hash(password)

def encrypt_platform_password(password: str) -> str:
    """플랫폼 비밀번호 암호화"""
    if not password:
        return ""
    encrypted_password = cipher_suite.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted_password).decode()

def decrypt_platform_password(encrypted_password: str) -> str:
    """플랫폼 비밀번호 복호화"""
    if not encrypted_password:
        return ""
    try:
        decoded_password = base64.urlsafe_b64decode(encrypted_password.encode())
        decrypted_password = cipher_suite.decrypt(decoded_password)
        return decrypted_password.decode()
    except Exception:
        return ""

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

def authenticate_user(db: Session, email: str, password: str):
    """사용자 인증 - 이메일로만 로그인 가능"""
    # 이메일로 검색
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user_by_username(db: Session, username: str):
    """사용자명으로 사용자 조회"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """이메일로 사용자 조회"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str):
    """사용자 생성 - 이메일과 패스워드만으로 생성"""
    hashed_password = get_password_hash(password)
    # username을 이메일 주소로 설정 (@ 이전 부분 사용)
    username = email.split('@')[0]
    
    # 동일한 username이 있으면 숫자를 붙여서 유니크하게 만들기
    original_username = username
    counter = 1
    while get_user_by_username(db, username):
        username = f"{original_username}{counter}"
        counter += 1
    
    db_user = User(
        username=username,
        email=email,
        full_name=None,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user 