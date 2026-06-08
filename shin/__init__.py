"""Shin — 한국어 음성 전사 파이프라인.

m4a(또는 임의 오디오) → wav 변환 → faster-whisper 전사 →
시간대별 자막(SRT/TXT) → 요약·핵심쟁점·할일 → 개인정보 마스킹.
"""

__version__ = "0.1.0"
