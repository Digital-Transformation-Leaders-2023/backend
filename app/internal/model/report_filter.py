from dataclasses import dataclass


@dataclass(frozen=True)
class ReportFilter:
    age: str
    sex: str
    mkb_code: str