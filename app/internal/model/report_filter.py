from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ReportFilter:
    limit: int = 10
    skip: int = 1
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    sex: Optional[str] = None
    mkb_code: Optional[str] = None
    sort_dir: Optional[str] = None
    sort_column: Optional[str] = None
      
    is_favorite: Optional[bool] = None
    age: Optional[str] = None
