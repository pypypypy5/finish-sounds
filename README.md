# Codex Finish Sound Hook

Codex 작업 완료 시 소리를 재생하는 훅 설정 문서입니다.

## 음원 위치

- 음원 파일(`.mp3`, `.wav`)은 `finish-sounds/sounds/` 폴더에 둡니다.

## 문서

- 전체 설치/검증/장애 대응: `SETUP.md`

## 빠른 시작

1. `config.toml`에 전역 `notify` 설정:

```toml
notify = ["python3", "/mnt/c/Users/shj/.codex/finish-sounds/main.py"]
```

2. self-test:

```bash
FINISH_SOUNDS_DEBUG=1 python3 /mnt/c/Users/shj/.codex/finish-sounds/main.py --self-test
tail -n 50 /mnt/c/Users/shj/.codex/finish-sounds/hook.log
```

3. Codex 재시작 후 실제 작업 1회 실행

문제가 있으면 `SETUP.md`의 "실제 에이전트 종료 시 무음일 때 점검 순서"부터 확인하세요.
