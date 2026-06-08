"""faster-whisper를 사용한 한국어 음성 전사."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class Segment:
    """전사된 한 구간."""

    index: int
    start: float  # 초
    end: float    # 초
    text: str


@dataclass
class Transcript:
    """전체 전사 결과."""

    language: str
    duration: float
    segments: list[Segment] = field(default_factory=list)

    @property
    def text(self) -> str:
        """구간 텍스트를 줄바꿈으로 이어붙인 전체 본문."""
        return "\n".join(s.text for s in self.segments)


def transcribe(
    wav_path: str | Path,
    *,
    model_size: str = "small",
    language: str = "ko",
    device: str = "auto",
    compute_type: str = "auto",
    beam_size: int = 5,
    vad_filter: bool = True,
    progress: Callable[[Segment], None] | None = None,
) -> Transcript:
    """`wav_path`를 전사해 `Transcript`를 반환한다.

    model_size: tiny/base/small/medium/large-v3 등. 클수록 정확하지만 느리다.
    progress: 각 구간이 나올 때마다 호출되는 콜백(선택). 진행 표시에 사용.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "faster-whisper가 설치되어 있지 않습니다. `pip install faster-whisper`로 설치하세요."
        ) from exc

    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"wav 파일을 찾을 수 없습니다: {wav_path}")

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    raw_segments, info = model.transcribe(
        str(wav_path),
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
    )

    segments: list[Segment] = []
    for i, seg in enumerate(raw_segments):
        s = Segment(
            index=i + 1,
            start=float(seg.start),
            end=float(seg.end),
            text=seg.text.strip(),
        )
        segments.append(s)
        if progress is not None:
            progress(s)

    return Transcript(
        language=info.language,
        duration=float(info.duration),
        segments=segments,
    )
