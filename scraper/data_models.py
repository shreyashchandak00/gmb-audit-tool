from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass
class BusinessHours:
    day: str
    hours: str  # e.g. "9 AM - 5 PM" or "Closed"


@dataclass
class BusinessProfile:
    url: str
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    photos_count: Optional[int] = None
    hours: list[BusinessHours] = field(default_factory=list)
    description: Optional[str] = None
    owner_response_ratio: Optional[float] = None  # 0.0 to 1.0


class Severity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class IssueType(Enum):
    MISSING_WEBSITE = "missing_website"
    LOW_RATING = "low_rating"
    MODERATE_RATING = "moderate_rating"
    FEW_REVIEWS = "few_reviews"
    NO_REVIEWS = "no_reviews"
    FEW_PHOTOS = "few_photos"
    NO_PHOTOS = "no_photos"
    INCOMPLETE_HOURS = "incomplete_hours"
    NO_HOURS = "no_hours"
    MISSING_DESCRIPTION = "missing_description"
    NO_OWNER_RESPONSES = "no_owner_responses"
    LOW_OWNER_RESPONSES = "low_owner_responses"
    MISSING_PHONE = "missing_phone"
    MISSING_CATEGORY = "missing_category"


@dataclass
class AuditIssue:
    issue_type: IssueType
    severity: Severity
    title: str
    description: str
    recommendation: str
    points_deducted: int


@dataclass
class AuditResult:
    profile: BusinessProfile
    score: int
    grade: str
    grade_label: str
    grade_color: str
    issues: list[AuditIssue] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.INFO)
