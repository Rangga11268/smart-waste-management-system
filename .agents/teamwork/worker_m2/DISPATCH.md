## 2026-11-02T09:24:24Z
From: 82c4b731-bdc8-49c5-a2ec-d29359fafec8
Content:
You are worker_m2, a teamwork_worker subagent.
Your working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2\
Project root: D:\Ngoding\interviewWeb\BillcodeTech

MANDATORY FIRST STEP:
Read:
1. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md (Day 2 requirement R3)
2. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\orchestrator_2\PROJECT.md
3. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day2\handoff.md
4. D:\Ngoding\interviewWeb\BillcodeTech\tests\test_day2_auth.py
5. docs/API_SPECS.md, docs/RUNBOOK.md, docs/FLOWS.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Milestone Scope (M2: JWT Authentication & Role-Based Access Control):
You will implement JWT authentication endpoints and RBAC dependencies:

1. `backend/app/core/security.py`:
   - `hash_password(password: str) -> str`: use native `bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')`.
   - `verify_password(plain_password: str, hashed_password: str) -> bool`: use native `bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))`.
   - `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`: encode HS256 JWT using `settings.JWT_SECRET` with `exp` timestamp. Payload must include `sub` (str representation of user UUID), `email`, `role`.
   - `decode_access_token(token: str) -> dict`: decode using `settings.JWT_SECRET` and `settings.ALGORITHM` ("HS256"). Raise JWTError on expired or invalid signature.

2. `backend/app/schemas/auth.py`:
   - Pydantic models matching `docs/API_SPECS.md`:
     - `RegisterRequest`: `full_name` (str), `email` (EmailStr), `password` (str), `phone_number` (Optional[str] = None)
     - `LoginRequest`: `email` (EmailStr), `password` (str)
     - `UserSummary`: `id` (UUID or str), `email` (str), `full_name` (str), `role` (str), `created_at` (Optional[datetime] = None)
     - `TokenResponseData`: `access_token` (str), `token_type` (str = "bearer"), `user`: `UserSummary`
     - Response envelope formats matching `docs/API_SPECS.md`:
       - Register: `{"status": "success", "message": "User registered successfully", "data": UserSummary}`
       - Login: `{"status": "success", "data": TokenResponseData}`
       - Me: `{"status": "success", "data": UserSummary}`

3. `backend/app/api/deps.py`:
   - Re-export `get_db` from `app.core.database`.
   - `oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)`.
   - `get_current_user`:
     - Reads token from `oauth2_scheme` (or `Authorization: Bearer <token>` header).
     - If missing: `raise HTTPException(status_code=401, detail="Not authenticated")`.
     - Decodes JWT. Extracts `sub`. **Critical Advisory from Reviewer**: Parse `sub` with `uuid.UUID(sub)` before querying SQLAlchemy SQLite session to avoid `'str' object has no attribute 'hex'` error!
     - Queries `db.query(User).filter(User.id == user_uuid).first()`.
     - If user not found: `raise HTTPException(status_code=401, detail="Could not validate credentials")`.
     - If not `user.is_active`: `raise HTTPException(status_code=401, detail="User account is inactive")`.
     - Returns `user`.
   - `get_current_admin`:
     - Depends on `current_user: User = Depends(get_current_user)`.
     - If `current_user.role != "admin"`: `raise HTTPException(status_code=403, detail="Admin access required")`.
     - Returns `current_user`.

4. `backend/app/api/v1/auth.py`:
   - `POST /register`:
     - Status code: `201 Created`.
     - Checks if `db.query(User).filter(User.email == payload.email).first()` exists: if so, `raise HTTPException(status_code=400, detail="Email already registered")`.
     - Creates `User` with `password_hash = hash_password(payload.password)` and `role = "user"`.
     - Commits and returns 201 response.
   - `POST /login`:
     - Accepts JSON (`LoginRequest`) or form data (`OAuth2PasswordRequestForm` / Request body).
     - Finds user by email. If not found or not `verify_password(password, user.password_hash)`: `raise HTTPException(status_code=401, detail="Invalid email or password")`.
     - If not `user.is_active`: `raise HTTPException(status_code=401, detail="User account is inactive")`.
     - Generates JWT token with `{"sub": str(user.id), "email": user.email, "role": user.role}`.
     - Returns 200 response with `access_token`, `token_type: "bearer"`, and `user` summary.
   - `GET /me`:
     - Depends on `get_current_user`.
     - Returns 200 response with authenticated user details.

5. Connect router to `backend/app/main.py`:
   - Mount router under `prefix=f"{settings.API_V1_STR}/auth"`.

Verification:
- Execute `pytest tests/test_day2_auth.py -v`. All 14 tests in the test suite MUST pass!
- Execute `pytest tests/test_day2_db_fallback.py` to ensure 0 regressions.

Write your report to `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2\handoff.md`.
Follow Handoff Protocol. Send a message to your caller when done.
