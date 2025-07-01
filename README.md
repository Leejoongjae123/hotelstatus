# 호텔 상태 관리 시스템 - 로그인/회원가입 API

FastAPI와 PostgreSQL을 이용한 사용자 인증 시스템입니다.

## 주요 기능

- 🔐 사용자 회원가입
- 🔑 로그인 (JWT 토큰 기반)
- 🛡️ 비밀번호 암호화 (bcrypt)
- 🔒 보호된 엔드포인트 접근
- 📊 사용자 정보 관리

## 기술 스택

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:
```env
DATABASE_URL=postgresql://hotelstatus:dlwndwo2!@34.81.137.138:5432/postgres
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 애플리케이션 실행
```bash
python main.py
```
또는
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인
브라우저에서 다음 주소로 접속하세요:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 🏠 기본
- `GET /` - 웰컴 메시지

### 👤 인증
- `POST /signup` - 회원가입
- `POST /login` - 로그인 (JSON 형식)
- `POST /token` - 로그인 (OAuth2 형식)

### 🔒 보호된 엔드포인트
- `GET /users/me` - 현재 사용자 정보 조회
- `GET /protected` - 보호된 라우트 예시

## 사용 예시

### 회원가입
```bash
curl -X POST "http://localhost:8000/signup" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpassword123",
       "full_name": "테스트 사용자"
     }'
```

### 로그인
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "testpassword123"
     }'
```

### 보호된 엔드포인트 접근
```bash
curl -X GET "http://localhost:8000/users/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 데이터베이스 구조

### users 테이블
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | Integer | 기본키 (자동증가) |
| username | String(50) | 사용자명 (유니크) |
| email | String(100) | 이메일 (유니크) |
| hashed_password | String(255) | 암호화된 비밀번호 |
| full_name | String(100) | 전체 이름 (선택사항) |
| is_active | Boolean | 활성 상태 |
| created_at | DateTime | 생성일시 |
| updated_at | DateTime | 수정일시 |

## 보안 기능

- ✅ 비밀번호 bcrypt 해싱
- ✅ JWT 토큰 기반 인증
- ✅ 토큰 만료 시간 설정
- ✅ 사용자명/이메일 중복 방지
- ✅ 활성 사용자 확인

## 주의사항

⚠️ **운영환경에서는 반드시 다음을 변경하세요:**
- `SECRET_KEY`를 강력한 랜덤 문자열로 변경
- 데이터베이스 연결 정보를 환경변수로 관리
- HTTPS 사용 권장 