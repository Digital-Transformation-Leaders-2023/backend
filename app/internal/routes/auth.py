from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.internal.repository.user import UserRepository
from app.internal.model.user import UserModel, UserCreate, UserResponse
from app.pkg.authentication_provider.auth import AuthProvider
from fastapi.responses import JSONResponse

SECRET_KEY = "fb7e694502a64cadab462ffe062ee5219c70f7b52fcd919ffe6974c608c43c29"
ALGORITHM = "HS256"

router = APIRouter(
    prefix=''
)

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)

db = UserRepository()
auth_provider = AuthProvider()

EMAIL_ALREADY_REGISTERED_RESPONSE = JSONResponse(
    content={"message": "this email already registered"}, status_code=status.HTTP_409_CONFLICT
)
ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration_time_in_minutes: timedelta


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    username: str
    email: str or None = None


class UserInDB(User):
    password_hash: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(email: str, password: str):
    user = db.get_user_by_email(email)
    if not user:
        return False
    if not auth_provider.verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRES

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = db.get_user_by_username(token_data.username)
    if user is None:
        raise credential_exception

    return user


@router.post("/token", response_model=Token)
async def login(from_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(from_data.username, from_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=ACCESS_TOKEN_EXPIRES)
    return {
        "expiration_time_in_minutes": ACCESS_TOKEN_EXPIRES,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/signup", summary="Create new user", response_model=Token)
async def create_user(from_data: UserCreate):
    user = UserModel(
        username=from_data.username,
        password_hash=auth_provider.get_password_hash(from_data.password),
        email=from_data.email
    )
    res = db.get_user_by_email(user.email)
    if res is not None:
        return EMAIL_ALREADY_REGISTERED_RESPONSE
    db.add_user(user)

    access_token = create_access_token(
        data={"sub": from_data.username}, expires_delta=ACCESS_TOKEN_EXPIRES)
    return {
        "expiration_time_in_minutes": ACCESS_TOKEN_EXPIRES,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get('/me', summary="Get details about user", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
    }
