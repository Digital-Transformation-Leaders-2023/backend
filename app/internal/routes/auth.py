from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.internal.repository.user import UserRepository

SECRET_KEY = "fb7e694502a64cadab462ffe062ee5219c70f7b52fcd919ffe6974c608c43c29"
ALGORITHM = "HS256"

db = UserRepository()

router = APIRouter(
    prefix='/api/v1/auth'
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    username: str
    email: str or None = None


class UserInDB(User):
    password_hash: str


pwd_context = CryptContext(schemes=["bcrypt"], depreacted="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hash):
    return pwd_context.verify(plain_password, hash)


def get_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

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

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(from_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(from_data.username, from_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sign-up", response_model=Token)
async def login_for_access_token(from_data: OAuth2PasswordRequestForm = Depends()):
    db.add_user(user=User(
        username=from_data.username,
        pass_hash=get_hash(from_data.password),
    ))

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": from_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
