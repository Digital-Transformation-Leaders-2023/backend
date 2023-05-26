from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ReportFilter:
    limit: int = 10
    skip: int = 0
    is_favorite: Optional[bool] = None
    age: Optional[str] = None
    sex: Optional[str] = None
    mkb_code: Optional[str] = None
