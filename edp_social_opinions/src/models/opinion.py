from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Opinion:
    source: str                          # glassdoor | indeed | linkedin | twitter
    company: str
    author: Optional[str]
    role: Optional[str]
    location: Optional[str]
    rating: Optional[float]              # 1-5 scale where applicable
    title: Optional[str]
    text: str
    pros: Optional[str]
    cons: Optional[str]
    date: Optional[str]
    url: Optional[str]
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    language: Optional[str] = None
    employment_status: Optional[str] = None  # current | former
    recommends: Optional[bool] = None

    def to_dict(self) -> dict:
        return asdict(self)
