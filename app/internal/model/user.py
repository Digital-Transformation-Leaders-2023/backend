from dataclasses import dataclass


@dataclass(frozen=True)
class UserCreate:
    username: str
    password: str
    email: str


@dataclass(frozen=True)
class UserSignin:
    email: str
    password: str


@dataclass(frozen=True)
class UserModel:
    username: str
    password_hash: str
    email: str


@dataclass(frozen=True)
class UserResponse:
    username: str
    email: str
