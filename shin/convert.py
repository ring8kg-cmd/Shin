"""ffmpeg로 오디오를 Whisper에 최적인 16kHz 모노 wav로 변환한다."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class FFmpegNotFoundError(RuntimeError):
    """ffmpeg 실행 파일을 찾을 수 없을 때."""


def ensure_ffmpeg() -> str:
    """ffmpeg 경로를 반환하거나, 없으면 안내와 함께 예외를 던진다."""
    path = shutil.which("ffmpeg")
    if not path:
        raise FFmpegNotFoundError(
            "ffmpeg를 찾을 수 없습니다. 설치 후 다시 시도하세요.\n"
            "  Ubuntu/Debian: sudo apt-get install -y ffmpeg\n"
            "  macOS:         brew install ffmpeg"
        )
    return path


def to_wav(
    src: str | Path,
    dst: str | Path | None = None,
    *,
    sample_rate: int = 16_000,
    overwrite: bool = True,
) -> Path:
    """`src` 오디오를 16kHz 모노 PCM wav로 변환해 `dst` 경로를 반환한다.

    `dst`를 생략하면 `src`와 같은 위치에 `.wav` 확장자로 만든다.
    """
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(f"입력 오디오를 찾을 수 없습니다: {src}")

    dst = Path(dst) if dst is not None else src.with_suffix(".wav")
    dst.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = ensure_ffmpeg()
    cmd = [
        ffmpeg,
        "-y" if overwrite else "-n",
        "-i", str(src),
        "-ac", "1",            # 모노
        "-ar", str(sample_rate),  # 샘플레이트
        "-vn",                 # 비디오 트랙 제거
        "-c:a", "pcm_s16le",   # 16-bit PCM
        str(dst),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 변환 실패 (코드 {proc.returncode}):\n{proc.stderr.strip()}"
        )
    return dst
