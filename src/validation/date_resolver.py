import re
from datetime import datetime

EFFECTIVE_DATE = datetime(
    2026,
    3,
    1,
)

class DateResolver:
    DATE_PATTERNS = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        (
            r"\b(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{1,2},?\s+\d{4}\b"
        ),
        (
            r"\b\d{1,2}\s+(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{4}\b"
        ),
    ]

    def parse_date(self, value):
        value = value.strip()
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%B %d %Y",
            "%B %d, %Y",
            "%d %B %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(
                    value,
                    fmt,
                )
            except ValueError:
                continue
        return None

    def extract_dates(self, text):
        found = []
        for pattern in self.DATE_PATTERNS:
            for match in re.finditer(
                pattern,
                text,
                re.IGNORECASE,
            ):
                parsed = self.parse_date(
                    match.group()
                )
                if parsed:
                    found.append(
                        (
                            parsed,
                            match.start(),
                        )
                    )
        found.sort(
            key=lambda item: item[1]
        )
        result = []
        seen = set()

        for date, position in found:
            key = date.strftime(
                "%Y-%m-%d"
            )
            if key not in seen:
                seen.add(key)
                result.append(
                    date
                )
        return result

    def get_date_type(self, query):
        text = query.lower()
        reporting_words = [
            "report",
            "reporting",
            "deadline",
            "notify",
            "notification",
            "change of circumstances",
            "change that occurred",
            "reporting period",
        ]

        if any(
            word in text
            for word in reporting_words
        ):
            return "change_date"
        determination_words = [
            "determination",
            "earnings disregard",
            "income threshold",
            "threshold",
            "sanction",
        ]

        if any(
            word in text
            for word in determination_words
        ):
            return "determination_date"
        return None

    def resolve(self, query):
        date_type = self.get_date_type(
            query
        )
        dates = self.extract_dates(
            query
        )

        if date_type is None:
            return {
                "needed": False,
                "date": None,
                "date_type": None,
                "version": None,
                "change_date": None,
                "change_version": None,
                "determination_date": None,
                "determination_version": None,
            }

        if not dates:
            return {
                "needed": True,
                "date": None,
                "date_type": date_type,
                "version": None,

                "change_date": None,
                "change_version": None,

                "determination_date": None,
                "determination_version": None,
            }
        change_date = None
        determination_date = None
        text = query

        change_match = re.search(
            r"change(?:\s+of\s+circumstances)?"
            r"(?:\s+that)?\s+occurred\s+(?:on\s+)?"
            r"("
            r"\d{4}-\d{2}-\d{2}"
            r"|"
            r"\d{1,2}/\d{1,2}/\d{4}"
            r"|"
            r"(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{1,2},?\s+\d{4}"
            r"|"
            r"\d{1,2}\s+(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{4}"
            r")",
            text,
            re.IGNORECASE,
        )

        if change_match:
            change_date = self.parse_date(
                change_match.group(1)
            )
        determination_match = re.search(
            r"determination\s+(?:was\s+)?made\s+(?:on\s+)?"
            r"("
            r"\d{4}-\d{2}-\d{2}"
            r"|"
            r"\d{1,2}/\d{1,2}/\d{4}"
            r"|"
            r"(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{1,2},?\s+\d{4}"
            r"|"
            r"\d{1,2}\s+(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{4}"
            r")",
            text,
            re.IGNORECASE,
        )

        if determination_match:
            determination_date = self.parse_date(
                determination_match.group(1)
            )

        if date_type == "change_date":
            if change_date is None:
                if len(dates) == 1:
                    change_date = dates[0]
                elif len(dates) >= 2:
                    change_date = dates[-1]

        elif date_type == "determination_date":
            if determination_date is None:
                if len(dates) == 1:
                    determination_date = dates[0]
                elif len(dates) >= 2:
                    determination_date = dates[0]

        change_version = None
        if change_date:
            change_version = (
                "original"
                if change_date < EFFECTIVE_DATE
                else "amended"
            )
        determination_version = None
        if determination_date:
            determination_version = (
                "original"
                if determination_date < EFFECTIVE_DATE
                else "amended"
            )

        if date_type == "change_date":
            primary_date = change_date
            primary_version = change_version
        else:
            primary_date = determination_date
            primary_version = determination_version

        return {
            "needed": primary_date is None,
            "date": primary_date,
            "date_type": date_type,
            "version": primary_version,
            "change_date": change_date,
            "change_version": change_version,
            "determination_date": determination_date,
            "determination_version": determination_version,
        }