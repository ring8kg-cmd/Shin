#!/usr/bin/env python3
"""Shin — 한국어 음성 전사 파이프라인 (CLI).

사용 예:
    python transcribe.py 회의.m4a
    python transcribe.py 통화.m4a --model medium --outdir 결과 --no-mask

수행 단계:
    1) ffmpeg로 16kHz 모노 wav 변환
    2) faster-whisper로 한국어 전사
    3) 시간대별 자막 생성 (.srt / .txt)
    4) 전체 요약·핵심 쟁점·할 일 목록 작성 (summary.md)
    5) 개인정보·전화번호 마스킹 (별도 *.masked.* 산출)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from shin import convert, subtitle, summarize
from shin.masking import mask
from shin.transcribe import Segment, transcribe


def _fmt_clock(seconds: float) -> str:
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _build_summary_md(s: summarize.Summary) -> str:
    lines = ["# 요약 보고서", "", f"_생성 엔진: {s.engine}_", "", "## 전체 요약", "", s.summary or "_(내용 없음)_", "", "## 핵심 쟁점"]
    lines += [f"- {p}" for p in s.key_points] or ["- _(추출된 쟁점 없음)_"]
    lines += ["", "## 해야 할 일"]
    lines += [f"- [ ] {t}" for t in s.todos] or ["- _(추출된 할 일 없음)_"]
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    src = Path(args.audio)
    if not src.exists():
        print(f"오류: 입력 파일을 찾을 수 없습니다: {src}", file=sys.stderr)
        return 2

    outdir = Path(args.outdir) if args.outdir else src.parent
    outdir.mkdir(parents=True, exist_ok=True)
    stem = src.stem

    # 1) wav 변환
    print(f"[1/5] ffmpeg로 wav 변환 중: {src.name}")
    try:
        wav = convert.to_wav(src, outdir / f"{stem}.wav")
    except (convert.FFmpegNotFoundError, RuntimeError, FileNotFoundError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    # 2) 전사
    print(f"[2/5] faster-whisper 전사 중 (model={args.model}, lang={args.language})…")

    def _progress(seg: Segment) -> None:
        print(f"    [{_fmt_clock(seg.start)}] {seg.text}")

    try:
        transcript = transcribe(
            wav,
            model_size=args.model,
            language=args.language,
            progress=_progress if args.verbose else None,
        )
    except (ImportError, FileNotFoundError, RuntimeError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1
    print(f"    완료: {len(transcript.segments)}개 구간, "
          f"길이 {_fmt_clock(transcript.duration)}, 언어={transcript.language}")

    # 3) 자막 생성
    print("[3/5] 자막(SRT/TXT) 생성 중…")
    srt_text = subtitle.to_srt(transcript)
    txt_text = subtitle.to_timestamped_txt(transcript)
    (outdir / f"{stem}.srt").write_text(srt_text, encoding="utf-8")
    (outdir / f"{stem}.txt").write_text(txt_text, encoding="utf-8")

    # 4) 요약
    print("[4/5] 요약·핵심 쟁점·할 일 작성 중…")
    summ = summarize.summarize(transcript.text)
    (outdir / f"{stem}.summary.md").write_text(_build_summary_md(summ), encoding="utf-8")

    # 5) 마스킹
    written = [f"{stem}.wav", f"{stem}.srt", f"{stem}.txt", f"{stem}.summary.md"]
    if not args.no_mask:
        print("[5/5] 개인정보·전화번호 마스킹 중…")
        srt_rep = mask(srt_text)
        txt_rep = mask(txt_text)
        sum_rep = mask(_build_summary_md(summ))
        (outdir / f"{stem}.masked.srt").write_text(srt_rep.text, encoding="utf-8")
        (outdir / f"{stem}.masked.txt").write_text(txt_rep.text, encoding="utf-8")
        (outdir / f"{stem}.summary.masked.md").write_text(sum_rep.text, encoding="utf-8")
        written += [f"{stem}.masked.srt", f"{stem}.masked.txt", f"{stem}.summary.masked.md"]
        total = srt_rep.total + txt_rep.total + sum_rep.total
        detail = ", ".join(f"{k}:{v}" for k, v in srt_rep.counts.items()) or "없음"
        print(f"    마스킹된 항목 {total}건 (본문 기준 {detail})")
    else:
        print("[5/5] 마스킹 건너뜀 (--no-mask)")

    print("\n완료. 생성된 파일:")
    for name in written:
        print(f"  - {outdir / name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="한국어 음성 전사 파이프라인 (m4a→wav→전사→자막→요약→마스킹)",
    )
    p.add_argument("audio", help="입력 오디오 파일 (m4a, mp3, wav 등)")
    p.add_argument("-o", "--outdir", help="출력 디렉터리 (기본: 입력 파일과 같은 위치)")
    p.add_argument("-m", "--model", default="small",
                   help="Whisper 모델 크기 (tiny/base/small/medium/large-v3, 기본: small)")
    p.add_argument("-l", "--language", default="ko", help="전사 언어 (기본: ko)")
    p.add_argument("--no-mask", action="store_true", help="개인정보 마스킹 단계를 건너뜀")
    p.add_argument("-v", "--verbose", action="store_true", help="전사 진행을 구간별로 출력")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
