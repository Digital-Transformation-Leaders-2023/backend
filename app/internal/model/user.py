from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    pass_hash: str
    email: str
