# 호텔 플랫폼 관리 API 사용 가이드

## 개요
로그인된 사용자의 정보를 기반으로 8개 플랫폼(야놀자, 여기어때_사장님, 여기어때_파트너, 네이버, 에어비앤비, 아고다, 부킹닷컴, 익스피디아)의 로그인 정보를 저장/관리할 수 있는 CRUD API입니다.

## 지원하는 플랫폼
- 야놀자 (YANOLJA)
- 여기어때_사장님 (YEOGI_BOSS)
- 여기어때_파트너 (YEOGI_PARTNER)
- 네이버 (NAVER)
- 에어비앤비 (AIRBNB)
- 아고다 (AGODA)
- 부킹닷컴 (BOOKING)
- 익스피디아 (EXPEDIA)

## API 엔드포인트

### 1. 사용 가능한 플랫폼 목록 조회
```
GET /platforms
```

**응답 예시:**
```json
[
  {"value": "야놀자", "name": "YANOLJA"},
  {"value": "여기어때_사장님", "name": "YEOGI_BOSS"},
  {"value": "여기어때_파트너", "name": "YEOGI_PARTNER"},
  {"value": "네이버", "name": "NAVER"},
  {"value": "에어비앤비", "name": "AIRBNB"},
  {"value": "아고다", "name": "AGODA"},
  {"value": "부킹닷컴", "name": "BOOKING"},
  {"value": "익스피디아", "name": "EXPEDIA"}
]
```

### 2. 호텔 플랫폼 정보 생성 (CREATE)
```
POST /hotel-platforms
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 본문:**
```json
{
  "platform": "야놀자",
  "login_id": "yanolja_user@example.com",
  "login_password": "yanolja_password123",
  "hotel_name": "그랜드 호텔",
  "mfa_id": "010-1234-5678",
  "mfa_password": "mfa_code_123",
  "mfa_platform": "SMS"
}
```

**응답 예시:**
```json
{
  "id": 1,
  "user_id": 1,
  "platform": "야놀자",
  "login_id": "yanolja_user@example.com",
  "hotel_name": "그랜드 호텔",
  "mfa_id": "010-1234-5678",
  "mfa_platform": "SMS",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null
}
```

### 3. 사용자의 모든 플랫폼 정보 조회 (READ - 목록)
```
GET /hotel-platforms
Authorization: Bearer <access_token>
```

**응답 예시:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "platform": "야놀자",
    "login_id": "yanolja_user@example.com",
    "hotel_name": "그랜드 호텔",
    "mfa_id": "010-1234-5678",
    "mfa_platform": "SMS",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": null
  },
  {
    "id": 2,
    "user_id": 1,
    "platform": "에어비앤비",
    "login_id": "airbnb_user@example.com",
    "hotel_name": "코지 게스트하우스",
    "mfa_id": "010-9876-5432",
    "mfa_platform": "Google Authenticator",
    "created_at": "2024-01-01T12:30:00",
    "updated_at": null
  }
]
```

### 4. 특정 플랫폼 정보 상세 조회 (READ - 상세, 비밀번호 포함)
```
GET /hotel-platforms/{platform_id}
Authorization: Bearer <access_token>
```

**응답 예시:**
```json
{
  "id": 1,
  "user_id": 1,
  "platform": "야놀자",
  "login_id": "yanolja_user@example.com",
  "login_password": "yanolja_password123",
  "hotel_name": "그랜드 호텔",
  "mfa_id": "010-1234-5678",
  "mfa_password": "mfa_code_123",
  "mfa_platform": "SMS",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null
}
```

### 5. 플랫폼명으로 정보 조회
```
GET /hotel-platforms/platform/{platform_name}
Authorization: Bearer <access_token>
```

**예시:** `GET /hotel-platforms/platform/야놀자`

### 6. 플랫폼 정보 수정 (UPDATE)
```
PUT /hotel-platforms/{platform_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 본문 (부분 수정 가능):**
```json
{
  "login_password": "new_password123",
  "hotel_name": "업데이트된 호텔명",
  "mfa_password": "new_mfa_code_456"
}
```

### 7. 플랫폼 정보 삭제 (DELETE)
```
DELETE /hotel-platforms/{platform_id}
Authorization: Bearer <access_token>
```

**응답 예시:**
```json
{
  "message": "야놀자 플랫폼 정보가 성공적으로 삭제되었습니다"
}
```

## 사용 전 준비사항

### 1. 회원가입
```
POST /signup
Content-Type: application/json
```

**요청 본문:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### 2. 로그인 (토큰 발급)
```
POST /login
Content-Type: application/json
```

**요청 본문:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**응답:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## 보안 기능

1. **사용자 인증**: JWT 토큰을 사용한 인증 시스템
2. **비밀번호 암호화**: 플랫폼 로그인 비밀번호와 MFA 비밀번호는 Fernet 암호화로 저장
3. **사용자별 격리**: 각 사용자는 자신의 플랫폼 정보만 접근 가능
4. **플랫폼별 유일성**: 한 사용자는 플랫폼당 하나의 설정만 가질 수 있음

## 에러 처리

- **400**: 잘못된 요청 (이미 등록된 플랫폼, 지원하지 않는 플랫폼 등)
- **401**: 인증되지 않은 요청
- **404**: 리소스를 찾을 수 없음
- **422**: 유효하지 않은 데이터

## 테스트 방법

1. 서버 실행: `python main.py`
2. API 문서 확인: `http://localhost:8000/docs`
3. Swagger UI에서 직접 테스트 가능

## 환경 변수

`.env` 파일에 다음 변수들을 설정해주세요:

```
SECRET_KEY=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_for_platform_passwords
DATABASE_URL=postgresql://username:password@localhost/dbname
```

## 데이터베이스 스키마

### Users 테이블
- id (PK)
- username
- email
- hashed_password
- full_name
- is_active
- created_at
- updated_at

### HotelPlatforms 테이블
- id (PK)
- user_id (FK to Users)
- platform (Enum)
- login_id
- login_password (암호화)
- hotel_name
- mfa_id
- mfa_password (암호화)
- mfa_platform
- created_at
- updated_at

**제약조건:** (user_id, platform) 조합은 유니크해야 함 