# finish-sounds Hook Setup & Troubleshooting

이 문서는 Codex 작업 완료 시 소리를 재생하는 `finish-sounds` 훅을 재현 가능하게 설정하는 방법과, 실제로 겪었던 장애/해결 과정을 정리합니다.

## 1) 디렉터리 구조

기준 경로: `/mnt/c/Users/shj/.codex`

```text
.codex/
  config.toml
  finish-sounds/
    main.py
    sounds/
      *.mp3 or *.wav
    hook.log
```

## 2) 핵심 설정

`notify`는 **전역(top-level)** 키로 넣어야 합니다.  
또한 상대경로 대신 **절대경로**를 권장합니다.

예시 (`config.toml`):

```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "low"
personality = "pragmatic"
notify = ["python3", "/mnt/c/Users/shj/.codex/finish-sounds/main.py"]
```

주의:
- `notify`를 `[mcp.servers.filesystem]` 같은 테이블 내부에 넣으면 훅이 동작하지 않습니다.

## 3) 어떤 config.toml을 수정해야 하는가

WSL에서는 보통 Codex가 `HOME` 기준 설정을 읽습니다.

- WSL 홈 설정: `/home/pypypy918/.codex/config.toml`
- Windows 경로 설정: `/mnt/c/Users/shj/.codex/config.toml` (`C:\Users\shj\.codex`)

아래로 현재 기준을 확인합니다:

```bash
echo $HOME
ls -l $HOME/.codex/config.toml
```

실사용 설정 파일에도 반드시 `notify`를 넣어야 합니다.

## 4) 훅 스크립트 동작 확인

self-test:

```bash
FINISH_SOUNDS_DEBUG=1 python3 /mnt/c/Users/shj/.codex/finish-sounds/main.py --self-test
```

로그 확인:

```bash
tail -n 50 /mnt/c/Users/shj/.codex/finish-sounds/hook.log
```

정상 로그 예:
- `invoked (self_test=True)`
- `selected file: ...`
- `available players: paplay, ffplay, ...`
- `playback success`

## 5) 실제 에이전트 종료 시 무음일 때 점검 순서

1. `hook.log` 타임스탬프가 갱신되는지 확인
2. 갱신되지 않으면 `notify` 미호출(설정 파일/위치 문제)
3. 갱신되는데 소리가 없으면 플레이어 실패(오디오 환경 문제)

## 6) 실제로 발생했던 장애와 원인

### 증상 A: self-test는 성공, 에이전트 종료 시는 무음
- 원인: `notify`가 잘못된 config 파일에 있거나, 테이블 내부에 들어가 전역 적용이 안 됨.
- 해결:
  - 실사용 config(`/home/pypypy918/.codex/config.toml`)에 전역 `notify` 추가
  - `notify` 경로를 절대경로로 변경

### 증상 B: `paplay` 관련 에러 / 소리 안 남
- 원인: 플레이어 부재 또는 오디오 백엔드 문제.
- 확인:
  - `which paplay`
  - `which ffplay`
  - `which aplay`
- 참고:
  - `aplay`는 주로 WAV에 적합, MP3는 `ffplay`/`paplay`가 안정적.

### 증상 C: WSL에서 `powershell.exe` 호출 실패
- 오류 예: `UtilBindVsockAnyPort ... socket failed 1`
- 원인: WSL↔Windows 인터롭/환경 이슈
- 대응: WSL 내부 플레이어(`paplay`/`ffplay`) 우선 사용

## 7) 재현 가능한 최종 체크리스트

1. `finish-sounds/main.py` 존재 및 실행 가능
2. `finish-sounds/sounds` 안에 `mp3` 또는 `wav` 파일 존재
3. 실사용 config(`$HOME/.codex/config.toml`)에 전역 `notify` 존재
4. `notify`는 절대경로 사용
5. self-test 성공
6. Codex 재시작 후 실제 작업 1회 수행
7. `hook.log`에 새 `invoked (...)` 로그 생성 확인

## 8) 운영 팁

- 설정 변경 후 Codex를 재시작해야 반영되는 경우가 많습니다.
- 문제 발생 시 `FINISH_SOUNDS_DEBUG=1`로 먼저 원인을 노출하세요.
- 로그 파일: `/mnt/c/Users/shj/.codex/finish-sounds/hook.log`
