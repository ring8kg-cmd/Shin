# Shin — 한국어 음성 전사 파이프라인

m4a(또는 임의 오디오) 파일을 넣으면 다음 5단계를 한 번에 수행합니다.

1. **ffmpeg**로 16kHz 모노 wav 변환
2. **faster-whisper**로 한국어 전사
3. 시간대별 **자막 생성** — `.srt`(SubRip) 및 타임스탬프 `.txt`
4. **전체 요약 · 핵심 쟁점 · 해야 할 일** 목록 작성 (`*.summary.md`)
5. **개인정보·전화번호 마스킹** — 마스킹본 별도 산출 (`*.masked.*`)

## 설치

```bash
# 1) 시스템 의존성 ffmpeg
sudo apt-get install -y ffmpeg      # Ubuntu/Debian
# brew install ffmpeg               # macOS

# 2) 파이썬 패키지
pip install -r requirements.txt
```

> **모델 다운로드 안내**: faster-whisper는 첫 실행 시 Whisper 모델을 Hugging Face에서
> 내려받습니다. 폐쇄망/제한된 네트워크에서는 huggingface.co 접근이 막혀 실패할 수
> 있습니다. 그런 환경에서는 모델을 미리 받아 두고 환경변수로 캐시 위치를 지정하세요:
>
> ```bash
> export HF_HUB_OFFLINE=1
> export HF_HOME=/path/to/preloaded/cache
> ```

## 사용법

```bash
# 기본 (입력 파일과 같은 위치에 결과 생성, small 모델, 마스킹 포함)
python transcribe.py 회의.m4a

# 모델·출력 디렉터리 지정, 진행 상황 표시
python transcribe.py 통화.m4a --model medium --outdir 결과 --verbose

# 마스킹 생략
python transcribe.py 인터뷰.m4a --no-mask
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `audio` | 입력 오디오 (m4a/mp3/wav 등) | (필수) |
| `-o, --outdir` | 출력 디렉터리 | 입력 파일과 같은 위치 |
| `-m, --model` | Whisper 모델 (`tiny`/`base`/`small`/`medium`/`large-v3`) | `small` |
| `-l, --language` | 전사 언어 | `ko` |
| `--no-mask` | 마스킹 단계 건너뜀 | off |
| `-v, --verbose` | 전사 진행을 구간별 출력 | off |

모델이 클수록 정확도는 높지만 느립니다. 회의/통화 한국어는 `small`~`medium`을 권장합니다.

## 산출물

입력이 `회의.m4a`일 때:

| 파일 | 내용 |
|------|------|
| `회의.wav` | 변환된 16kHz 모노 wav |
| `회의.srt` | 시간대별 SRT 자막 |
| `회의.txt` | `[HH:MM:SS - HH:MM:SS] 텍스트` 형식 자막 |
| `회의.summary.md` | 전체 요약 · 핵심 쟁점 · 할 일 목록 |
| `회의.masked.srt` / `.masked.txt` | 개인정보 마스킹본 |
| `회의.summary.masked.md` | 요약 마스킹본 |

## 요약 엔진 (4단계)

- `ANTHROPIC_API_KEY`가 설정돼 있으면 **Claude(`claude-opus-4-8`)** 로 고품질 요약을
  생성합니다(구조화 출력 사용).
  ```bash
  export ANTHROPIC_API_KEY=sk-ant-...
  ```
- 키가 없거나 호출이 실패하면, 의존성 없는 **추출 기반(extractive) 폴백**으로
  전환됩니다. 핵심 문장과 액션 단서("준비", "확인", "공유", "기한" 등)를 골라냅니다.

## 마스킹 (5단계)

정규식으로 다음 PII 패턴을 탐지·치환합니다(원본은 그대로 두고 별도 마스킹본 생성).

| 종류 | 예시 → 치환 |
|------|-------------|
| 전화번호 | `010-1234-5678` → `010-****-****` |
| 주민등록번호 | `900101-1234567` → `900101-*******` |
| 신용카드 | `1234-5678-9012-3456` → `****-****-****-****` |
| 이메일 | `hong@example.com` → `h***@example.com` |
| 계좌번호(후보) | `123-456-789012` → `****-****-****` |

> 정규식 기반이라 100% 완벽하지는 않습니다. 민감 정보가 포함된 녹취는 마스킹본을
> 사람이 한 번 더 검토하세요. 패턴은 `shin/masking.py`에서 조정할 수 있습니다.

## 모듈 구조

```
shin/
├── convert.py     # ffmpeg 래퍼 (m4a→wav)
├── transcribe.py  # faster-whisper 전사 → Transcript/Segment
├── subtitle.py    # SRT / 타임스탬프 TXT 생성
├── summarize.py   # Claude 요약 + 추출 폴백
└── masking.py     # PII 정규식 마스킹
transcribe.py      # 5단계를 묶는 CLI 진입점
tests/test_pipeline.py  # 오디오 없이 검증 가능한 단위 테스트
```

## 테스트

```bash
python tests/test_pipeline.py     # 또는: pytest tests/
```
