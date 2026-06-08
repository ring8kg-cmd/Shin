"""시간대별 자막(SRT / 타임스탬프 TXT) 생성."""

from __future__ import annotations

from .transcribe import Transcript


def _srt_timestamp(seconds: float) -> str:
    """초를 SRT 타임코드(HH:MM:SS,mmm)로 변환한다."""
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _clock(seconds: float) -> str:
    """초를 [HH:MM:SS] 형태로 변환한다."""
    if seconds < 0:
        seconds = 0.0
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def to_srt(transcript: Transcript) -> str:
    """SRT 형식 자막 문자열을 만든다."""
    blocks: list[str] = []
    for seg in transcript.segments:
        blocks.append(
            f"{seg.index}\n"
            f"{_srt_timestamp(seg.start)} --> {_srt_timestamp(seg.end)}\n"
            f"{seg.text}\n"
        )
    return "\n".join(blocks)


def to_timestamped_txt(transcript: Transcript) -> str:
    """[HH:MM:SS] 텍스트 형태의 타임스탬프 자막 문자열을 만든다."""
    lines = [
        f"[{_clock(seg.start)} - {_clock(seg.end)}] {seg.text}"
        for seg in transcript.segments
    ]
    return "\n".join(lines)
