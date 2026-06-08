"""오디오 없이 검증 가능한 순수 로직 테스트 (pytest 없이도 실행 가능)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shin import subtitle, summarize
from shin.masking import mask
from shin.transcribe import Segment, Transcript


def _sample_transcript() -> Transcript:
    return Transcript(
        language="ko",
        duration=12.0,
        segments=[
            Segment(1, 0.0, 3.5, "안녕하세요 회의를 시작하겠습니다."),
            Segment(2, 3.5, 8.0, "제 번호는 010-1234-5678 이고 이메일은 hong@example.com 입니다."),
            Segment(3, 8.0, 12.0, "다음 주까지 보고서를 준비해서 공유하기로 했습니다."),
        ],
    )


def test_srt_format():
    t = _sample_transcript()
    srt = subtitle.to_srt(t)
    assert "00:00:00,000 --> 00:00:03,500" in srt
    assert "1\n" in srt
    assert "안녕하세요" in srt


def test_timestamped_txt():
    t = _sample_transcript()
    txt = subtitle.to_timestamped_txt(t)
    assert "[00:00:00 - 00:00:04]" in txt  # 3.5초는 반올림되어 04
    assert txt.count("\n") == 2  # 3줄


def test_mask_phone_and_email():
    rep = mask("연락처 010-1234-5678, 메일 hong@example.com")
    assert "010-1234-5678" not in rep.text
    assert "010-****-****" in rep.text
    assert "hong@example.com" not in rep.text
    assert "@example.com" in rep.text
    assert rep.counts.get("PHONE") == 1
    assert rep.counts.get("EMAIL") == 1


def test_mask_rrn_and_card():
    rep = mask("주민번호 900101-1234567 카드 1234-5678-9012-3456")
    assert "900101-1234567" not in rep.text
    assert "1234-5678-9012-3456" not in rep.text
    assert rep.counts.get("RRN") == 1
    assert rep.counts.get("CARD") == 1


def test_extractive_summary():
    t = _sample_transcript()
    summ = summarize._summarize_extractive(t.text)
    assert summ.engine == "extractive"
    assert summ.summary
    # "준비/공유/하기로" 단서가 있는 문장이 할 일로 잡혀야 한다.
    assert any("보고서" in todo for todo in summ.todos)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {fn.__name__}: {exc!r}")
    print(f"\n{len(fns) - failed}/{len(fns)} 통과")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
