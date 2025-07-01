from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from database import get_db, create_tables
from schemas import (
    UserCreate, UserResponse, Token, UserLogin,
    HotelPlatformCreate, HotelPlatformUpdate, HotelPlatformResponse, 
    HotelPlatformDetailResponse, PlatformTypeResponse
)
from auth import (
    authenticate_user, 
    create_access_token, 
    verify_token, 
    get_user_by_username, 
    get_user_by_email, 
    create_user,
    encrypt_platform_password,
    decrypt_platform_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import User, HotelPlatform, PlatformType

app = FastAPI(title="호텔 상태 관리 시스템", description="로그인/회원가입 및 호텔 플랫폼 관리 API", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """현재 사용자 조회"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """활성 사용자 확인"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다")
    return current_user

@app.on_event("startup")
def startup_event():
    """애플리케이션 시작 시 테이블 생성"""
    create_tables()

@app.get("/")
def read_root():
    """루트 엔드포인트"""
    return {"message": "호텔 상태 관리 시스템 API에 오신 것을 환영합니다!"}

@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """회원가입 - 이메일과 패스워드만 필요"""
    # 이메일 중복 확인
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 이메일입니다"
        )
    
    # 사용자 생성
    return create_user(db=db, email=user.email, password=user.password)

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 형식 로그인 (토큰 발급) - 이메일 또는 사용자명으로 로그인"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일/사용자명 또는 비밀번호가 잘못되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """일반 로그인 - 이메일로 로그인"""
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """현재 사용자 정보 조회"""
    return current_user

@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_active_user)):
    """보호된 라우트 예시"""
    return {"message": f"안녕하세요, {current_user.full_name or current_user.username}님! 인증된 사용자만 접근할 수 있는 페이지입니다."}

# ==================== 호텔 플랫폼 관리 API ====================

@app.get("/platforms", response_model=List[PlatformTypeResponse])
def get_available_platforms():
    """사용 가능한 플랫폼 목록 조회"""
    return [{"value": platform.value, "name": platform.name} for platform in PlatformType]

@app.post("/hotel-platforms", response_model=HotelPlatformResponse)
def create_hotel_platform(
    platform_data: HotelPlatformCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """호텔 플랫폼 로그인 정보 생성"""
    # 해당 사용자의 플랫폼이 이미 존재하는지 확인
    existing_platform = db.query(HotelPlatform).filter(
        HotelPlatform.user_id == current_user.id,
        HotelPlatform.platform == platform_data.platform
    ).first()
    
    if existing_platform:
        raise HTTPException(
            status_code=400,
            detail=f"{platform_data.platform.value} 플랫폼은 이미 등록되어 있습니다. 수정을 원하시면 PUT 요청을 사용하세요."
        )
    
    # 비밀번호 암호화
    encrypted_login_password = encrypt_platform_password(platform_data.login_password)
    encrypted_mfa_password = encrypt_platform_password(platform_data.mfa_password) if platform_data.mfa_password else None
    
    # 새 플랫폼 정보 생성
    new_platform = HotelPlatform(
        user_id=current_user.id,
        platform=platform_data.platform,
        login_id=platform_data.login_id,
        login_password=encrypted_login_password,
        hotel_name=platform_data.hotel_name,
        mfa_id=platform_data.mfa_id,
        mfa_password=encrypted_mfa_password,
        mfa_platform=platform_data.mfa_platform
    )
    
    db.add(new_platform)
    db.commit()
    db.refresh(new_platform)
    
    return new_platform

@app.get("/hotel-platforms", response_model=List[HotelPlatformResponse])
def get_hotel_platforms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """현재 사용자의 호텔 플랫폼 목록 조회 (비밀번호 제외)"""
    platforms = db.query(HotelPlatform).filter(
        HotelPlatform.user_id == current_user.id
    ).all()
    
    return platforms

@app.get("/hotel-platforms/{platform_id}", response_model=HotelPlatformDetailResponse)
def get_hotel_platform_detail(
    platform_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """특정 호텔 플랫폼 상세 정보 조회 (비밀번호 포함)"""
    platform = db.query(HotelPlatform).filter(
        HotelPlatform.id == platform_id,
        HotelPlatform.user_id == current_user.id
    ).first()
    
    if not platform:
        raise HTTPException(
            status_code=404,
            detail="플랫폼 정보를 찾을 수 없습니다"
        )
    
    # 비밀번호 복호화
    decrypted_login_password = decrypt_platform_password(platform.login_password)
    decrypted_mfa_password = decrypt_platform_password(platform.mfa_password) if platform.mfa_password else None
    
    # 응답 데이터 구성
    response_data = {
        "id": platform.id,
        "user_id": platform.user_id,
        "platform": platform.platform,
        "login_id": platform.login_id,
        "login_password": decrypted_login_password,
        "hotel_name": platform.hotel_name,
        "mfa_id": platform.mfa_id,
        "mfa_password": decrypted_mfa_password,
        "mfa_platform": platform.mfa_platform,
        "created_at": platform.created_at,
        "updated_at": platform.updated_at
    }
    
    return response_data

@app.put("/hotel-platforms/{platform_id}", response_model=HotelPlatformResponse)
def update_hotel_platform(
    platform_id: int,
    platform_data: HotelPlatformUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """호텔 플랫폼 정보 수정"""
    platform = db.query(HotelPlatform).filter(
        HotelPlatform.id == platform_id,
        HotelPlatform.user_id == current_user.id
    ).first()
    
    if not platform:
        raise HTTPException(
            status_code=404,
            detail="플랫폼 정보를 찾을 수 없습니다"
        )
    
    # 수정할 필드들만 업데이트
    update_data = platform_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "login_password" and value:
            # 로그인 비밀번호 암호화
            setattr(platform, field, encrypt_platform_password(value))
        elif field == "mfa_password" and value:
            # MFA 비밀번호 암호화
            setattr(platform, field, encrypt_platform_password(value))
        else:
            setattr(platform, field, value)
    
    db.commit()
    db.refresh(platform)
    
    return platform

@app.delete("/hotel-platforms/{platform_id}")
def delete_hotel_platform(
    platform_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """호텔 플랫폼 정보 삭제"""
    platform = db.query(HotelPlatform).filter(
        HotelPlatform.id == platform_id,
        HotelPlatform.user_id == current_user.id
    ).first()
    
    if not platform:
        raise HTTPException(
            status_code=404,
            detail="플랫폼 정보를 찾을 수 없습니다"
        )
    
    db.delete(platform)
    db.commit()
    
    return {"message": f"{platform.platform.value} 플랫폼 정보가 성공적으로 삭제되었습니다"}

@app.get("/hotel-platforms/platform/{platform_name}", response_model=HotelPlatformDetailResponse)
def get_hotel_platform_by_name(
    platform_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """플랫폼명으로 호텔 플랫폼 정보 조회"""
    # 플랫폼명으로 PlatformType 찾기
    platform_type = None
    for platform in PlatformType:
        if platform.value == platform_name or platform.name == platform_name:
            platform_type = platform
            break
    
    if not platform_type:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 플랫폼입니다"
        )
    
    platform = db.query(HotelPlatform).filter(
        HotelPlatform.user_id == current_user.id,
        HotelPlatform.platform == platform_type
    ).first()
    
    if not platform:
        raise HTTPException(
            status_code=404,
            detail=f"{platform_name} 플랫폼 정보를 찾을 수 없습니다"
        )
    
    # 비밀번호 복호화
    decrypted_login_password = decrypt_platform_password(platform.login_password)
    decrypted_mfa_password = decrypt_platform_password(platform.mfa_password) if platform.mfa_password else None
    
    # 응답 데이터 구성
    response_data = {
        "id": platform.id,
        "user_id": platform.user_id,
        "platform": platform.platform,
        "login_id": platform.login_id,
        "login_password": decrypted_login_password,
        "hotel_name": platform.hotel_name,
        "mfa_id": platform.mfa_id,
        "mfa_password": decrypted_mfa_password,
        "mfa_platform": platform.mfa_platform,
        "created_at": platform.created_at,
        "updated_at": platform.updated_at
    }
    
    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
