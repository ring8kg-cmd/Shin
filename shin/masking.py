"""한국어 텍스트의 개인정보·전화번호 마스킹.

전화번호, 주민등록번호, 이메일, 신용카드번호, 계좌번호 등을 정규식으로
탐지해 식별 불가능한 형태로 치환한다. 정규식 기반이므로 완벽하지는 않지만,
가장 흔한 PII 패턴을 안전하게 가린다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MaskRule:
    name: str
    pattern: re.Pattern[str]
    repl: object  # str 또는 Callable


def _mask_phone(m: re.Match[str]) -> str:
    """전화번호 가운데·뒤를 가린다. 010-1234-5678 → 010-****-****."""
    digits = re.sub(r"\D", "", m.group(0))
    if len(digits) >= 9:
        return f"{digits[:3]}-****-****"
    return "***-****"


# 한국 휴대폰/지역번호: 010-1234-5678, 02-123-4567, 031.123.4567, 01012345678 등
_PHONE = re.compile(
    r"(?<!\d)"
    r"(0(?:1[016789]|2|[3-6][1-5]|70))"   # 국번
    r"[-.\s]?"
    r"(\d{3,4})"
    r"[-.\s]?"
    r"(\d{4})"
    r"(?!\d)"
)

# 주민등록번호: 900101-1234567
_RRN = re.compile(r"(?<!\d)(\d{6})[-\s]?([1-4]\d{6})(?!\d)")

# 이메일
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

# 신용카드: 1234-5678-9012-3456
_CARD = re.compile(r"(?<!\d)(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})(?!\d)")

# 계좌번호 후보: 10~14자리 연속 숫자 또는 하이픈 구분 (전화/카드/주민번호 제거 후 적용)
_ACCOUNT = re.compile(r"(?<!\d)(\d{2,6}[-\s]\d{2,6}[-\s]\d{2,6}(?:[-\s]\d{1,6})?)(?!\d)")


def _mask_email(m: re.Match[str]) -> str:
    local, _, domain = m.group(0).partition("@")
    head = local[0] if local else "*"
    return f"{head}***@{domain}"


# 적용 순서가 중요하다: 더 구체적인(자릿수 많은) 패턴을 먼저 가린다.
RULES: list[MaskRule] = [
    MaskRule("RRN", _RRN, r"\1-*******"),
    MaskRule("CARD", _CARD, r"****-****-****-****"),
    MaskRule("PHONE", _PHONE, _mask_phone),
    MaskRule("EMAIL", _EMAIL, _mask_email),
    MaskRule("ACCOUNT", _ACCOUNT, "****-****-****"),
]


@dataclass
class MaskReport:
    text: str
    counts: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def mask(text: str, *, rules: list[MaskRule] | None = None) -> MaskReport:
    """`text`에서 PII를 마스킹한 결과와 규칙별 적용 횟수를 반환한다."""
    rules = rules if rules is not None else RULES
    counts: dict[str, int] = {}
    out = text
    for rule in rules:
        out, n = rule.pattern.subn(rule.repl, out)
        if n:
            counts[rule.name] = counts.get(rule.name, 0) + n
    return MaskReport(text=out, counts=counts)
