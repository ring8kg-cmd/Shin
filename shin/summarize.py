"""전사 본문으로부터 전체 요약·핵심 쟁점·할 일 목록 생성.

ANTHROPIC_API_KEY가 설정돼 있으면 Claude(claude-opus-4-8)로 고품질 요약을
생성하고, 없으면 의존성 없이 동작하는 추출 기반(extractive) 폴백을 사용한다.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

MODEL = "claude-opus-4-8"

_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
        "todos": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "key_points", "todos"],
    "additionalProperties": False,
}

_SYSTEM = (
    "당신은 한국어 회의/통화 녹취를 분석하는 비서입니다. "
    "전사 텍스트를 읽고 (1) 전체 요약, (2) 핵심 쟁점 목록, (3) 해야 할 일(액션 아이템) "
    "목록을 한국어로 작성하세요. 사실에 근거하고 추측은 피하며, 액션 아이템은 가능하면 "
    "담당/기한 단서를 포함해 동사형으로 적으세요."
)


@dataclass
class Summary:
    summary: str
    key_points: list[str] = field(default_factory=list)
    todos: list[str] = field(default_factory=list)
    engine: str = "extractive"  # "claude" 또는 "extractive"


def summarize(text: str) -> Summary:
    """API 키가 있으면 Claude로, 없으면 추출 방식으로 요약한다."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _summarize_with_claude(text)
        except Exception as exc:  # API 실패 시 폴백
            print(f"[요약] Claude 호출 실패 → 추출 방식으로 대체합니다: {exc}")
    return _summarize_extractive(text)


def _summarize_with_claude(text: str) -> Summary:
    import anthropic

    client = anthropic.Anthropic()
    prompt = (
        "다음은 음성 전사 본문입니다. 분석해 주세요.\n\n"
        "----- 전사 시작 -----\n"
        f"{text}\n"
        "----- 전사 끝 -----"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=_SYSTEM,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    raw = next((b.text for b in response.content if b.type == "text"), "")
    data = json.loads(raw)
    return Summary(
        summary=data.get("summary", "").strip(),
        key_points=[p.strip() for p in data.get("key_points", []) if p.strip()],
        todos=[t.strip() for t in data.get("todos", []) if t.strip()],
        engine="claude",
    )


# --- 폴백: 의존성 없는 추출 요약 -----------------------------------------

_TODO_HINTS = (
    "해야", "하기로", "하겠", "할 것", "할게", "합시다", "하자", "필요",
    "준비", "확인", "검토", "처리", "전달", "공유", "보내", "마감", "기한",
    "예정", "계획", "요청", "팔로업", "follow", "todo", "to-do", "액션",
)
_ISSUE_HINTS = (
    "문제", "이슈", "쟁점", "우려", "리스크", "위험", "논의", "결정",
    "합의", "반대", "이견", "지연", "지적", "병목",
)


def _split_sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?。…])\s+|\n+", flat)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def _summarize_extractive(text: str) -> Summary:
    sentences = _split_sentences(text)

    summary = " ".join(sentences[:3]) if sentences else ""
    if len(summary) > 500:
        summary = summary[:500].rstrip() + "…"

    key_points: list[str] = []
    todos: list[str] = []
    for s in sentences:
        if any(h in s for h in _TODO_HINTS) and s not in todos:
            todos.append(s)
        if any(h in s for h in _ISSUE_HINTS) and s not in key_points:
            key_points.append(s)

    # 쟁점 단서가 없으면 가장 긴 문장 몇 개를 핵심으로 추린다.
    if not key_points and sentences:
        key_points = sorted(sentences, key=len, reverse=True)[:5]

    return Summary(
        summary=summary,
        key_points=key_points[:10],
        todos=todos[:10],
        engine="extractive",
    )
