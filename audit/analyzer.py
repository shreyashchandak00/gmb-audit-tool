from scraper.data_models import (
    BusinessProfile, AuditResult, AuditIssue, IssueType, Severity
)
from audit.recommendations import RECOMMENDATIONS
from config import THRESHOLDS, GRADES


class ProfileAuditor:

    def __init__(self, profile: BusinessProfile):
        self.profile = profile
        self.issues: list[AuditIssue] = []
        self.score = 100

    def run_audit(self) -> AuditResult:
        self._check_website()
        self._check_rating()
        self._check_reviews()
        self._check_photos()
        self._check_hours()
        self._check_description()
        self._check_owner_responses()
        self._check_phone()
        self._check_category()

        self.score = max(0, min(100, self.score))
        grade, grade_label, grade_color = self._calculate_grade()

        return AuditResult(
            profile=self.profile,
            score=self.score,
            grade=grade,
            grade_label=grade_label,
            grade_color=grade_color,
            issues=sorted(self.issues, key=lambda i: i.points_deducted, reverse=True),
        )

    def _add_issue(self, issue_type: IssueType, severity: Severity,
                   title: str, description: str, points: int):
        self.score -= points
        self.issues.append(AuditIssue(
            issue_type=issue_type,
            severity=severity,
            title=title,
            description=description,
            recommendation=RECOMMENDATIONS[issue_type],
            points_deducted=points,
        ))

    def _check_website(self):
        if not self.profile.website:
            self._add_issue(
                IssueType.MISSING_WEBSITE, Severity.CRITICAL,
                "No Website Listed",
                "Your business profile does not have a website URL. "
                "This is one of the most important fields for credibility and traffic.",
                15
            )

    def _check_rating(self):
        rating = self.profile.rating
        if rating is None:
            return  # Can't assess without data

        if rating < 3.0:
            self._add_issue(
                IssueType.LOW_RATING, Severity.CRITICAL,
                f"Very Low Rating ({rating}/5.0)",
                f"Your rating of {rating} stars is significantly below average. "
                "Most customers filter for 4+ star businesses.",
                20
            )
        elif rating < 4.0:
            deduction = int(10 + (4.0 - rating) * 10)  # 10-20 points
            self._add_issue(
                IssueType.LOW_RATING, Severity.CRITICAL,
                f"Low Rating ({rating}/5.0)",
                f"Your rating of {rating} stars is below the 4.0 threshold. "
                "Businesses below 4 stars lose significant potential customers.",
                min(deduction, 20)
            )
        elif rating < THRESHOLDS['min_rating_excellent']:
            self._add_issue(
                IssueType.MODERATE_RATING, Severity.WARNING,
                f"Rating Could Be Higher ({rating}/5.0)",
                f"Your rating of {rating} is decent but not exceptional. "
                "Top-performing businesses maintain 4.5+ stars.",
                5
            )

    def _check_reviews(self):
        count = self.profile.review_count
        if count is None or count == 0:
            self._add_issue(
                IssueType.NO_REVIEWS, Severity.CRITICAL,
                "No Reviews",
                "Your profile has zero reviews. Reviews are the #1 factor "
                "customers consider when choosing a business.",
                15
            )
        elif count < THRESHOLDS['min_reviews_ok']:
            self._add_issue(
                IssueType.FEW_REVIEWS, Severity.WARNING,
                f"Very Few Reviews ({count})",
                f"Only {count} reviews. Businesses with fewer than 10 reviews "
                "appear less trustworthy to potential customers.",
                10
            )
        elif count < THRESHOLDS['min_reviews_good']:
            self._add_issue(
                IssueType.FEW_REVIEWS, Severity.WARNING,
                f"Few Reviews ({count})",
                f"You have {count} reviews. While decent, aim for 25+ reviews "
                "to build stronger social proof.",
                7
            )
        elif count < THRESHOLDS['min_reviews_excellent']:
            self._add_issue(
                IssueType.FEW_REVIEWS, Severity.INFO,
                f"Reviews Could Be Higher ({count})",
                f"You have {count} reviews. Getting to 50+ reviews will "
                "significantly boost your search visibility.",
                5
            )

    def _check_photos(self):
        count = self.profile.photos_count
        if count is None or count == 0:
            self._add_issue(
                IssueType.NO_PHOTOS, Severity.CRITICAL,
                "No Photos",
                "Your profile has no photos. Profiles without photos get "
                "significantly less engagement and clicks.",
                10
            )
        elif count < THRESHOLDS['min_photos_good']:
            self._add_issue(
                IssueType.FEW_PHOTOS, Severity.WARNING,
                f"Very Few Photos ({count})",
                f"Only {count} photos. Visual content is crucial for "
                "attracting customers. Aim for at least 10 photos.",
                7
            )
        elif count < THRESHOLDS['min_photos_excellent']:
            self._add_issue(
                IssueType.FEW_PHOTOS, Severity.INFO,
                f"Could Use More Photos ({count})",
                f"You have {count} photos. Adding more variety will make "
                "your profile more engaging and informative.",
                3
            )

    def _check_hours(self):
        hours = self.profile.hours
        if not hours:
            self._add_issue(
                IssueType.NO_HOURS, Severity.CRITICAL,
                "No Business Hours Listed",
                "Business hours are not available on your profile. "
                "Customers need to know when you're open before visiting.",
                10
            )
        elif len(hours) < THRESHOLDS['expected_hours_days']:
            self._add_issue(
                IssueType.INCOMPLETE_HOURS, Severity.WARNING,
                f"Incomplete Business Hours ({len(hours)}/7 days)",
                f"Only {len(hours)} out of 7 days have hours listed. "
                "Complete your schedule for all days of the week.",
                5
            )

    def _check_description(self):
        if not self.profile.description:
            self._add_issue(
                IssueType.MISSING_DESCRIPTION, Severity.WARNING,
                "No Business Description",
                "Your profile is missing a description. This is a missed opportunity "
                "to tell potential customers what makes your business special.",
                8
            )

    def _check_owner_responses(self):
        ratio = self.profile.owner_response_ratio
        if ratio is None:
            return  # Can't assess

        if ratio == 0:
            self._add_issue(
                IssueType.NO_OWNER_RESPONSES, Severity.WARNING,
                "No Owner Responses to Reviews",
                "You haven't responded to any customer reviews. "
                "Responding shows you value feedback and care about customers.",
                7
            )
        elif ratio < THRESHOLDS['min_owner_response_rate']:
            pct = int(ratio * 100)
            self._add_issue(
                IssueType.LOW_OWNER_RESPONSES, Severity.INFO,
                f"Low Response Rate ({pct}%)",
                f"You've only responded to {pct}% of reviews. "
                "Aim to respond to at least 50% of all reviews.",
                4
            )

    def _check_phone(self):
        if not self.profile.phone:
            self._add_issue(
                IssueType.MISSING_PHONE, Severity.WARNING,
                "No Phone Number",
                "Your profile doesn't have a phone number. "
                "Many customers prefer to call before visiting.",
                5
            )

    def _check_category(self):
        if not self.profile.category:
            self._add_issue(
                IssueType.MISSING_CATEGORY, Severity.WARNING,
                "No Business Category",
                "Your business category is not visible. "
                "The category determines which searches your business appears in.",
                5
            )

    def _calculate_grade(self) -> tuple[str, str, str]:
        for letter in ['A', 'B', 'C', 'D', 'F']:
            grade_info = GRADES[letter]
            if self.score >= grade_info['min']:
                return letter, grade_info['label'], grade_info['color']
        return 'F', GRADES['F']['label'], GRADES['F']['color']
